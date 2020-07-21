# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import googleapiclient.discovery
import googleapiclient.errors
import secret
import libs.classes as obj
from datetime import datetime, timedelta
import datetime as dt
from libs.sqlite_interface import Db
import pytz
import time
import re
import libs.config as config
from libs.youtube_parser import get_video_title
import schedule

_pacific_tz = pytz.timezone("US/Pacific")


def _create_status(db, v, message, keyword=None):
    db.create_primitive(obj.Status, obj.Status(v.video_id, str(datetime.now()), "YtC",
                                               message, keyword=keyword))


class YtCommunicator(metaclass=obj.Singleton):
    MAX_N_QUERIES = 10000

    # TODO: add last updated
    def __init__(self):
        self.db = Db()
        api_service_name = "youtube"
        api_version = "v3"
        self.fetched = 0
        self.last_reset = datetime.now(_pacific_tz)
        self.delay = 60
        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=secret.API_KEY)

    def check_and_reset_quota(self):
        if datetime.now(_pacific_tz).day > self.last_reset.day:
            self.fetched = 0
            self.last_reset = datetime.now(_pacific_tz)

    def calculate_delay_between_lookups(self):
        remaining_qs = YtCommunicator.MAX_N_QUERIES - self.fetched

        midnight = datetime.now(_pacific_tz) \
            .replace(hour=0, minute=0, second=0, microsecond=0) \
            .astimezone(pytz.utc)
        midnight = midnight + timedelta(days=1)
        now = datetime.now(_pacific_tz).astimezone(pytz.utc)
        remaining_seconds = (midnight - now).total_seconds()
        num_of_channels = len(self.db.get_all_channels())
        remaining_calls = remaining_qs / num_of_channels
        delay = remaining_seconds / remaining_calls
        return delay if delay > 60 else 60

    # REQUIRES OAUTH
    # def get_subscriptions(self):
    #     request = self.youtube.subscriptions().list(
    #         part="snippet,contentDetails",
    #         channelId="UCXDxv85c0rkekUrrhVs10xg"
    #     )
    #     print(request.execute())

    def get_channel_id(self, channel_name):
        request = self.youtube.search().list(
            part="snippet",
            q=channel_name,
            type="channel"
        )
        response = request.execute()
        return [{
            "channel_name": c["snippet"]["title"],
            "description": c["snippet"]["description"],
            "channel_id": c["snippet"]["channelId"],
            "thumbnail": c["snippet"]["thumbnails"]["default"]
        } for c in response["items"]]

    def get_videos(self, channel: obj.Channel):
        self.check_and_reset_quota()
        self.delay = self.calculate_delay_between_lookups()
        #
        # if not config.DEVELOPMENT:
        #     time.sleep(self.delay)
        request = self.youtube.search().list(
            part="id",
            channelId=channel.channel_id,
            maxResults=config.NUMBER_OF_YT_RESULTS,
            order="date"
        )
        response = request.execute()
        self.fetched += 1
        ignore_regex = [re.compile(pattern) for pattern in config.IGNORE_REGEX]
        for i in response["items"]:
            i["video_title"] = get_video_title(i["id"]["videoId"])

        # [print(i["snippet"]["title"]) for i in response["items"] if all([r.match(i["snippet"]["title"]) is None for r in ignore_regex])]
        vids = [obj.Video(None, i["id"]["videoId"], None, None, None, None) for i in response["items"] if
                all([r.match(i["video_title"]) is None for r in ignore_regex])]

        return vids


def _parse_time_string_to_time(time_string: str):
    return datetime.strptime(time_string, "%H:%M") - datetime.strptime("15:15", "%H:%M")


def _parse_time_string_to_sec(time_string: str):
    "d=1,h=1,m=1,s=1"
    diffrent_times = time_string.split(",")
    seconds = 0
    for t in diffrent_times:
        if t.startswith("d"):
            seconds += float(t.split("=")[1]) * 24 * 60 * 60
        if t.startswith("h"):
            seconds += float(t.split("=")[1]) * 60 * 60
        if t.startswith("m"):
            seconds += float(t.split("=")[1]) * 60
        if t.startswith("s"):
            seconds += float(t.split("=")[1])
    return seconds



def YtCWorker(q_out_ytdl):
    db = Db()
    ytc = YtCommunicator()

    channels = db.get_all_channels()
    for channel in channels:
        try:
            print(
                f"[{datetime.now()}] - YtC - Getting channel {channel.channel_name} ({channel.channel_id}) videos")
            videos = ytc.get_videos(channel)
            vids = [x[1] for x in filter(lambda x: x[0], [db.check_if_vid_exist_else_add(v) for v in videos])]
            for v in vids:
                _create_status(db, v, "Discovered video.", obj.VidStatus.FETCHED)
            print(f"[{datetime.now()}] - YtC - Got {len(vids)} new videos")

            q_out_ytdl.put(vids)
        except Exception as e:
            _create_status(db, obj.Video(None, "-1", None, None, None, None), f"[channel {channel.channel_id}] {e}",
                           obj.VidStatus.FETCHING_ERROR)

    # if config.DEVELOPMENT:
    #     ytc.delay = 10

def YtCThread(q_out_ytdl):
    if type(config.UPDATE_TIMES) == list:
        for t in config.UPDATE_TIMES:
            schedule.every().day.at(t).do(YtCThread,q_out_ytdl)
        while True:
            schedule.run_pending()
            time.sleep(1)

    elif type(config.UPDATE_TIMES) == str:
        while True:
            YtCWorker(q_out_ytdl)
            time.sleep(_parse_time_string_to_sec(config.UPDATE_TIMES))


# print(f"[{datetime.now()}] - YtC - Sleeping for {ytc.delay}s")
# if type(config.UPDATE_TIMES) == list:
#     time.sleep(1)
# elif type(config.UPDATE_TIMES) == str:
#     time.sleep(_parse_time_string_to_sec(config.UPDATE_TIMES))
#     YtCThread(q_out_ytdl)


if __name__ == "__main__":
    print(_parse_time_string_to_time("13:45"))
    # # ytc = YtCommunicator()
    # # print(ytc.calculate_waiting_time_between_lookups())
    # # print(ytc.get_videos(obj.Channel(None, "UCeeFfhMcJa1kjtfZAGskOCA", "bla", None)))
    # # print(ytc.get_channel_id("LTT"))
    # # ytc.get_subscriptions()
    #
    # from queue import Queue
    # from threading import Thread
    #
    # q1 = Queue()
    # q2 = Queue()
    # t = Thread(target=YtCThread, args=(q1, q2))
    # t.start()
    # print("sleep stop")
    #
    # print("Got first")
    # while not q1.empty():
    #     print(q1.get())
    # print("Got second")
    # print(q2.get())
    # while not q2.empty():
    #     print(q2.get())
