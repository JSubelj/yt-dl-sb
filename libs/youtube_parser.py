from bs4 import BeautifulSoup as bs
import requests
import json

def get_video_title(vid_id):
    content = requests.get(f"https://www.youtube.com/watch?v={vid_id}")
    soup = bs(content.content, "html.parser")
    return soup.find("meta", attrs={"name": "title"})["content"]




if __name__=="__main__":
    # content = requests.get("https://www.youtube.com/user/PewDiePie/videos")
    # soup = bs(content.content, "html.parser")
    # # print(soup)
    # title = soup.find("meta", attrs={"name": "title"}).text
    # print(soup.find("meta", attrs={"name": "title"})["content"])
    import re
    pattern = re.compile(r'window\["ytInitialData"\] = (.+?);')

    soup = bs(open("test.html","r").read(),"html.parser")
    data = soup.find("script", text=pattern).contents[0]
    tabs = json.loads(pattern.search(data).group(1))["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
    videos = None
    for t in tabs:
        if t["tabRenderer"]["title"] == "Videos":
            videos = t["tabRenderer"]["content"]
            break
    contents = videos["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["gridRenderer"]["items"]
    print(contents)




    #        contents twoColumnBrowseResultsRenderer tabs    tabRenderer content "sectionListRenderer" "contents": [contents [gridRenderer items gridVideoRenderer]]