import requests
import re

print("Welcome to Lyrics Tags Generator.")

print("")

start = input("Enter any key to start...")

error = {
    "message": {
        "characterLimitExceeded": "Character limit exceeded.",
        "provideAllRequiredFields": "Please provide all the required fields.",
        "removeCommasFromTitle": "Please remove any commas , from the title or artist.",
        "somethingWentWrong": "Something went wrong.",
        "provideTitle": "Please provide the title.",
        "provideArtist": "Please provide the artist.",
        "nothingToClear": "There's nothing to clear.",
        "provideAValidGenre": "Please provide a valid genre.",
        "generateTagsFirst": "Please generate the tags first.",
        "removeSpecialCharactersAndNumbersExceptCommasVerse": "Please remove any numbers or special characters.",
        "threeVersesAreOnlyAllowed": "You can only include 3 verses.",
        "generateTagsBeforeYouCopyToClipboard": "Please generate the tags before you copy to clipboard.",
        "tagsAlreadyRemoved": "Recommended tags have already been removed.",
        "invalidFormat": "Invalid format.",
        "methodNotAllowed": "Method Not Allowed",
    }
}

ARTIST_INPUT_FIELD_CHARACTER_LIMIT_FORMATTED = 100
CHANNEL_NAME_INPUT_FIELD_CHARACTER_LIMIT = 30
FEATURES_INPUT_FIELD_CHARACTER_LIMIT = 30
ARTIST_INPUT_FIELD_CHARACTER_LIMIT = 30
TITLE_INPUT_FIELD_CHARACTER_LIMIT = 45

print("")

artist = input("*Artist: ")
title = input("Title: ")
features = input("Features: ")
channel_name = input("Channel: ")
tiktok = input("TikTok: ")
format = input("Format (Lyrics, Bass Boosted, Nightcore/Sped Up, Slowed/Reverb, Letra, Phonk): ")
genre = input("Genre (None, Country, Latin, Phonk, Pop, Rap): ")
verse = input("Verse: ")

print("")

def generate(artist: str, title: str, features: str, channel_name: str, tiktok: str, format: str, genre: str, verse: str):
    # Checks if the artist was provided.
    if len(artist) == 0:
        error_message = error["message"]["provideArtist"]
        print(f"[ARTIST] {error_message}")
        return
    
    # Check if the artist field ends with ",-" which means the title wasn't provided.
    if artist.endswith(",-"):
        error_message = error["message"]["provideTitle"]
        print(f"[ARTIST] {error_message}")
        return
    
    # Check if the artist field starts with ",-" which means the title wasn't provided.
    if artist.startswith(",-"):
        error_message = error["message"]["invalidFormat"]
        print(f"[ARTIST] {error_message}")
        return
    
    # Check if there are any commas in the title.
    if "," in title:
        error_message = error["message"]["removeCommasFromTitle"]
        print(f"[TITLE] {error_message}")
        return 
    
    # Checks if artist contains a comma.
    if "," in artist or "-" in artist:
        # Checks if the artist field reaches the character limit (formatted).
        if len(artist) > ARTIST_INPUT_FIELD_CHARACTER_LIMIT_FORMATTED:
            error_message = error["message"]["characterLimitExceeded"]
            print(f"[ARTIST] {error_message}")
            return
    else:
        # Checks if the artist field reaches the character limit.
        if len(artist) > ARTIST_INPUT_FIELD_CHARACTER_LIMIT:
            error_message = error["message"]["characterLimitExceeded"]
            print(f"[ARTIST] {error_message}")
            return
        
    # Checks if the title field reaches the character limit.
    if len(title) > TITLE_INPUT_FIELD_CHARACTER_LIMIT:
        error_message = error["message"]["characterLimitExceeded"]
        print(f"[TITLE] {error_message}")
        return

    # Checks if the features field reaches the character limit.
    if len(features) > FEATURES_INPUT_FIELD_CHARACTER_LIMIT:
        error_message = error["message"]["characterLimitExceeded"]
        print(f"[FEATURES] {error_message}")
        return
    
    # Checks if the channel name field reaches the character limit.
    if len(channel_name) > CHANNEL_NAME_INPUT_FIELD_CHARACTER_LIMIT:
        error_message = error["message"]["characterLimitExceeded"]
        print(f"[CHANNEL NAME] {error_message}")
        return
    
    # Checks if the artist and title is not provided in the artist field.
    if not re.search(r"-", artist):
        if not title:
            error_message = error["message"]["provideTitle"]
            print(f"[ARTIST] [TITLE] {error_message}")
            return
        
    # Checks if verse contains any numbers or special characters.
    if len(verse) > 0 and not re.fullmatch(r"[a-zA-Z ,]*", verse):
        error_message = error["message"]["removeSpecialCharactersAndNumbersExceptCommasVerse"]
        print(f"[VERSE] {error_message}")
        return
    
    # Checks if verse contains a comma, if does then we split the verses and check if there are more than 3 verses.
    if len(verse) > 0 and ',' in verse:
        verse_split = verse.split(",")

        # If there's more than 3 verses then send back a error response
        if len(verse_split) > 3:
            error_message = error["message"]["threeVersesAreOnlyAllowed"]
            print(f"[VERSE] {error_message}")
            return
        
    formats = ["lyrics", "bassboosted", "nightcore", "slowed", "letra", "phonk"]

    # Checks if a valid format was provided.
    if format.lower() not in formats:
        error_message = error['message']['invalidFormat']
        print(f"[FORMAT] {error_message}. Defaulted to 'Lyrics'.")
        format = "lyrics"
    
    genres = ["none", "country", "latin", "phonk", "pop", "rap"]

    # Checks if a valid genre was provided.
    if genre.lower() not in genres:
        print("[GENRE] Defaulted to 'None'.")
        genre = "none"

    print("")
    
    url = "https://tags.notnick.io/api/generate"

    payload = {
        "title": title if title else "none",
        "artist": artist,
        "features": features if features else "none",
        "channel": channel_name if channel_name else "none",
        "tiktok": "true" if tiktok.lower() in ["true", "t"] else "false",
        "format": format,
        "genre": genre,
        "verse": verse if verse else "none"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.get(url, params=payload, headers=headers)

    if response.status_code == 200:
        print("Here's your generated tags:\n")
        print(response.json()["removedTags"])

        print("")

        response_url_path = response.json()["url"]

        url = "https://tags.notnick.io"

        print(f"Link: {url}{response_url_path}")


    else:
        error_message = response.json()["error"]
        print(f"Error: {error_message}")

generate(artist, title, features, channel_name, tiktok, format, genre, verse)

