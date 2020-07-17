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
    start: str
    stop: str
    votes: int


@dataclass
class Video:
    id: int
    video_id: str
    status: str
    downloaded_path: str
    sponsor_times: list
    latest_sponsortime_at: datetime.datetime


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
    CUTTING = "CUTTING"  # cutting video
    DONE = "DONE"
    ERROR_DOWNLOADING = "ERROR_DOWNLOADING"
