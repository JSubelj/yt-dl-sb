import json
import os

_default_values = {
    "DEVELOPMENT": False,
    "TIME_WATCHING_FOR_SPONSORBLOCK_MIN": 60,
    "OUTPUT_DIR": os.path.join(os.getcwd(),"output"),
    "TMP_DIR": os.path.join(os.getcwd(),"tmp"),
    "REMOVE_SPONSORED": False,
    "DOWNLOAD_QUALITY": "bestvideo+bestaudio",
    "NUMBER_OF_YT_RESULTS": 5,
    "IGNORE_REGEX": [],
    "UPDATE_TIMES": ["00:00"] #"h=1,m=1,s=1"
}
try:
    _cnf = json.load(open(os.path.join(os.getcwd(),"config.json"),"r"))
except:
    _cnf = {"FFMPEG_BIN":"None"}

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
IGNORE_REGEX = _cnf.get("IGNORE_REGEX",_default_values["IGNORE_REGEX"])
DOWNLOAD_QUALITY = _cnf.get("DOWNLOAD_QUALITY",_default_values["DOWNLOAD_QUALITY"])
NUMBER_OF_YT_RESULTS = _cnf.get("NUMBER_OF_YT_RESULTS",_default_values["NUMBER_OF_YT_RESULTS"])
UPDATE_TIMES = _cnf.get("UPDATE_TIMES",_default_values["UPDATE_TIMES"])
