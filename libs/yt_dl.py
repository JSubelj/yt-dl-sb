from youtube_dl import YoutubeDL
import libs.classes as obj
from libs.sqlite_interface import Db
import time
import config
import os
import mimetypes

# TODO: Try this!


class ytdl_logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def download(vid: obj.Video):
    global filename
    ydl_opts = {
        "writesubtitles": True,
        "subtitlesformat": "srt",
        "outtmpl": os.path.join(config.OUTPUT_DIR, "SPON - %(uploader)s - %(title)s [%(id)s].%(ext)s"),
        "format": "bestvideo+bestaudio",
        "ffmpeg_location": config.FFMPEG_BIN,
        "logger": ytdl_logger(),
        "test": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={vid.video_id}", ])
    return


def find_filename(video: obj.Video):
    files_w_id = []
    for root, folder, files in os.walk(config.OUTPUT_DIR, topdown=False):
        for name in files:
            if name.find(f"[{video.video_id}]") != -1:
                print("path: ", os.path.join(root, name))
                files_w_id.append(os.path.join(root, name))
    return files_w_id

def rename_files_return_video(video: obj.Video):
    filenames = find_filename(video)
    new_filenames = []
    for filename in filenames:
        base = os.path.dirname(filename)
        file = os.path.basename(filename)
        new_file = "".join(file.split(f" [{video.video_id}]"))
        new_filename = os.path.join(base,new_file)
        os.rename(filename,new_filename)
        new_filenames.append(new_filename)
    for f in new_filenames:
        print(mimetypes.guess_type(f))
    return new_filename

def YtDlThread(in_q, out_q):
    db = Db()
    while True:
        vid_files = in_q.get()

        for v in vid_files:
            v.status = obj.VidStatus.DOWNLOADING
            db.update_video(v)
            try:
                import sys
                print("download file")
                download(v)
                v.status = obj.VidStatus.FINISHED_DOWNLOADING

                v.downloaded_path = rename_files_return_video(v)
                print(v.downloaded_path)

            except Exception as e:
                print("EXCEPTION in YT_DL:", e)
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
