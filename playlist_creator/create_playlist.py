import os
import argparse
import spotipy
import spotipy.util as util
import spotify_tokens
from datetime import datetime
import warnings


warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import pandas as pd
def get_songs(database, filters):
    pass


def create_spotify_playlist(spotify, user, title, public=True, description="Auto-generated playlist"):
    res = spotify.user_playlist_create(user, title, public, description)
    return res['id']


def main():
    token = util.prompt_for_user_token("alegaballo", "playlist-modify-public", 
                                client_id=spotify_tokens.SPOTIPY_CLIENT_ID,
                                client_secret=spotify_tokens.SPOTIPY_CLIENT_SECRET, 
                                redirect_uri=spotify_tokens.SPOTIPY_REDIRECT_URI)
    sp = spotipy.Spotify(auth=token)
    timestamp = datetime.today().strftime('%d/%m/%Y %H:%M')
    parser = argparse.ArgumentParser(description='''Python script to create playlists on Spotify and 
    p #                                                 today.minute)
                                    Youtube starting from a csv file containing the songs list properly
                                    labeled''')
    parser.add_argument("-f", "--file", required=True, help="csv file to use as input")
    parser.add_argument("-d", "--duration", type=int, default=60, help="duration in minutes of the playlist")
    parser.add_argument("-t", "--title", default="A wonderful playlist - %s" % timestamp,
                        help="playlist title")
    args = parser.parse_args()
    playlist_id = create_spotify_playlist(sp, "alegaballo", args.title)
    # a list of IDs is expected, even if it's a single song
    sp.user_playlist_add_tracks("alegaballo", playlist_id, ["2IZdcwQPUj99UDROhTY4D4"])
#   database = pd.read_csv(args.file)
#   songs = get_songs(database, True)

if __name__ == "__main__":
    main()

