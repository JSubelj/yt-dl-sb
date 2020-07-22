from bs4 import BeautifulSoup as bs
import requests
import json
import libs.classes as obj
import re


def get_video_title(vid_id):
    content = requests.get(f"https://www.youtube.com/watch?v={vid_id}")
    soup = bs(content.content, "html.parser")
    return soup.find("meta", attrs={"name": "title"})["content"]


def _get_video_items_from_json(j):
    tabs = j["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
    videos = None
    for t in tabs:
        if t["tabRenderer"]["title"] == "Videos":
            videos = t["tabRenderer"]["content"]
            break
    items = [i["gridVideoRenderer"] for i in
             videos["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["gridRenderer"][
                 "items"]]
    return items


def get_needed_info_from_items(items):
    # keys:
    # videoId
    # thumbnail
    # title
    # publishedTimeText
    # viewCountText
    # navigationEndpoint
    # ownerBadges
    # trackingParams
    # shortViewCountText
    # menu
    # thumbnailOverlays
    return [{"videoId": i["videoId"], "title": i["title"]["simpleText"]} for i in items]


def get_videos(ch: obj.Channel):
    pattern = re.compile(r'window\["ytInitialData"\] = (.+?);')

    content = requests.get(f"https://www.youtube.com/channel/{ch.channel_id}/videos")
    soup = bs(content.content, "html.parser")
    data = soup.find("script", text=pattern).contents[0]
    json_data = json.loads(pattern.search(data).group(1))
    items = _get_video_items_from_json(json_data)
    return get_needed_info_from_items(items)


def _get_channel_items_from_json(json_data):
    j = json_data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
        "sectionListRenderer"]["contents"]
    for o in j:
        if "itemSectionRenderer" in o.keys():
            j = o["itemSectionRenderer"]["contents"]
    return [i["channelRenderer"] for i in j]


def get_info_from_channel_items(items):
    return [{
        "channelId": i["channelId"],
        "name": i["title"]["simpleText"],
        "url": f"https://www.youtube.com/channel/{i['channelId']}",
        "thumbnail": i["thumbnail"]["thumbnails"][-1]["url"],
        "description": i["descriptionSnippet"]["runs"][0]["text"] if "descriptionSnippet" in i.keys() else None
    } for i in items]

def get_channel(name):
    pattern = re.compile(r'window\["ytInitialData"\] = (.+?);')

    # content = requests.get(f"https://www.youtube.com/results?search_query={name}&sp=EgIQAg%253D%253D")
    # soup = bs(content.content, "html.parser")
    soup = bs(open(r"C:\Users\jan.subelj\Documents\personal\yt-dl-sb\libs\\channels-test.html","r").read(), "html.parser")
    data = soup.find("script", text=pattern).contents[0]
    json_data = json.loads(pattern.search(data).group(1))
    items = _get_channel_items_from_json(json_data)
    return get_info_from_channel_items(items)


if __name__ == "__main__":
    # content = requests.get("https://www.youtube.com/user/PewDiePie/videos")
    # soup = bs(content.content, "html.parser")
    # # print(soup)
    # title = soup.find("meta", attrs={"name": "title"}).text
    # print(soup.find("meta", attrs={"name": "title"})["content"])

    pattern = re.compile(r'window\["ytInitialData"\] = (.+?);')

    # soup = bs(open("videos-test.html","r").read(),"html.parser")

    soup = bs(open("channels-test.html", "r").read(), "html.parser")
    data = soup.find("script", text=pattern).contents[0]
    json_data = \
        json.loads(pattern.search(data).group(1))["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
            "sectionListRenderer"]["contents"]
    for o in json_data:
        if "itemSectionRenderer" in o.keys():
            json_data = o["itemSectionRenderer"]["contents"]
    json_data = _get_channel_items_from_json(json.loads(pattern.search(data).group(1)))
    json.dump(get_info_from_channel_items(json_data), open("test.json", "w"))

    # items = _get_video_items_from_json(json_data)
    # get_needed_info_from_items(items)
    # json.dump(items,open("test1.json","w"),indent=4)

    #        contents twoColumnBrowseResultsRenderer tabs    tabRenderer content "sectionListRenderer" "contents": [contents [gridRenderer items gridVideoRenderer]]
