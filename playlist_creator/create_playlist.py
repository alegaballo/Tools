import os
import argparse
import spotipy
import spotipy.util as util
import spotify_tokens
from datetime import datetime
import warnings

# suppressing warning from pandas import
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import pandas as pd

def get_songs(database, **kwargs):
    genres = kwargs["genre(s)"]
    moods = kwargs["mood(s)"]
    print(database.genre)
    print(genres)
    print(database.genre.isin(genres))

def create_spotify_playlist(spotify, user, title, public=True, description="Auto-generated playlist"):
    res = spotify.user_playlist_create(user, title, public, description)
    return res['id']


def main():
    timestamp = datetime.today().strftime('%d/%m/%Y %H:%M')
    parser = argparse.ArgumentParser(description='''Python script to create playlists on Spotify and 
                                    Youtube starting from a csv file containing the songs list properly
                                    labeled''')
    parser.add_argument("-u", "--user", required=True, help="Spotify username")
    parser.add_argument("-f", "--file", required=True, help="csv file to use as input")
    parser.add_argument("-d", "--duration", type=int, default=60, help="duration in minutes of the playlist")
    parser.add_argument("-t", "--title", default="A wonderful playlist - %s" % timestamp, help="playlist title")
    parser.add_argument("-m", "--mood(s)", nargs='+', help="expected mood of the desired playlist")
    parser.add_argument("-g", "--genre(s)", nargs='+', help="expected genre for the songs in the playlist")
    args = parser.parse_args()
    token = util.prompt_for_user_token(args.user, "playlist-modify-public", 
                                client_id=spotify_tokens.SPOTIPY_CLIENT_ID,
                                client_secret=spotify_tokens.SPOTIPY_CLIENT_SECRET, 
                                redirect_uri=spotify_tokens.SPOTIPY_REDIRECT_URI)
    sp = spotipy.Spotify(auth=token)
    
    #playlist_id = create_spotify_playlist(sp, args.user, args.title)
    # a list of IDs is expected, even if it's a single song
    #sp.user_playlist_add_tracks(args.user, playlist_id, ["2IZdcwQPUj99UDROhTY4D4"])
    database = pd.read_csv(args.file, skipinitialspace=True)
    songs = get_songs(database, **vars(args))

if __name__ == "__main__":
    main()

