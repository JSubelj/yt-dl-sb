import sqlite3
import os
import libs.classes as obj
import datetime
import config

# TODO: Status should be array!!!!
class Db:
    def __init__(self, db_name="yt_dl_sb.db", create_new=False):
        if create_new:
            if os.path.exists(db_name):
                os.unlink(db_name)
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        if create_new:
            self.create_tables()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    id: int
    video_id: str
    status: str
    downloaded_path: str
    sponsor_times: list

    def _create_videos(self):
        # creates tables associated to videos
        self.c.execute(
            '''create table if not exists videos(id integer primary key autoincrement, video_id text unique,status text,downloaded_path text, latest_sponsortime_at text);''')
        self.c.execute(
            '''create table if not exists sponsor_times(id integer primary key autoincrement, video_id text,  start real, stop real, votes integer)''')
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
        self.c.execute('''insert into videos (video_id, status, downloaded_path) values (?,?,?)''',
                       (vid.video_id, vid.status, vid.downloaded_path))

        if vid.sponsor_times:
            sponsor_times_tuple = [(st.video_id, st.start, st.stop, st.votes) for st in vid.sponsor_times]
            self.c.executemany('''insert into sponsor_times (video_id, start, stop, votes) values (?,?,?,?)''',
                               sponsor_times_tuple)
        self.conn.commit()

        return self.get_video(vid.video_id)

    def get_video(self, video_id: str):
        self.c.execute(
            f"SELECT id, video_id, status, downloaded_path,latest_sponsortime_at FROM videos WHERE videos.video_id=?;",
            (video_id,))
        res = self.c.fetchone()
        if res is None:
            return
        id, video_id, status, downloaded_path, latest_sponsortime = res
        self.c.execute(f"SELECT id, video_id, start, stop, votes FROM sponsor_times WHERE sponsor_times.video_id=?;",
                       (video_id,))
        res = self.c.fetchall()
        if res is None:
            return
        sponsor_times = [obj.SponsorTime(*st) for st in res]

        return obj.Video(id, video_id, status, downloaded_path, sponsor_times, latest_sponsortime)

    def update_video(self, vid: obj.Video):
        self.c.execute(f"update videos set status=?, downloaded_path=? where video_id=?",
                       (vid.status, vid.downloaded_path, vid.video_id))
        self.c.execute("delete from sponsor_times where video_id=?", (vid.video_id,))
        if vid.sponsor_times:
            sponsor_times_tuple = [(st.video_id, st.start, st.stop, st.votes) for st in vid.sponsor_times]
            self.c.executemany('''insert into sponsor_times (video_id, start, stop, votes) values (?,?,?,?)''',
                               sponsor_times_tuple)
        self.conn.commit()
        return self.get_video(video_id=vid.video_id)

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
                    print(vid.sponsor_times, vid_in_db.sponsor_times)
                new_vid = self.update_video(vid)

                return True, new_vid

        print("Tuki5")
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
    # v = db.create_video(
    #     obj.Video(None, "HeUietgDuVc", "FETCHED", None, [obj.SponsorTime(None, "123", "13", "12", 51), ], None))
    # print(db.get_video("fdsa"))
    # db.update_video(obj.Video(None, "123", "DONE", "bla", [obj.SponsorTime(None, "123", "13", "123", 51), ], None))
    # v.sponsor_times.append(obj.SponsorTime(None, "123", "13", "12", 51))
    # print(db.get_video("123"))
    # print(db.update_video_sponsortimes_if_new(v))
