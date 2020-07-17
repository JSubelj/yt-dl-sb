from libs.yt_ids_retrival import YtCommunicator
from libs.sqlite_interface import Db
from libs.classes import Channel

def add_channel(name):
    ytc = YtCommunicator()
    db = Db()
    channels = ytc.get_channel_id(name)
    print("Channels found:")
    for inx,c in enumerate(channels):
        print(f"\t{inx}. {c['channel_name']}: {c['description']} [https://youtube.com/channel/{c['channel_id']}]")
    channel_num = int(input("Enter a number of correct channel: "))
    ch = channels[channel_num]
    db.create_channel(Channel(None, ch["channel_id"], ch["channel_name"], None))



if __name__=="__main__":
    add_channel("ltt")