# Playlist Creator

#### What is this?
It is a tool for creating playlists on Spotify from a csv file given some filtering details chosen by the user.

For example, you may want a playlist with classical pieces with piano and violin only, or a playlist with techno tracks with bpm > 130 only. 

#### How does it work?
You need:
- a csv file with your music with the following values: `artists`, `title`, `genre`, `src`, `bpm`, `tags`, `rating` (see below for further details on this),
- to [register your app](https://spotipy.readthedocs.io/en/latest/#authorized-requests) for Spotify to get the access token 
- to create a file named `spotify_tokens.py` with your `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI`) and whitelist the `SPOTIPY_REDIRECT_URI` in your app 
- [spotipy](https://spotipy.readthedocs.io/en/latest/#installation)
- run the script `create_playlist.py` with the arguments you want for filtering (see below for further details)

#### Details about the csv file
Below the list of column names the csv file can have. If a track has no value for a specific column name, then it won't be considered when a filter is applied on that column.
 
- `artists`: list of composers of the track
    * when the artist's name is formed by multiple words (e.g., `Tale Of Us`), spaces must be replaced by underscore (e.g., `Tale_Of_Us`)
    * when a track has multiple artists, they should be separated by spaces (e.g., `Tale_Of_Us Mind_Against`)
- `title`: title of the track
- `genre`: genre of the track (could be more than one, e.g.,  `acid techno`)
- `src`: source, where the track can be found
    * `sp` for Spotify 
    * `sc` for SoundCloud
    * `yt` for Youtube
    * if a track is both on Spotify and YouTube you can specify it i.e., "`sp yt`"
- `bpm`: beat per minute of the track
- `tags`: list of words describing the track
    * instruments used (piano, cello, orchestra, ...)
    * adjectives 
        - `soft`: generally for relaxing classical or neoclassical pieces 
        - `heavy`: generally for electronic and techno tracks with heavy bass
        - `powerful`: generally for energetic classical pieces 
        - `dark`
        - `melodic` : generally for electronic music with a melody
    * others or your own:
        - `dj_set`
        - ...
- `rating`: personal rating of the track
    * `1` if the track is not that great
    * `2` if the track is great
    * `3` if the track is extraordinary

#### Details about the arguments
- `-u` (required): Spotify username
- `-f` (required): csv file with tracks
- `-g` : genres for the songs in the playlist (can be multiple genres separated by spaces)
- `-a` : artists to include in the playlist (can be multiple tags separated by spaces)
- `-Ti` : song tags to include in the playlist (can be multiple tags separated by spaces)
- `-Te` : song tags to exclude from the playlist (can be multiple tags separated by spaces)
- `-b` : bpm for the tracks in the playlist (e.g., -b "> 130")
- `-r` (default: `2`): minimum rating for the songs in the playlist
- `-s` (default: `sp`): source of the song
- `-d` (default: `300`): max duration of playlist in minutes
- `-t` (default: concatenation of the filtering arguments): playlist title

### TODO:
- select Spotify query results without the word "live"
- add support for YouTube playlists
- add support for SoundCloud playlists
