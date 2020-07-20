import requests
import libs.classes as obj
import time
from libs import config
from libs.sqlite_interface import Db
import queue
from threading import Thread
import datetime


if hasattr(config, "REMOVE_SPONSORED"):
    REMOVE_SPONSORED = config.REMOVE_SPONSORED
else:
    REMOVE_SPONSORED = False

def get_sponsor_times(video: obj.Video):
    r = requests.get(f"https://sponsor.ajay.app/api/skipSegments?videoID={video.video_id}")
    if r.status_code == 404:
        return None

    return [obj.SponsorTime(None, video.video_id, st["segment"][0], st["segment"][1], None) for st in r.json()]


def is_sponsor_time_same(st1: obj.SponsorTime, st2: obj.SponsorTime):
    return st1.video_id == st2.video_id and abs(st1.start - st2.start) < 1 and abs(st1.stop - st2.stop) < 1


def daughterThread(vid: obj.Video, q):
    SLEEP_FOR_SECONDS = 600
    for i in range(int(config.TIME_WATCHING_FOR_SPONSORBLOCK_MIN * 60 / SLEEP_FOR_SECONDS)):
        if config.DEVELOPMENT:
            print(f"[{datetime.datetime.now()}] - SbR#{vid.video_id} - Getting sponsor times")

        sts = get_sponsor_times(vid)
        if config.DEVELOPMENT:
            print(f"[{datetime.datetime.now()}] - SbR#{vid.video_id} - Got {sts}")
        if sts:
            vid.sponsor_times = sts
            q.put(vid)
        if REMOVE_SPONSORED:
            break
        if config.DEVELOPMENT:
            SLEEP_FOR_SECONDS = 1
        time.sleep(SLEEP_FOR_SECONDS)

def _create_status(db,v,message,keyword=None):
    db.create_primitive(obj.Status, obj.Status(v.video_id, str(datetime.datetime.now()), "SbR",
                                               message,keyword=keyword))


def SbRetThread(q_in_vids: queue.Queue, q_out_vid: queue.Queue):
    db = Db()
    trd_q_dict = {}

    while True:
        try:
            # adding new
            v = q_in_vids.get_nowait()
            print(f"[{datetime.datetime.now()}] - SbR - Got new vids")


            _create_status(db,v,"Started watching for sponsor times",obj.VidStatus.WAITING_SPONSORTIMES)

            q = queue.Queue()
            t = Thread(target=daughterThread, args=(v, q))

            trd_q_dict[v.video_id] = (t,q)
            print(f"[{datetime.datetime.now()}] - SbR - Starting watcher thread for id: {v.video_id}")

            t.start()
        except queue.Empty:
            pass


        remove_keys = []
        for key, (t,q) in trd_q_dict.items():
            if not t.is_alive():
                remove_keys.append(key)
            try:
                vid = q.get_nowait()
                new, vid = db.update_video_sponsortimes_if_new(vid)
                if config.DEVELOPMENT:
                    print(f"[{datetime.datetime.now()}] - SbR - ({vid.video_id}) Updated sponsorshitp, got {new,vid}")
                if new:
                    print(f"[{datetime.datetime.now()}] - SbR - Got new sponsortimes for id: {v.video_id}")
                    _create_status(db,vid, "Got new sponsortimes")

                    q_out_vid.put(vid)

            except queue.Empty:
                pass
        for key in remove_keys:
            vid = db.get_video(key)
            db.update_video(vid)
            print(f"[{datetime.datetime.now()}] - SbR - Done watching video: {v.video_id}")
            _create_status(db,vid, "Stopped watching video for sponsortimes.",keyword=obj.VidStatus.SPONSORTIMES_DONE)

            t,q = trd_q_dict[key]
            t.join()
            q.join()
            del trd_q_dict[key]








if __name__ == "__main__":
    # print(get_sponsor_times(obj.Video(None, "iTucRz9Pdj0&t=1s", "bla", "", None, None)))
    # assert is_sponsor_time_same(obj.SponsorTime(None, "bla", "15", "20", None),
    #                             obj.SponsorTime(None, "bla", "15", "20", None))
    # assert not is_sponsor_time_same(obj.SponsorTime(None, "bla", "15", "20", None),
    #                                 obj.SponsorTime(None, "bla", "15", "21", None))
    q1= queue.Queue()
    q2 = queue.Queue()

    db = Db()
    # v1=obj.Video(None, "HeUietgDuVc", "FETCHED", None, [obj.SponsorTime(None, "123", "13", "12", 51), ], None)
    # v2=obj.Video(None, "LtlyeDAJR7A", "FETCHED", None, [obj.SponsorTime(None, "123", "13", "12", 51), ], None)
    # db.create_video(v1)
    # db.create_video(v2)
    v1 = db.get_video("ipFhGlt8Qkw")
    v2 = db.get_video("bKLM_tWOoYg")
    q1.put([v1,v2])

    SbRetThread(q1,q2)

    # When transcoding remove sponsors on just the last, always do other id first