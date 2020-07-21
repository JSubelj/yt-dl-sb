from youtube_dl import YoutubeDL
import libs.classes as obj
from libs.sqlite_interface import Db
import time
from libs import config
import os
import mimetypes
# import subprocess
from  datetime import datetime
import asstosrt
from libs.vtt_to_srt import vtt_to_srt
from threading import Thread
import queue

class ytdl_logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def _create_status(db,v,message,keyword=None):
    db.create_primitive(obj.Status, obj.Status(v.video_id, str(datetime.now()), "YtDl",
                                               message,keyword=keyword))


def download(vid: obj.Video):

    ydl_opts = {
        "writesubtitles": True,
        "subtitlesformat": "srt",
        "outtmpl": os.path.join(config.OUTPUT_DIR, "%(uploader)s/SPON - %(uploader)s - %(title)s [%(id)s].%(ext)s"),
        "format": config.DOWNLOAD_QUALITY,
        "ffmpeg_location": config.FFMPEG_BIN,
        "logger": ytdl_logger(),
        # "test": True,
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
    vid_file = None
    sub_file = None
    for root, folder, files in os.walk(config.OUTPUT_DIR, topdown=False):
        for name in files:
            if name.find(f"[{video.video_id}]") != -1:
                files_w_id.append(os.path.join(root, name))
    for f in files_w_id:
        mimetype = mimetypes.guess_type(f)[0]
        if mimetype and mimetype.find("video") != -1:
            vid_file = f
        elif len(list(filter(lambda x: x=="en",os.path.basename(f).split(".")))) > 0:
            sub_file = f
    return vid_file,sub_file

def MultiDownloadThread(v, in_q, out_q):
    db = Db()
    _create_status(db, v, "Started downloading video.", obj.VidStatus.DOWNLOADING)
    try:
        print(f"[{datetime.now()}] - YtDl - Getting video {v.video_id}")
        download(v)
        _create_status(db, v, "Finished downloading video.", obj.VidStatus.FINISHED_DOWNLOADING)

        v.downloaded_path, v.downloaded_path_subs = find_filename(v)
        if v.downloaded_path_subs.endswith("ass") or v.downloaded_path_subs.endswith("ssa"):
            print(f"[{datetime.now()}] - YtDl - Changing  {v.video_id}")

            # convert subtitles to srt
            ass_file = open(v.downloaded_path_subs)
            srt_str = asstosrt.convert(ass_file)
            base = os.path.basename(v.downloaded_path_subs)
            folder = os.path.dirname(v.downloaded_path_subs)

            base = ".".join(base.split(".")[:-1]) + ".srt"
            os.unlink(v.downloaded_path_subs)
            v.downloaded_path_subs = os.path.join(folder, base)
            with open(v.downloaded_path_subs, "w") as f:
                f.write(srt_str)
        if v.downloaded_path_subs.endswith("vtt"):
            vtt_to_srt(v.downloaded_path_subs)
            base = os.path.basename(v.downloaded_path_subs)
            folder = os.path.dirname(v.downloaded_path_subs)
            base = ".".join(base.split(".")[:-1]) + ".srt"
            os.unlink(v.downloaded_path_subs)
            v.downloaded_path_subs = os.path.join(folder, base)

        print(f"[{datetime.now()}] - YtDl - Video {v.video_id} is stored in {v.downloaded_path}")

        db.update_video(v)
        out_q.put(v)
    except Exception as e:
        print(f"EXCEPTION - [{datetime.now()}] - YtDl - ", e)

        _create_status(db, v, str(e), keyword=obj.VidStatus.ERROR_DOWNLOADING)
        if config.DEVELOPMENT:
            time.sleep(1)
        else:
            time.sleep(60)
        in_q.put([v, ])


def YtDlThread(in_q : queue.Queue, out_q: queue.Queue):
    threads = []
    while True:
        try:
            vid_files = in_q.get_nowait()
            for v in vid_files:
                q_in_t = queue.Queue()
                q_out_t = queue.Queue()
                t = Thread(target=MultiDownloadThread,args=(v,q_in_t,q_out_t))
                t.start()
                threads.append((t,q_in_t,q_out_t))
        except queue.Empty:
            pass

        threads_to_kill = []
        for i, (t,q_in_t,q_out_t) in enumerate(threads):
            try:
                while not q_in_t.empty():
                    vid_file = q_in_t.get_nowait()
                    in_q.put(vid_file)
            except queue.Empty:
                pass
            try:
                while not q_out_t.empty():
                    vid_file = q_out_t.get_nowait()
                    out_q.put(vid_file)
            except queue.Empty:
                pass
            if not t.is_alive():
                t.join()
                threads_to_kill.append(i)
        for inx in threads_to_kill:
            del threads[inx]




if __name__ == "__main__":
    vtt_to_srt("tmp.vtt")
    # db = Db()
    # v1 = db.get_video("HeUietgDuVc")
    #
    # v2 = db.get_video("W9pvsDsDi1Y")
    #
    # q1 = queue.Queue()
    # q1.put([v1, ])
    # q2 = queue.Queue()
    # t = Thread(target=YtDlThread, args=(q1, q2))
    # t.start()
    # time.sleep(10)
    # q1.put([v2, ])
    # # download(obj.Video(None,"LtlyeDAJR7A",None,None,None,None))
