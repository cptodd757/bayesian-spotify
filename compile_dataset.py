import numpy as np 
import pandas as pd 
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config

# spotify API python client
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=config.CLIENT_ID,client_secret=config.CLIENT_SECRET))

def compile_dataset(artist_ids=[],year='2019'):
    df = pd.DataFrame()

    # names of artists
    artist_names = []

    for artist_id in artist_ids:
        artist = sp.artist(artist_id)
        artist_names.append(artist['name'])

        albums = sp.artist_albums(artist_id)
        for album in albums['items']:

            # for some reason there are duplicate albums sometimes. don't include
            is_duplicate = False 
            if 'album' in df.columns:
                is_duplicate = album['name'] in df['album'].values

            if album['release_date'][0:4] == year and not is_duplicate:
                #print(album['id'],album['name'])

                tracks = sp.album_tracks(album['id'])
                for track in tracks['items']:
                    try:
                        track_features = sp.audio_features([track['id']])

                        # for some reason the API call returns a list of size 1 containing the object
                        track_obs = track_features[0]

                        # add other important fields 
                        track_obs['artist'] = artist['name']
                        track_obs['title'] = track['name'].encode("utf-8",'replace')
                        track_obs['popularity'] = sp.track(track['id'])['popularity']
                        track_obs['album'] = album['name']

                        # might have to manually coerce this into certain category we want,
                        # e.g. "rap" for Drake instead of "canadian hip hop"
                        track_obs['genre'] = artist['genres'][0]

                        df = df.append(track_obs, ignore_index=True)
                    except Exception as e:
                        print('Exception caught: ,', e)
    
    # drop unneeded metadata-like columns
    df = df.drop(columns=['analysis_url','uri','track_href'])
    df.to_csv('data/'+'_'.join(artist_names) + '_' + year + '.csv')
    return df

# artist IDs. can be found just by searching up an artist on the web player: 
# open.spotify.com/artist/artist_id_will_be_here
TRAVIS = '0Y5tJX1MQlPlqiwlOH1tJY'
DRAKE = '3TVXtAsR1Inumwj472S9r4'
DABABY = '4r63FhuTkUYltbVAg5TQnk'

compile_dataset([TRAVIS, DRAKE, DABABY])