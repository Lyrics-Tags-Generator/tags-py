import requests # type: ignore
import re

# Welcome message
print("Welcome to Lyrics Tags Generator.")
print("")

# Pause until user presses a key
start = input("Enter any key to start...")

# Centralized error messages (for consistency across script)
error = {
    "message": {
        "artistAndTitleAlreadyProvidedInTheArtistField": "The artist and title was already provided in the artist field.",
        "removeSpecialCharactersAndNumbersExceptCommasVerse": "Please remove any numbers or special characters.",
        "somethingWentWrongRetrievingCustomFormatKey": "Something went wrong retrieving the custom format key.",
        "generateTagsBeforeYouCopyToClipboard": "Please generate the tags before you copy to clipboard.",
        "youHaveAlreadyGeneratedTheExampleResponse": "You've already generated the example response.",
        "removeCommasFromTitle": "Please remove any commas , from the title or artist.",
        "needToProvideAllValidVariables": "You need to provide the valid variables.",
        "provideAllRequiredFields": "Please provide all the required fields.",
        "tagsAlreadyRemoved": "Recommended tags have already been removed.",
        "providedVariablesNotValid": "The provided variable is not valid.",
        "threeVersesAreOnlyAllowed": "You can only include 3 verses.",
        "generateTagsFirst": "Please generate the tags first.",
        "provideAValidGenre": "Please provide a valid genre.",
        "characterLimitExceeded": "Character limit exceeded.",
        "somethingWentWrong": "Something went wrong.",
        "provideArtist": "Please provide the artist.",
        "nothingToClear": "There's nothing to clear.",
        "enterValidKey": "Please enter a valid key.",
        "provideTitle": "Please provide the title.",
        "methodNotAllowed": "Method Not Allowed",
        "invalidFormat": "Invalid format.",
    }
}


# Input field character limits (for validation)
ARTIST_INPUT_FIELD_CHARACTER_LIMIT_FORMATTED = 100
CHANNEL_NAME_INPUT_FIELD_CHARACTER_LIMIT = 30
FEATURES_INPUT_FIELD_CHARACTER_LIMIT = 30
ARTIST_INPUT_FIELD_CHARACTER_LIMIT = 30
TITLE_INPUT_FIELD_CHARACTER_LIMIT = 45

# Prints a new line
print("")

# Collect user inputs for tag generation
artist = input("*Artist: ")
title = input("Title: ")
features = input("Features: ")
channel_name = input("Channel: ")
tiktok = input("TikTok: ")
format = input("Format (Lyrics, Bass Boosted, Nightcore/Sped Up, Slowed/Reverb, Letra, Testo, Phonk): ")
genre = input("Genre (None, Country, Latin, Italian, Phonk, Pop, Rap): ")
verse = input("Verse: ")

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
        
    formats = ["lyrics", "bassboosted", "nightcore", "slowed", "letra", "testo", "phonk", "none"]

    # Prints a new line
    print("")

    # Checks if a valid format was provided.
    if format.lower() not in formats:
        error_message = error['message']['invalidFormat']
        print(f"[FORMAT] {error_message}. Defaulted to 'Lyrics'.")
        format = "lyrics"
    
    genres = ["none", "country", "latin", "italian", "dance" "phonk", "pop", "rap"]

    # Checks if a valid genre was provided.
    if genre.lower() not in genres:
        print("[GENRE] Defaulted to 'None'.")
        genre = "none"

    # Prints a new line
    print("")

    # API endpoint for tag generation
    url = "https://tags.notnick.io/api/v1/generate"

    # Build the payload with provided inputs (fallbacks to "none" if empty)
    payload = {
        "tiktok": "true" if tiktok.lower() in ["true", "t"] else "false",
        "channel": channel_name if channel_name else "none",
        "features": features if features else "none",
        "title": title if title else "none",
        "verse": verse if verse else "none",
        "genre": genre.lower(),
        "source": "tags-py",
        "format": format,
        "artist": artist,
    }

    # Set headers for the request
    headers = {
        "Content-Type": "application/json"
    }

    # Show loading message before making request
    print("⏳ Loading, please wait...")

    # Send GET request to API with payload
    response = requests.get(url, params=payload, headers=headers)

    # Clear the loading message once response is back
    print("\033[1A\033[K", end="")

    # If request succeeded
    if response.status_code == 200:
        print("Here's your generated tags:\n")

        # Extract tags from JSON response
        tags = response.json()["removedTags"]
        print(tags)
        print("")

        # Extract response ID and URL path
        response_id = response.json()["responseId"]
        response_url_path = response.json()["url"]

        # Base URL for full link
        url = "https://tags.notnick.io"

        # Print link and response ID
        # print(f"Link: {url}{response_url_path}\n")
        print(f"Response: {response_id}")

    # If request failed, show error
    else:
        error_message = response.json()["error"]
        print(f"Error: {error_message}")


# Call the generate method
generate(artist, title, features, channel_name, tiktok, format, genre, verse)

