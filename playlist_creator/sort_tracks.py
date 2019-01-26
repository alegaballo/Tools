# import re
import pandas as pd
# import numpy as np
# from collections import Counter
# import argparse
# import os.path
# import time
# from datetime import datetime

tracks = pd.read_csv('sorted_tracks.csv', dtype={'tags': str, 'genre': str})
tracks.artists = tracks.artists.str.lower()
tracks.title = tracks.title.str.lower()
tracks = tracks.sort_values(['genre', 'artists', 'title']) # for classical music
# tracks = tracks.sort_values(['genre', 'artists', 'tags','title']) # for electronic music
tracks.to_csv('sorted_tracks.csv', index=False)