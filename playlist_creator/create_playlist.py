import os
import argparse
import pandas as pd
import spotipy
import spotipy.util as util
import spotify_tokens
from datetime import datetime

def get_songs(database, filters):
    pass


def create_spotify_playlist(spotify, user, title, public=True, description="Auto-generated playlist"):
    spotify.user_playlist_create(user, title, public, description)



def main():
    token = util.prompt_for_user_token("alegaballo", "playlist-modify-public", 
                                client_id=spotify_tokens.SPOTIPY_CLIENT_ID,
                                client_secret=spotify_tokens.SPOTIPY_CLIENT_SECRET, 
                                redirect_uri=spotify_tokens.SPOTIPY_REDIRECT_URI)
    sp = spotipy.Spotify(auth=token)
    today = datetime.today()
    playlist_timestamp = "%02d/%02d/%d %02d:%02d" % (today.day, today.month, today.year, today.hour,
                                                     today.minute)
    parser = argparse.ArgumentParser(description='''Python script to create playlists on Spotify and 
                                    Youtube starting from a csv file containing the songs list properly
                                    labeled''')
    parser.add_argument("-f", "--file", required=True, help="csv file to use as input")
    parser.add_argument("-d", "--duration", type=int, default=60, help="duration in minutes of the playlist")
    parser.add_argument("-t", "--title", default="A wonderful playlist - %s" % playlist_timestamp,
                        help="playlist title")
    args = parser.parse_args()
    create_spotify_playlist(sp, "alegaballo", args.title)
#   database = pd.read_csv(args.file)
#   songs = get_songs(database, True)

if __name__ == "__main__":
    main()

