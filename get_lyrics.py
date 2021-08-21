
from numpy import nan
import billboard
import pandas as pd
import lyricsgenius
import numpy as np
import json


def master_get_lyrics(access_tokens="access.json", songs_database="Songs_database.csv"):
    """Extracts latest billboard songs & 
       Extract corresponding lyrics from Genius &
       Adds new lyrics to song database

    Args:
        access_tokens (str): [location of json file with genius API access token]. Defaults to "access.json".
        songs_database (str): [location of songs database csv file ]. Defaults to "Songs_database.csv".
    """
    with open(access_tokens) as jsonFile:
        jsonaccess = json.load(jsonFile)
        jsonFile.close()

    def get_lyrics_genius(search_title="", search_artist="", access_token_genius=None):
        """Extracts Lyrics from genius website"""

        genius = lyricsgenius.Genius(access_token=access_token_genius,
                                     remove_section_headers=True, retries=10, sleep_time=0.1)

        try:
            song = genius.search_song(title=search_title, artist=search_artist, song_id=None,
                                      get_full_info=True)

        except:
            return "Not_Found"
        if not song:
            return "Not_Found"
        return str(song.lyrics)

    # Load Current Unique top songs from billboard

    try:
        chart_hot_100 = billboard.ChartData(
            'hot-100', date=None, year=None, fetch=True, timeout=25)
        chart_200_global = billboard.ChartData(
            'billboard-global-200', date=None, year=None, fetch=True, timeout=25)

        chart_hot_100_list = [str(entry.title) + " " + str(entry.artist)
                              for entry in chart_hot_100]

        chart_200_global_list = [str(entry.title) + " " + str(entry.artist)
                                 for entry in chart_200_global]

        Songs_list = chart_hot_100_list + chart_200_global_list
        Songs_list = list(set(Songs_list))
        print("Billboard Extracted")
    except:
        print("Unable to Extract Billboard")
        Songs_list = []

    # Load previous Database & Consolidate Data
    Songs_database_old = pd.read_csv(songs_database)
    Songs_database = pd.DataFrame(data=Songs_list, columns=["Song_title"])
    Songs_database["Lyrics"] = np.nan

    Songs_database = pd.concat([Songs_database_old, Songs_database])
    Songs_database.sort_values(
        by=['Song_title', 'Lyrics'], axis=0, ascending=True, na_position='last', inplace=True)

    Songs_database.drop_duplicates(
        subset=['Song_title'], keep='first', inplace=True)

    # Get Lyrics from Genius for new entries
    for row in Songs_database.itertuples(index=True):

        if len(str(row.Lyrics)) < 100:

            Songs_database.at[row.Index, "Lyrics"] = get_lyrics_genius(
                search_title=str(row.Song_title), access_token_genius=jsonaccess["genius_token"])

    Songs_database.Lyrics = Songs_database.Lyrics.str.replace(
        pat="\n", repl=" ", regex=False)

    Songs_database.Lyrics = Songs_database.Lyrics.str.replace(
        pat="//", repl=" ", regex=False)

    # Overwrite Database with new data
    Songs_database.to_csv(songs_database, index=False,
                          encoding='utf-8')
    print("Database Updated")

# %%
