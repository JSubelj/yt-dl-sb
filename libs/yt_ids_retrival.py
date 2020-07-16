# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import secret
import libs.classes as obj

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.search().list(
        part="id",
        channelId="UCeeFfhMcJa1kjtfZAGskOCA"
    )
    response = request.execute()

    print(response)




class YtCommunicator:
    # TODO: add quota checked
    def __init__(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        self.fetched = 0

        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=secret.API_KEY)

    def get_videos(self, channel: obj.Channel):
        request = self.youtube.search().list(
            part="id",
            channelId=channel.channel_id,
            maxResults=5,
            order="date"
        )
        response = request.execute()
        self.fetched+=1
        return [obj.Video(None, i["id"]["videoId"], obj.VidStatus.FETCHED, None, None) for i in response["items"]]

if __name__ == "__main__":
    ytc = YtCommunicator()
    print(ytc.get_videos(obj.Channel(None,"UCeeFfhMcJa1kjtfZAGskOCA","bla",None)))
