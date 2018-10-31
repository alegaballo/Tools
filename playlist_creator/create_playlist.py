from __future__ import print_function
import os
import argparse
import spotipy
import numpy as np
import spotipy.util as util
import spotify_tokens
import re
from datetime import datetime
import warnings
import sys


# suppressing warning from pandas import
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import pandas as pd

def get_songs_list(database, **kwargs):
    src = kwargs["source"]
    genres = kwargs["genres"]
    tags_to_include = kwargs["tags_to_include"]
    tags_to_exclude = kwargs["tags_to_exclude"]
    rating = kwargs["rating"]
    bpm = kwargs["bpm"]
    artists = kwargs["artists"]

    filtered = database
    # print(filtered.shape[0], 'database')
    filtered = filtered[pd.notnull(filtered['src'])]
    filtered = filtered[filtered.apply(lambda x: any(t in x['src'].split(' ') for t in src), axis=1)]

    if artists:
        filtered = filtered[filtered.apply(lambda x: any(t in x['artists'].split(' ') for t in artists), axis=1)]
        # print(filtered.shape[0], 'artists')
    if genres:
        filtered = filtered[pd.notnull(filtered['genre'])]
        filtered = filtered[filtered.apply(lambda x: any(t in x['genre'].split(' ') for t in genres), axis=1)]
    if rating:
        filtered = filtered[(filtered.rating >= rating)]
    if bpm:
        beats = float(bpm.strip().split()[1])
        print(beats)
        if ">" in bpm:
            filtered = filtered[filtered.bpm > beats]
        elif "<" in bpm:
            filtered = filtered[filtered.bpm < beats]
        else:
            print('bpm problem')
    if tags_to_exclude:
        filtered = filtered[pd.notnull(filtered['tags'])]
        filtered = filtered[filtered.apply(lambda x: all(t in x['tags'].split(' ') for t in tags_to_include) and\
                                              any(t not in x['tags'].split(' ') for t in tags_to_exclude), axis=1)]
    elif tags_to_include:
        filtered = filtered[pd.notnull(filtered['tags'])]
        filtered = filtered[filtered.apply(lambda x: all(t in x['tags'].split(' ') for t in tags_to_include), axis=1)]
    # print(filtered.shape[0])
    
    return filtered


def create_spotify_playlist(spotify, user, title, public=True, description="Auto-generated playlist"):
    res = spotify.user_playlist_create(user, title, public=public)
    return res['id']


def bpm_type(bpm, pattern=re.compile("[<>] \d+$")):
    if not pattern.match(bpm):
        print("Correct format: [<>] bpm", file=sys.stderr)
        raise argparse.ArgumentTypeError
    return bpm


def get_title(**kwargs):
    # title of the playlist to be created
    title = ""
    if kwargs["title"]:
        return kwargs["title"]

    if kwargs["rating"]:
        title += "rating_" + str(int(kwargs["rating"])) + '_'
    if kwargs["genres"]:
        title += "genres_" + "_".join(kwargs["genres"]) + '_'
    if kwargs["artists"]:
        title += "artists_" + "_".join(kwargs["artists"]) + '_'
    if kwargs["tags_to_include"]:
        title += "tagsIn_" + "_".join(kwargs["tags_to_include"]) + '_'
    if kwargs["tags_to_exclude"]:
        title += "tagsEx_" + "_".join(kwargs["tags_to_exclude"]) + '_'
    if kwargs["bpm"]:
        title += "bpm_" + "_" + kwargs["bpm"].replace(" ", "_") + '_'
    if title[-1]=="_":
        title = title[:-1]

    return title


def main():
    timestamp = datetime.today().strftime('%d/%m/%Y %H:%M')
    parser = argparse.ArgumentParser(description='''Python script to create playlists on Spotify and 
                                    Youtube starting from a csv file containing the songs list properly
                                    labeled''')
    parser.add_argument("-u", "--user", required=True, help="Spotify username")
    parser.add_argument("-f", "--file", required=True, help="csv file to use as input")
    parser.add_argument("-d", "--duration", type=int, default=300, help="duration in minutes of the playlist")
    parser.add_argument("-t", "--title", help="playlist title")
    parser.add_argument("-Ti", "--tags_to_include", nargs='+', help="songs tags to include in the playlist")
    parser.add_argument("-Te", "--tags_to_exclude", nargs='+', help="songs tags to exclude from the playlist")
    parser.add_argument("-g", "--genres", nargs='+', help="genres for the songs in the playlist")
    parser.add_argument("-a", "--artists", nargs='+', help="artists to include in the playlist <name_surname>")
    parser.add_argument("-b", "--bpm", type=bpm_type, help="bpm for the songs in the playlist")
    parser.add_argument("-r", "--rating", type=float, default=2.0, help="minimum rating for the songs in the playlist")
    parser.add_argument("-s", "--source", type=str, nargs='+', default="sp", help="source of the song")

    args = parser.parse_args()
    title = get_title(**vars(args)) # title of the playlist
    token = util.prompt_for_user_token(args.user, "playlist-modify-public", 
                                client_id=spotify_tokens.SPOTIPY_CLIENT_ID,
                                client_secret=spotify_tokens.SPOTIPY_CLIENT_SECRET, 
                                redirect_uri=spotify_tokens.SPOTIPY_REDIRECT_URI)

    # print(token)
    sp = spotipy.Spotify(auth=token)

    database = pd.read_csv(args.file, sep=' *, *', engine="python")
    songs = get_songs_list(database, **vars(args))
    # print(songs)
    
    tracks = []
    playlist_duration = 0
    # converting the playlist required duration in ms
    requested_playlist_duration = args.duration * 60 * 1000
    print('looking for', songs.shape[0], 'tracks')
    for row in songs.itertuples():
        # print(row.artists, row.title)
        res = sp.search(q="track:%s artist:%s" % (row.title, row.artists.replace("_", " ")), limit=1, type="track") 

        try:
            track_id = res["tracks"]["items"][0]["id"]
            duration_ms = res["tracks"]["items"][0]["duration_ms"]
            tracks.append(track_id)
            playlist_duration += duration_ms
            # print(playlist_duration, requested_playlist_duration)
            # if playlist_duration >= requested_playlist_duration:
                # print(playlist_duration, requested_playlist_duration)
                # print("Creating playlist...")
                # playlist_id = create_spotify_playlist(sp, args.user, title)
                # print("Adding tracklist: ", tracks)
                # sp.user_playlist_add_tracks(args.user, playlist_id, tracks)
                # print("Created playlist: %s" % title)
                # break
        
        except IndexError:
            print("Couldn't find song: {:s} - {:s}".format(row.title, row.artists), file=sys.stderr)
    print('tracks found:', len(tracks))
    print("Creating playlist...")
    if len(tracks) <= 100: 
        playlist_id = create_spotify_playlist(sp, args.user, title)
        print("Adding tracklist: ", tracks)
        sp.user_playlist_add_tracks(args.user, playlist_id, tracks)
    else: 
        playlist_id = create_spotify_playlist(sp, args.user, title)
        n_splits = len(tracks)//100
        for i in range(n_splits):
            tracks_split = tracks[i*100:(i+1)*100]
            print("Adding tracklist: ", tracks_split)
            sp.user_playlist_add_tracks(args.user, playlist_id, tracks_split)
        tracks_split = tracks[100*n_splits:100*n_splits+len(tracks)%100]
        print("Adding tracklist: ", tracks_split)
        sp.user_playlist_add_tracks(args.user, playlist_id, tracks_split)

    print("Created playlist: %s" % title)


if __name__ == "__main__":
    main()

