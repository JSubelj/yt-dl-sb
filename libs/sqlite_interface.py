import sqlite3
import os
import libs.classes as obj
import datetime


class Db:
    def __init__(self, db_name="yt_dl_sb.db", create_new=True):
        if create_new:
            os.unlink(db_name)
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()

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
            '''create table if not exists videos(id integer primary key autoincrement, video_id text unique,status text,downloaded_path text);''')
        self.c.execute(
            '''create table if not exists sponsor_times(id integer primary key autoincrement, video_id text,  start text, stop text, votes integer)''')
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
        self.c.execute("update channels set last_fetched=? where channel_id=?",(str(datetime.datetime.now()),ch.channel_id))

    def get_channel(self, channel_id: str):
        self.c.execute(f"SELECT id, channel_id, channel_name, last_fetched FROM channels WHERE channels.channel_id=?;",
                       (channel_id,))
        id, channel_id, channel_name, last_fetched = self.c.fetchone()
        return obj.Channel(id, channel_id, channel_name, datetime.datetime.fromisoformat(last_fetched) if last_fetched else None)

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
        self.c.execute(f"SELECT id, video_id, status, downloaded_path FROM videos WHERE videos.video_id=?;", (video_id,))
        vid_tuple = self.c.fetchone()
        self.c.execute(f"SELECT id, video_id, start, stop, votes FROM sponsor_times WHERE sponsor_times.video_id=?;", (video_id,))
        sponsor_times = [obj.SponsorTime(*st) for st in self.c.fetchall()]

        return obj.Video(*vid_tuple, sponsor_times=sponsor_times)

    def update_video(self, vid: obj.Video):
        self.c.execute(f"update videos set status=?, downloaded_path=? where video_id=?",(vid.status, vid.downloaded_path, vid.video_id))
        self.c.execute("delete from sponsor_times where video_id=?", (vid.video_id,))
        if vid.sponsor_times:
            sponsor_times_tuple = [(st.video_id, st.start, st.stop, st.votes) for st in vid.sponsor_times]
            self.c.executemany('''insert into sponsor_times (video_id, start, stop, votes) values (?,?,?,?)''',
                               sponsor_times_tuple)

        self.conn.commit()


if __name__ == "__main__":
    db = Db()
    db.create_tables()
    db.create_channel(obj.Channel(None, "bla", "bla",None))
    print(db.get_channel("bla"))
    db.create_video(obj.Video(None, "123", "DOWNLOADING", None, [obj.SponsorTime(None, "123", "13", "12", 51), ]))
    db.update_video(obj.Video(None, "123", "DONE", "bla",[obj.SponsorTime(None, "123", "13", "123", 51),]))
    print(db.get_video("123"))
