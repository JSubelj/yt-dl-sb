from flask import Flask, json, render_template
import libs.youtube_parser as ytp

app = Flask(__name__,template_folder=r"C:\Users\jan.subelj\Documents\personal\yt-dl-sb\templates")

companies = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]

@app.route('/companies', methods=['GET'])
def get_companies():

    return json.dumps(companies)

@app.route('/channels/<name>')
def show_channels(name):
    # show the user profile for that user
    return json.dumps(ytp.get_channel(name))

@app.route('/add_channels')
def add_channels():
    # show the user profile for that user
    return render_template('channel_selector.html')


def run():
    app.run()