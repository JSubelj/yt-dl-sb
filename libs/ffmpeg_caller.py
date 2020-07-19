import subprocess


# because multiprocessing is stupid and this function has to be in a separate file
def ffmpeg_caller(command_string):
    subprocess.run(command_string)