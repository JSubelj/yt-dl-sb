import subprocess
import libs.classes as obj
import config
from libs.sqlite_interface import Db

def _generate_cutting_segments(video: obj.Video):
    ffmpeg_filter = "select='"
    for st in video.sponsor_times:
        ffmpeg_filter+=f"between({st.start},{st.stop})+"
    ffmpeg_filter = ffmpeg_filter[:-1]+"'"
    return ffmpeg_filter

def cut(video : obj.Video):

    print(_generate_cutting_segments(video))

    # ffmpeg_opts = [
    #     "-vf", "\"select='between(t,"
    # ]
    # subprocess.run([config.FFMPEG_BIN, "-i", video.downloaded_path,])

if __name__=="__main__":
    db = Db()
    cut(db.get_video("HeUietgDuVc"))

