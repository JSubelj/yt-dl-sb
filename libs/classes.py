from dataclasses import dataclass
import datetime


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


@dataclass
class Channel:
    id: int
    channel_id: str
    channel_name: str
    last_fetched: datetime.datetime


class VidStatus:
    FETCHED = "FETCHED"  # got link from yt download
    DOWNLOADING = "DOWNLOADING"  # downloading
    WAITING_SPONSORTIMES = "WAITING_SPONSORTIMES"  # waiting for sponsortimes
    CUTTING = "CUTTING"  # cutting video
    DONE = "DONE"
