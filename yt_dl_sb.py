import argparse
from libs.sqlite_interface import Db
from libs import channel_adder
from threading import Thread
from queue import Queue

from libs.yt_ids_retrival import YtCThread
from libs.sb_times_retrival import SbRetThread
from libs.yt_dl import YtDlThread
from libs.sponsor_cutter import SCThread
import libs.config as cnf
import libs.webserver as ws


def parser():
    p = argparse.ArgumentParser(description="Looks up videos of subscribed channels, downloads them and cuts sponsors out of the video.")
    p.add_argument("-a","--add-channel", dest='channel_name')
    return p
if __name__=="__main__":
    db = Db()
    args = parser().parse_args()
    if args.channel_name:
        channel_adder.add_channel(args.channel_name)
        exit(0)


    q_ytc_to_ytdl = Queue()
    q_ytdl_to_sbret = Queue()
    q_sbret_to_sc = Queue()

    vids = db.get_not_done_videos()
    if len(vids):
        q_ytc_to_ytdl.put(vids)
    # ytc_t = Thread(target=YtCThread, args=(q_ytc_to_ytdl,))
    # ytdl_t = Thread(target=YtDlThread,args=(q_ytc_to_ytdl, q_ytdl_to_sbret))
    # sbret_t = Thread(target=SbRetThread,args=(q_ytdl_to_sbret, q_sbret_to_sc))
    # sc_t = Thread(target=SCThread,args=(q_sbret_to_sc,))
    #
    # ytc_t.start()
    # ytdl_t.start()
    # sbret_t.start()
    # sc_t.start()
    ws.run()
