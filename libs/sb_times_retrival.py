import requests
import libs.classes as obj

def get_sponsor_times(video: obj.Video):
    r=requests.get(f"https://sponsor.ajay.app/api/skipSegments?videoID={video.video_id}")
    return [obj.SponsorTime(None, video.video_id,st["segment"][0],st["segment"][1],None) for st in r.json()]

def compare_sponsor_times(st1:obj.SponsorTime,st2:obj.SponsorTime):
    return st1.video_id==st2.video_id and st1.start==st2.start and st1.stop==st2.stop

if __name__ == "__main__":
    # print(get_sponsor_times(obj.Video(None, "LtlyeDAJR7A","bla","",None)))
    assert compare_sponsor_times(obj.SponsorTime(None, "bla","15","20",None),obj.SponsorTime(None, "bla","15","20",None))
    assert not compare_sponsor_times(obj.SponsorTime(None, "bla", "15", "20", None),
                                 obj.SponsorTime(None, "bla", "15", "21", None))