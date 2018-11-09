from flask import Flask, render_template, redirect, request, session
import spotipy.util as util
import spotify_tokens
import spotipy
import sys
import requests
import urllib


app = Flask(__name__)
app.secret_key = "any random string"


@app.route("/")
def main():
    return render_template("welcome.html")


@app.route("/home")
def login():
    token = request.args["code"]
    session['sp_token'] = ""
    print(len(session))
    return "Welcome!"


@app.route("/service/spotify")
def sp_login():
    URL = "https://accounts.spotify.com/authorize"
    params = {"client_id":spotify_tokens.SPOTIPY_CLIENT_ID, "response_type":"code", "redirect_uri":spotify_tokens.SPOTIPY_REDIRECT_URI, 
                "scope":"playlist-modify-private", "show_dialog": "false"}
    r = requests.get(url = URL, params = params)
    return redirect("%s?%s" % (URL, urllib.urlencode(params)))


if __name__ == "__main__":
    app.run()
