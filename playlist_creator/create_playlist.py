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
    
    # filtered = filtered[pd.notnull(filtered['src'])]
    # filtered = filtered[filtered.apply(lambda x: any(t in x['src'].split(' ') for t in src), axis=1)]
    if rating:
       filtered = filtered[(filtered.rating >= rating)]
        # print(filtered.shape[0], 'rating')

    if artists:
        filtered = filtered[filtered.apply(lambda x: any(t in x['artists'].split(' ') for t in artists), axis=1)]
        # print(filtered.shape[0], 'artists')

    if genres:
        filtered = filtered[pd.notnull(filtered['genre'])]
        filtered = filtered[filtered.apply(lambda x: any(t in x['genre'].split(' ') for t in genres), axis=1)]
        # print(filtered.shape[0], 'genres')

    if bpm:
        beats = float(bpm.strip().split()[1])
        # print(beats)
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
        print(filtered.shape[0], 'tags out')

    elif tags_to_include:
        # print(tags_to_include)
        filtered = filtered[pd.notnull(filtered['tags'])]
        filtered = filtered[filtered.apply(lambda x: all(t in x['tags'].split(' ') for t in tags_to_include), axis=1)]
        print(filtered.shape[0], 'tags in')
    
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
        title += str(int(kwargs["rating"])) + '_'
    if kwargs["genres"]:
        title += "_".join(kwargs["genres"]) + '_'
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
    print(title)
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
    # database.artists = database.artists.str.lower()
    # database.title = database.title.str.lower()

    if args.genres == ['classical']:
        database = database.sort_values(['genre', 'artists', 'title', 'tags']) 
        print('Sorting tracks for classical music...')
    else:
        database = database.sort_values(['genre', 'artists', 'tags', 'title'])
        print('Sorting tracks for non-classical music...')
    songs = get_songs_list(database, **vars(args))
    # print(songs)

    tracks = []
    playlist_duration = 0
    # converting the playlist required duration in ms
    requested_playlist_duration = args.duration * 60 * 1000
    print('looking for', songs.shape[0], 'tracks')
    for row in songs.itertuples():
        track_id = ''
        if isinstance(row.spotify_id, str):
            # specified manually
            track_id = row.spotify_id
            # print('https://open.spotify.com/track/' + track_id)
        elif isinstance(row.youtube_id, str):
            pass
            # print('YouTube only:', row.artists, row.title)
        else:
            try:
                # single quote (') is a problem in spotify: remove it
                title_split = row.title.split(' ')
                title_track = ' '.join([w for w in title_split if "'" not in w])
                # print(title_track)
                artists_split = row.artists.split('_')
                artists_split = ' '.join(artists_split).split(' ')
                artists_track = ' '.join([w for w in artists_split if "'" not in w])
                # print(artists_split, ',,,,',artists_track)
                res = sp.search(q="track:%s artist:%s" % (title_track, artists_track), limit=1, type="track")
                # print('query', res["tracks"]["items"][0]["id"])
                track_id = res["tracks"]["items"][0]["id"]
                ttl_quote = res["tracks"]["items"][0]['name']
                ttl = ' '.join([w for w in ttl_quote.split(' ') if "'" not in w])
                # raise AssertionError(res["tracks"]["items"][0]['name'])
                artists_track_set = set(artists_track.split(' '))
                t_as = ' '.join([el['name'].lower() for el in res["tracks"]["items"][0]['album']['artists']])
                # check artist result
                for a in artists_track_set:
                    if a.lower() not in t_as:
                        msg = a + ' not in ' + str(t_as)
                        print(msg)
                        track_id = '' # discard bad search result
                        break
                        # raise AssertionError(msg)

                # check title result
                if ttl.lower() not in title_track.lower():
                    msg = ttl.lower() + ' not in ' + title_track.lower() + ' - ' + t_as
                    print(msg)
                    track_id = '' # discard bad search result


                # duration_ms = res["tracks"]["items"][0]["duration_ms"]
                # playlist_duration += duration_ms
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
                if row.src == 'sp':
                    print("Couldn't find song: {:s} - {:s} Source: {:s}".format(title_track, artists_track, row.src), file=sys.stderr)
            except AttributeError:
                print(row, ' AttributeError')
        if track_id:
            tracks.append(track_id)
    if tracks:
        print('Tracks found:', len(tracks))
        print("Creating playlist...")
        if len(tracks) <= 100: 
            playlist_id = create_spotify_playlist(sp, args.user, title)
            # print("Adding tracklist: ", tracks)
            sp.user_playlist_add_tracks(args.user, playlist_id, tracks)
        else: 
            playlist_id = create_spotify_playlist(sp, args.user, title)
            n_splits = len(tracks)//100
            for i in range(n_splits):
                tracks_split = tracks[i*100:(i+1)*100]
                # print("Adding tracklist: ", tracks_split)
                sp.user_playlist_add_tracks(args.user, playlist_id, tracks_split)
            tracks_split = tracks[100*n_splits:100*n_splits+len(tracks)%100]
            # print("Adding tracklist: ", tracks_split)
            sp.user_playlist_add_tracks(args.user, playlist_id, tracks_split)

        print("Created playlist: %s" % title)
    else:
        print('No tracks found')

if __name__ == "__main__":
    main()
