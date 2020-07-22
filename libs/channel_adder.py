from libs.youtube_parser import get_channel
from libs.sqlite_interface import Db
from libs.classes import Channel

def add_channel(name):

    db = Db()
    channels = get_channel(name)
    print("Channels found:")
    for inx,c in enumerate(channels):
        print(f"\t{inx}. {c['name']}: {c['description']} [https://youtube.com/channel/{c['channel_id']}]")
    channel_num = int(input("Enter a number of correct channel: "))
    ch = channels[channel_num]
    db.create_channel(Channel(None, ch["channelId"], ch["name"], None))



if __name__=="__main__":
    add_channel("ltt")