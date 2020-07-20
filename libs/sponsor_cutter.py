import libs.classes as obj
from libs import config
from libs.sqlite_interface import Db
import os
from multiprocessing import Pool
from libs.ffmpeg_caller import ffmpeg_caller
import datetime
from queue import Queue





def _create_status(db,v,message,keyword=None):
    db.create_primitive(obj.Status, obj.Status(v.video_id, str(datetime.datetime.now()), "SC",
                                               message,keyword=keyword))


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
    # TODO: check if avoid negative ts corrects
    commands.append(f"{config.FFMPEG_BIN} -y -i \"{video.downloaded_path}\" -to {first} -c copy -avoid_negative_ts make_zero \"{path_name(counter)}\"")
    counter+=1
    end = skiping_times.pop()

    for skiping_time,stopping_time in zip(skiping_times,stopping_times):
        commands.append(f"{config.FFMPEG_BIN} -y -i \"{video.downloaded_path}\" -ss {skiping_time} -to {stopping_time} -c copy -avoid_negative_ts make_zero \"{path_name(counter)}\"")
    commands.append(f"{config.FFMPEG_BIN} -y -i \"{video.downloaded_path}\" -ss {end} -c copy -avoid_negative_ts make_zero \"{path_name(counter)}\"")
    counter += 1
    return commands,[path_name(i) for i in range(counter)]


def _rename_spon_file(video:obj.Video):
    base = os.path.basename(video.downloaded_path)
    dirname = os.path.dirname(video.downloaded_path)

    base = base.replace("SPON -","").replace(f" [{video.video_id}]","")
    return os.path.join(dirname,base)


def cut(video : obj.Video):
    commands, tmp_files = _generate_cutting_commands(video)
    print(f"[{datetime.datetime.now()}] - SC - Cutting useful segments of video ({video.video_id})")
    with Pool(5) as p:
        p.map(ffmpeg_caller, commands)
    tmp_inputs_txt = os.path.join(config.TMP_DIR, f"{video.video_id}_inputs.txt")
    with open(tmp_inputs_txt, "w") as f:
        f.writelines([f"file '{t}'\n" for t in tmp_files])

    print(f"[{datetime.datetime.now()}] - SC - Merging video into end result ({video.video_id})")
    ffmpeg_caller(f"{config.FFMPEG_BIN} -y -f concat -safe 0 -i \"{tmp_inputs_txt}\"  -c copy \"{_rename_spon_file(video)}\"")
    for tmp in tmp_files:
        os.remove(tmp)
    os.remove(tmp_inputs_txt)
    print(f"[{datetime.datetime.now()}] - SC - Video merged ({video.video_id})")
    if config.REMOVE_SPONSORED:
        os.remove(video.downloaded_path)
        if video.downloaded_path_subs:
            os.remove(video.downloaded_path_subs)






def SCThread(q_in : Queue):
    db = Db()
    while True:
        vids = []
        while not q_in.empty():
            vids.append(q_in.get())

        if len(vids) == 0:
            continue

        required = list(filter(lambda x: not db.is_video_done(x),vids))
        optional = list(filter(lambda x: db.is_video_done(x),vids))

        for v in required:
            _create_status(db,v,"Started cutting video", keyword=obj.VidStatus.CUTTING)
            cut(v)
            _create_status(db, v, "Finished cutting video", keyword=obj.VidStatus.DONE)

        for v in optional:
            if not q_in.empty():
                break
            _create_status(db, v, "Started cutting video", keyword=obj.VidStatus.CUTTING)
            cut(v)
            _create_status(db, v, "Finished cutting video", keyword=obj.VidStatus.DONE)





if __name__=="__main__":
    db = Db()
    import threading
    qin=Queue()
    qin.put(db.get_video("ipFhGlt8Qkw"))
    t=threading.Thread(target=SCThread,args=(qin,))
    t.start()


