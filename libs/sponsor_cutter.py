import subprocess
import libs.classes as obj
import config
from libs.sqlite_interface import Db
import os
from multiprocessing import Pool
from libs.ffmpeg_caller import ffmpeg_caller

# def _generate_cutting_segments(video: obj.Video):
#     ffmpeg_filter = "'"
#     for st in video.sponsor_times:
#         ffmpeg_filter+=f"between(t,{st.start},{st.stop})+"
#     ffmpeg_filter = ffmpeg_filter[:-1]+"'"
#     return ffmpeg_filter

# def _generate_cutting_segments(video: obj.Video):
#     ffmpeg_filter = "\""
#     segs = 0
#     for st in video.sponsor_times:
#
#         ffmpeg_filter += f"[0:v]trim=start={st.start}:end={st.stop},setpts=PTS-STARTPTS[{segs}v]; "
#         ffmpeg_filter += f"[0:a]atrim=start={st.start}:end={st.stop},asetpts=PTS-STARTPTS[{segs}a]; "
#         segs += 1
#         # ffmpeg_filter+=f"between(t,{st.start},{st.stop})+"
#     for i in range(segs):
#         ffmpeg_filter += f"[{i}v][{i}a]"
#     ffmpeg_filter += f"concat=n={segs}:v=1:a=1[outv][outa]\" -map [outv] -map [outa]"
#     return ffmpeg_filter

def _generate_cutting_commands(video: obj.Video):
    # cuts viable parts and puts them in file
    def path_name(c):
        end = video.downloaded_path.split(".")[-1]
        return os.path.join(config.TMP_DIR, video.video_id + '_' + str(c)+".tmp."+end)
    commands = []
    skiping_times = []
    stopping_times = []
    for st in video.sponsor_times:
        skiping_times.append(st.stop)
        stopping_times.append(st.start)

    first = stopping_times.pop(0)
    counter = 0
    commands.append(f"{config.FFMPEG_BIN} -y -i \"{video.downloaded_path}\" -to {first} -c copy \"{path_name(counter)}\"")
    counter+=1
    end = skiping_times.pop()

    for skiping_time,stopping_time in zip(skiping_times,stopping_times):
        commands.append(f"{config.FFMPEG_BIN} -y -i \"{video.downloaded_path}\" -ss {skiping_time} -to {stopping_time} -c copy \"{path_name(counter)}\"")
        counter+=1
    commands.append(f"{config.FFMPEG_BIN} -y -i \"{video.downloaded_path}\" -ss {end} -c copy \"{path_name(counter)}\"")
    counter += 1
    return commands,[path_name(i) for i in range(counter)]






def _rename_spon_file(video:obj.Video):
    base = os.path.basename(video.downloaded_path)
    dirname = os.path.dirname(video.downloaded_path)

    base = base.replace("SPON -","")
    return os.path.join(dirname,base)


def cut(video : obj.Video):
    # BUG: When cutting files frames can get lost idk why
    commands, tmp_files = _generate_cutting_commands(video)
    with Pool(5) as p:
        p.map(ffmpeg_caller, commands)
    tmp_inputs_txt = os.path.join(config.TMP_DIR, f"{video.video_id}_inputs.txt")
    with open(tmp_inputs_txt, "w") as f:
        f.writelines([f"file '{t}'\n" for t in tmp_files])

    ffmpeg_caller(f"{config.FFMPEG_BIN} -y -f concat -safe 0 -i \"{tmp_inputs_txt}\"  -c copy \"{_rename_spon_file(video)}\"")
    for tmp in tmp_files:
        os.remove(tmp)
    os.remove(tmp_inputs_txt)

if __name__=="__main__":
    db = Db()
    cut(db.get_video("HeUietgDuVc"))

