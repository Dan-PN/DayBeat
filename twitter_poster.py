def post_tweet(input_database="top_news_songs_DB.csv", access_tokens="access_twitter.json"):
    """[Posts one Tweet based on latest flag and highest similarity score]

    Args:
        input_database (str, optional): [location of processed database csv file]. Defaults to "top_news_songs_DB.csv".
        access_tokens (str, optional): [location of json file with twitter API access tokens]. Defaults to "access_twitter.json".
    """
    import pandas as pd
    import tweepy
    import json

    data_input = pd.read_csv(input_database)
    with open(access_tokens) as jsonFile:
        jsonaccess = json.load(jsonFile)
        jsonFile.close()

    # Grab one record
    post = data_input[["Song_title", "Spotify_url", "link", "title"]][(
        data_input.Latest == "Y") & (data_input.Spotify_id.notnull())].head(1)

    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(jsonaccess["API"],
                               jsonaccess["API_S"])
    auth.set_access_token(jsonaccess["Token"],
                          jsonaccess["Token_S"])
    api = tweepy.API(auth)

    try:
        api.verify_credentials()
        print("Authentication OK")

        # Post
        post_it = ' '.join(["News Beats! Your Soundtrack for the Top News", "#newsbeats", "#"+post.Song_title.values[0], "#" +
                            post.title.values[0].split()[0], "#" + post.title.values[0].split()[1], post.Spotify_url.values[0], post.link.values[0]])
        try:
            api.update_status(post_it)
            print("Posted!")
        except:
            print("Not Posted!")
    except:
        print("Error during authentication")
