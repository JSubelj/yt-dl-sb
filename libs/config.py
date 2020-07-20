import json
import os

_default_values = {
    "DEVELOPMENT": False,
    "TIME_WATCHING_FOR_SPONSORBLOCK_MIN": 60,
    "OUTPUT_DIR": os.path.join(os.getcwd(),"output"),
    "TMP_DIR": os.path.join(os.getcwd(),"tmp"),
    "REMOVE_SPONSORED": False
}

_cnf = json.load(open(os.path.join(os.getcwd(),"config.json"),"r"))

DEVELOPMENT = _cnf.get("DEVELOPMENT", _default_values["DEVELOPMENT"])
TIME_WATCHING_FOR_SPONSORBLOCK_MIN = _cnf.get("TIME_WATCHING_FOR_SPONSORBLOCK_MIN", _default_values["TIME_WATCHING_FOR_SPONSORBLOCK_MIN"])
FFMPEG_BIN = _cnf["FFMPEG_BIN"]
OUTPUT_DIR = _cnf.get("OUTPUT_DIR", _default_values["OUTPUT_DIR"])
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
TMP_DIR = _cnf.get("TMP_DIR", _default_values["TMP_DIR"])
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)
REMOVE_SPONSORED = _cnf.get("REMOVE_SPONSORED", _default_values["REMOVE_SPONSORED"])
