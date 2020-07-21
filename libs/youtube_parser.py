from bs4 import BeautifulSoup as bs
import requests

def get_video_title(vid_id):
    content = requests.get(f"https://www.youtube.com/watch?v={vid_id}")
    soup = bs(content.content, "html.parser")
    return soup.find("meta", attrs={"name": "title"})["content"]




if __name__=="__main__":
    content = requests.get("https://www.youtube.com/user/PewDiePie/videos")
    soup = bs(content.content, "html.parser")
    # print(soup)
    title = soup.find("meta", attrs={"name": "title"}).text
    print(soup.find("meta", attrs={"name": "title"})["content"])