from dataclasses import dataclass
import datetime

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



@dataclass
class SponsorTime:
    id: int
    video_id: str
    start: float
    stop: float
    votes: int


@dataclass
class Video:
    id: int
    video_id: str
    downloaded_path: str
    downloaded_path_subs: str
    sponsor_times: list
    latest_sponsortime_at: datetime.datetime

@dataclass
class Status:
    video_id: str
    added_on: str
    thread: str
    message: str
    id: int = None
    keyword: str = None

@dataclass
class Channel:
    id: int
    channel_id: str
    channel_name: str
    last_fetched: datetime.datetime


class VidStatus:
    FETCHED = "FETCHED"  # got link from yt download
    DOWNLOADING = "DOWNLOADING"  # downloading
    FINISHED_DOWNLOADING = "FINISHED_DOWNLOADING"
    WAITING_SPONSORTIMES = "WAITING_SPONSORTIMES"  # waiting for sponsortimes
    SPONSORTIMES_DONE = "SPONSORTIMES_DONE"
    CUTTING = "CUTTING"  # cutting video
    DONE = "DONE"
    ERROR_DOWNLOADING = "ERROR_DOWNLOADING"
    FETCHING_ERROR="FETCHING_ERROR"
