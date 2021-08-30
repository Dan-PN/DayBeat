# %%
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json


def get_spotify_data(input_data="top_news_songs_DB.csv", filter_by_Latest=True, access_tokens="access_spotify.json", output_file="top_news_songs_DB.csv"):
    """[Uses Spotify API to extract ID and Spotify link for each song]

    Args:
        input_data (str, optional): [location of top songs/news database csv file]. Defaults to "top_news_songs_DB.csv".
        filter_by_Latest (bool, optional): [Flag to limit he API request. If True only rows with Latest = Y will be processed]. Defaults to True.
        access_tokens (str, optional): [location of json file with Spotify API access client and secret]. Defaults to "access_spotify.json".
        output_file (str, optional): [Output csv file]. Defaults to "top_news_songs_DB.csv".
    """
    with open(access_tokens) as jsonFile:
        jsonaccess = json.load(jsonFile)
        jsonFile.close()

    data_input = pd.read_csv(input_data)

    # Split DF based on what needs to be run by API
    if filter_by_Latest:
        process_df = data_input[data_input.Latest == "Y"]
        rest_df = data_input[data_input.Latest == "N"]
    else:
        process_df = data_input
        rest_df = pd.DataFrame(columns=list(data_input.columns))

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=jsonaccess["client_id"],
                                                               client_secret=jsonaccess["client_secret"]))

    # Spotify API call one by one - Get id and Spotify link
    for row in process_df.itertuples(index=True):

        song_title_processed = str(row.Song_title).replace("Featuring", "", -1)

        try:
            result = sp.search(q=song_title_processed, limit=1, type="track")
            process_df.at[row.Index,
                          "Spotify_url"] = result['tracks']['items'][0]['external_urls']['spotify']
            process_df.at[row.Index,
                          "Spotify_id"] = result['tracks']['items'][0]['id']
        except:
            pass

    result = pd.concat([process_df, rest_df])
    result.to_csv(output_file, index=False)
