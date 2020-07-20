import sqlite3
import os
import libs.classes as obj
import datetime
from libs import config
import re

def camel_to_snake(name):
  name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
  return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

def python_types_to_sql_types(type):
    if type == int:
        return "INTEGER"
    if type == float:
        return "REAL"
    if type == str:
        return "TEXT"

class Db:
    def __init__(self, db_name="yt_dl_sb.db", create_new=False):
        if create_new:
            if os.path.exists(db_name):
                os.unlink(db_name)
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()

        self.create_tables()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def _get_attributes_and_types(self, obj):
        att_and_types = []
        for att, props in obj.__dataclass_fields__.items():
            att_and_types.append((att, props.type))
        return att_and_types

    def get_not_done_videos(self):
        command = "select video_id from videos;"
        self.c.execute(command)
        return list(filter(lambda x: not self.is_video_done(x),[self.get_video(r[0]) for r in self.c.fetchall()]))


    def _create_primitive_table(self, obj):
        att_and_types = self._get_attributes_and_types(obj)
        att_and_types = list(filter(lambda x: x[0] != "id", att_and_types))

        command=f"create table if not exists {camel_to_snake(obj.__name__)}s (id integer primary key autoincrement, "
        for name,m_type in att_and_types:
            command += f"{name} {python_types_to_sql_types(m_type)}, "
        command = command[:-2]
        command+= ");"
        self.c.execute(command)
        self.conn.commit()

    def create_primitive(self,obj_sig,obj):
        att_and_types = self._get_attributes_and_types(obj_sig)
        att_and_types = list(filter(lambda x: x[0] != "id", att_and_types))

        command = f"insert into {camel_to_snake(obj_sig.__name__)}s ("
        attrs = []
        for name,m_type in att_and_types:
            command+=f"{name}, "
            attrs.append(getattr(obj,name))
        command = command[:-2]+") values ("
        for name,m_type in att_and_types:
            command+=f"?, "
        command = command[:-2] + ");"
        self.c.execute(command,attrs)
        self.conn.commit()
        obj.id = self.c.lastrowid
        return obj


        #(channel_id, channel_name) values (?,?)''', (ch.channel_id, ch.channel_name))"


    def _create_videos(self):
        # creates tables associated to videos
        self.c.execute(
            '''create table if not exists videos(id integer primary key autoincrement, video_id text unique,downloaded_path text, downloaded_path_subs text, latest_sponsortime_at text);''')
        self.c.execute(
            '''create table if not exists sponsor_times(id integer primary key autoincrement, video_id text,  start real, stop real, votes integer)''')
        self._create_primitive_table(obj.Status)
        self.conn.commit()

    def _create_channels(self):
        self.c.execute(
            '''create table if not exists channels(id integer primary key autoincrement, channel_id text unique,channel_name text, last_fetched text);''')
        self.conn.commit()

    def create_tables(self):
        self._create_videos()
        self._create_channels()

    def create_channel(self, ch: obj.Channel):
        self.c.execute(
            '''insert into channels (channel_id, channel_name) values (?,?)''', (ch.channel_id, ch.channel_name))
        self.conn.commit()
        ch.id = self.c.lastrowid
        return ch

    def update_last_fetched(self, ch: obj.Channel):
        # TODO: datetime to current timezone!
        self.c.execute("update channels set last_fetched=? where channel_id=?",
                       (str(datetime.datetime.now()), ch.channel_id))

    def get_channel(self, channel_id: str):
        self.c.execute(f"SELECT id, channel_id, channel_name, last_fetched FROM channels WHERE channels.channel_id=?;",
                       (channel_id,))
        id, channel_id, channel_name, last_fetched = self.c.fetchone()
        return obj.Channel(id, channel_id, channel_name,
                           datetime.datetime.fromisoformat(last_fetched) if last_fetched else None)

    def get_all_channels(self):
        self.c.execute("SELECT id, channel_id, channel_name, last_fetched FROM channels;")
        return [
            obj.Channel(id, channel_id, channel_name,
                        datetime.datetime.fromisoformat(last_fetched) if last_fetched else None) for
            id, channel_id, channel_name, last_fetched in self.c.fetchall()
        ]

    def create_video(self, vid: obj.Video):
        self.c.execute(
            '''insert into videos (video_id, downloaded_path, downloaded_path_subs) values (?,?,?)''',
            (vid.video_id, vid.downloaded_path, vid.downloaded_path_subs))

        if vid.sponsor_times:
            sponsor_times_tuple = [(st.video_id, st.start, st.stop, st.votes) for st in vid.sponsor_times]
            self.c.executemany('''insert into sponsor_times (video_id, start, stop, votes) values (?,?,?,?)''',
                               sponsor_times_tuple)
        self.conn.commit()

        return self.get_video(vid.video_id)

    def get_video(self, video_id: str):
        self.c.execute(
            f"SELECT id, video_id, downloaded_path, downloaded_path_subs, latest_sponsortime_at FROM videos WHERE videos.video_id=?;",
            (video_id,))
        res = self.c.fetchone()
        if res is None:
            return
        id, video_id, downloaded_path, downloaded_path_subs, latest_sponsortime = res
        self.c.execute(f"SELECT id, video_id, start, stop, votes FROM sponsor_times WHERE sponsor_times.video_id=?;",
                       (video_id,))
        res = self.c.fetchall()
        if res is None:
            return
        sponsor_times = [obj.SponsorTime(*st) for st in res]

        return obj.Video(id, video_id, downloaded_path, downloaded_path_subs, sponsor_times, latest_sponsortime)

    def update_video(self, vid: obj.Video):
        self.c.execute(f"update videos set downloaded_path=?, downloaded_path_subs=? where video_id=?",
                       (vid.downloaded_path, vid.downloaded_path_subs, vid.video_id))
        self.c.execute("delete from sponsor_times where video_id=?", (vid.video_id,))
        if vid.sponsor_times:
            sponsor_times_tuple = [(st.video_id, st.start, st.stop, st.votes) for st in vid.sponsor_times]
            self.c.executemany('''insert into sponsor_times (video_id, start, stop, votes) values (?,?,?,?)''',
                               sponsor_times_tuple)
        self.conn.commit()
        return self.get_video(video_id=vid.video_id)

    def is_video_done(self,v:obj.Video):
        self.c.execute("select keyword from statuss where video_id=?",(v.video_id,))
        for row in self.c.fetchall():
            if row[0] == obj.VidStatus.DONE:
                return True
        return False

    def update_video_sponsortimes_if_new(self, vid: obj.Video):
        from libs.sb_times_retrival import is_sponsor_time_same

        vid_in_db = self.get_video(vid.video_id)
        if vid_in_db.sponsor_times is None and vid.sponsor_times is None:
            return False, vid

        if vid_in_db.sponsor_times is None and vid.sponsor_times:
            new_vid = self.update_video(vid)
            return True, new_vid
        if vid_in_db.sponsor_times and vid.sponsor_times is None:
            new_vid = self.update_video(vid)
            return True, new_vid
        if len(vid_in_db.sponsor_times) != len(vid.sponsor_times):
            new_vid = self.update_video(vid)
            return True, new_vid

        for st in vid_in_db.sponsor_times:
            if not any([is_sponsor_time_same(st, new_st) for new_st in vid.sponsor_times]):
                if config.DEVELOPMENT:
                    #print(vid.sponsor_times, vid_in_db.sponsor_times)
                    [print((st.start,st.stop)) for st in vid.sponsor_times]
                    print("////")
                    [print((st.start, st.stop)) for st in vid_in_db.sponsor_times]
                new_vid = self.update_video(vid)

                return True, new_vid

        return False, vid

    def check_if_vid_exist_else_add(self, vid: obj.Video):
        if self.get_video(vid.video_id):
            return False, vid
        return True, self.create_video(vid)


if __name__ == "__main__":
    db = Db(create_new=True)

    # db.create_tables()
    # db.create_channel(obj.Channel(None, "bla", "bla", None))
    # print(db.get_channel("bla"))
    v = db.create_video(
        obj.Video(None, "HeUietgDuVc", None, None, [obj.SponsorTime(None, "123", "13", "12", 51), ], None))

    # print(db.get_video("fdsa"))
    db.update_video(
        obj.Video(None, "123", "bla", "bla", [obj.SponsorTime(None, "123", "13", "123", 51), ], None))
    # v.sponsor_times.append(obj.SponsorTime(None, "123", "13", "12", 51))
    # print(db.get_video("123"))
    # print(db.update_video_sponsortimes_if_new(v))
