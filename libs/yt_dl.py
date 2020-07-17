from youtube_dl import YoutubeDL
import libs.classes as obj
from  libs.sqlite_interface import Db
import time
# TODO: Try this!
filename = ""


def download(vid: obj.Video):
    ydl_opts = {
        "writesubtitles":True,
        "outtmpl":"SPON - %(creator)s - %(title)s.%(ext)s",
        "test": True
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={vid.video_id}",])

    return filename

def hook(d):
    global filename
    if d["status"] == "finished":
        filename = d["filename"]

def YtDlThread(in_q, out_q):
    db = Db()
    while True:
        vid_files = in_q.get()

        for v in vid_files:
            v.status = obj.VidStatus.DOWNLOADING
            db.update_video(v)
            try:
                path = download(v)
                v.status = obj.VidStatus.FINISHED_DOWNLOADING
                v.downloaded_path = path
            except Exception as e:
                v.status = obj.VidStatus.ERROR_DOWNLOADING + " " + str(e)
            db.update_video(v)
            out_q.put(v)




if __name__=="__main__":
    from queue import Queue
    from threading import Thread

    q1 = Queue()
    q1.put([obj.Video(None, "HeUietgDuVc", "FETCHED", None, [obj.SponsorTime(None, "123", "13", "12", 51), ], None),])
    q2 = Queue()
    t = Thread(target=YtDlThread, args=(q1,q2))
    t.start()
    time.sleep(10)
    q1.put([obj.Video(None, "HeUietgDuVc", "FETCHED", None, [obj.SponsorTime(None, "123", "13", "12", 51), ], None), ])
    #download(obj.Video(None,"LtlyeDAJR7A",None,None,None,None))