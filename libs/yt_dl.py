from youtube_dl import YoutubeDL
import libs.classes as obj
from libs.sqlite_interface import Db
import time
import config
import os
import mimetypes
# import subprocess
from  datetime import datetime


class ytdl_logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def download(vid: obj.Video):

    ydl_opts = {
        "writesubtitles": True,
        "subtitlesformat": "srt",
        "outtmpl": os.path.join(config.OUTPUT_DIR, "SPON - %(uploader)s - %(title)s [%(id)s].%(ext)s"),
        "format": "bestvideo+bestaudio",
        "ffmpeg_location": config.FFMPEG_BIN,
        "logger": ytdl_logger(),
        "test": True,
    }

    # ydl_opts = [
    #     "--write-sub",
    #     "--sub-format","srt",
    #     "--output",os.path.join(config.OUTPUT_DIR, "SPON - %(uploader)s - %(title)s [%(id)s].%(ext)s"),
    #     "--format", "bestvideo+bestaudio",
    #     "--ffmpeg-location", config.FFMPEG_BIN,
    #     "--test"
    # ]


    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={vid.video_id}", ])

    # subprocess.run([os.path.join(sys.prefix,"Scripts","youtube-dl"),*ydl_opts, vid.video_id])
    # time.sleep(1)



def find_filename(video: obj.Video):
    files_w_id = []
    for root, folder, files in os.walk(config.OUTPUT_DIR, topdown=False):
        for name in files:
            if name.find(f"[{video.video_id}]") != -1:
                files_w_id.append(os.path.join(root, name))
    for f in files_w_id:
        mimetype = mimetypes.guess_type(f)[0]
        if mimetype and mimetype.find("video") != -1:
            return f



def YtDlThread(in_q, out_q):
    db = Db()
    while True:
        vid_files = in_q.get()

        for v in vid_files:
            v.status = obj.VidStatus.DOWNLOADING
            db.update_video(v)
            try:

                print(f"[{datetime.now()}] - YtDl - Getting video {v.video_id}")

                download(v)
                v.status = obj.VidStatus.FINISHED_DOWNLOADING

                v.downloaded_path = find_filename(v)
                print(f"[{datetime.now()}] - YtDl - Video {v.video_id} is stored in {v.downloaded_path}")


            except Exception as e:
                print(f"EXCEPTION - [{datetime.now()}] - YtDl - ", e)
                v.status = obj.VidStatus.ERROR_DOWNLOADING + " " + str(e)
            db.update_video(v)
            out_q.put(v)


if __name__ == "__main__":
    from queue import Queue
    from threading import Thread

    db = Db(create_new=True)
    v1 = db.create_video(
        obj.Video(None, "HeUietgDuVc", "FETCHED", None, [obj.SponsorTime(None, "123", "13", "12", 51), ], None))
    v2 = db.create_video(
        obj.Video(None, "LtlyeDAJR7A", "FETCHED", None, [obj.SponsorTime(None, "123", "13", "12", 51), ], None))

    q1 = Queue()
    q1.put([v1, ])
    q2 = Queue()
    t = Thread(target=YtDlThread, args=(q1, q2))
    t.start()
    time.sleep(10)
    q1.put([v2, ])
    # download(obj.Video(None,"LtlyeDAJR7A",None,None,None,None))
