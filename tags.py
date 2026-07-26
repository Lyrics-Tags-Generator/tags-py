import requests # type: ignore
import threading
import ctypes
import time
import sys
import re
import os

# Enable ANSI escape sequences on Windows terminals (no-op elsewhere).
if os.name == "nt":
    try:
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        # -11 = STD_OUTPUT_HANDLE, 0x0004 = ENABLE_VIRTUAL_TERMINAL_PROCESSING
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass

# Ensure Unicode (banner art, spinner glyphs) renders regardless of the
# terminal's default code page.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except (AttributeError, ValueError):
    pass

# ANSI color / style helpers
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
GRAY    = "\033[90m"


def prompt(label: str, hint: str = "", required: bool = False) -> str:
    """Renders a styled input prompt."""
    star = f"{RED}*{RESET}" if required else " "
    hint_str = f" {GRAY}({hint}){RESET}" if hint else ""
    return input(f"{star}{CYAN}❯{RESET} {BOLD}{label}{RESET}{hint_str}{GRAY}:{RESET} ")


class Spinner:
    """A lightweight animated spinner shown while waiting for the request."""

    def __init__(self, message: str = "Loading"):
        self.message = message
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._spin)

    def _spin(self):
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while not self._stop.is_set():
            frame = frames[i % len(frames)]
            print(f"\r{CYAN}{frame}{RESET} {self.message}...", end="", flush=True)
            i += 1
            time.sleep(0.08)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join()
        print("\r\033[K", end="", flush=True)


def write_metadata(data: dict) -> str:
    """Writes all generated metadata to a text file and returns its filename."""
    extras = data.get("extras", {})
    arrays = extras.get("array", {})

    # Suggested titles and SEO keywords come back as "=" separated strings.
    titles = arrays.get("titles") or [t for t in extras.get("titles", "").split("=") if t]
    seo = [k for k in extras.get("seo", {}).get("text", "").split("=") if k]
    hashtags = [f"#{tag}" for tag in data.get("hashtags", [])]
    tags = data.get("removedTags", "")

    def section(heading: str, body: str) -> str:
        line = "=" * 50
        return f"{line}\n{heading}\n{line}\n{body}\n\n"

    content = (
        f"Artist: {data.get('artist', '')}\n"
        f"Title: {data.get('title', '')}\n"
        f"Genre: {data.get('genre', '')}\n\n"
        + section("TAGS", tags)
        + section("SUGGESTED TITLES", "\n".join(titles))
        + section("SEO KEYWORDS", "\n".join(seo))
        + section("HASHTAGS", " ".join(hashtags))
    )

    # Build a safe, descriptive filename from the artist and title.
    base = f"{data.get('artist', '')} - {data.get('title', '')}".strip(" -")
    safe = re.sub(r'[<>:"/\\|?*]', "", base) or "metadata"

    # Save inside a dedicated metadata directory, creating it if needed.
    os.makedirs("metadata", exist_ok=True)
    filepath = os.path.join("metadata", f"{safe} metadata.txt")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


# Welcome message
print("Welcome to Lyrics Tags Generator.")
print("")

# Pause until user presses a key
input(f"{GRAY}Press Enter to start...{RESET}")

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
artist = prompt("Artist", required=True)

# If the artist field already contains both the artist and title (the "Artist -
# Title" format), the backend parses the artist/title out of that single field,
# so skip the Title and Verse prompts. Still prompt for the remaining options.
if "-" in artist or "—" in artist:
    title = ""
    verse = ""

    # Everything before the title separator is the artist plus any features.
    separator = "—" if "—" in artist else "-"
    main_part = artist.split(separator)[0]

    # Features are already provided inline if there's any artist after the first
    # one (separated by a comma or &). Only prompt for features if there aren't.
    if "," in main_part or "&" in main_part:
        features = ""
    else:
        features = prompt("Features")

    channel_name = prompt("Channel")
    tiktok = prompt("TikTok", hint="true/false")
    format = prompt("Format", hint="Lyrics, Bass Boosted, Nightcore/Sped Up, Slowed/Reverb, Letra, Testo, Phonk")
    genre = prompt("Genre", hint="None, Country, Latin, Italian, Dance, Phonk, Pop, Rap, Alternative, Emo, Rock, EDM, Trap, Electronic")
    shuffle = prompt("Shuffle", hint="yes/no")
    metadata = prompt("Save metadata file", hint="yes/no")
else:
    title = prompt("Title")
    features = prompt("Features")
    channel_name = prompt("Channel")
    tiktok = prompt("TikTok", hint="true/false")
    format = prompt("Format", hint="Lyrics, Bass Boosted, Nightcore/Sped Up, Slowed/Reverb, Letra, Testo, Phonk")
    genre = prompt("Genre", hint="None, Country, Latin, Italian, Dance, Phonk, Pop, Rap, Alternative, Emo, Rock, EDM, Trap, Electronic")
    verse = prompt("Verse")
    shuffle = prompt("Shuffle", hint="yes/no")
    metadata = prompt("Save metadata file", hint="yes/no")

def generate(artist: str, title: str, features: str, channel_name: str, tiktok: str, format: str, genre: str, verse: str, shuffle: str, metadata: str):
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
        print(f"{YELLOW}![FORMAT]{RESET} {error_message} Defaulted to {BOLD}'Lyrics'{RESET}.")
        format = "lyrics"

    genres = ["none", "country", "latin", "italian", "dance", "phonk", "pop", "rap", "alternative", "emo", "rock", "edm", "trap", "electronic"]

    # Checks if a valid genre was provided.
    if genre.lower() not in genres:
        print(f"{YELLOW}![GENRE]{RESET} Defaulted to {BOLD}'None'{RESET}.")
        genre = "none"

    # Checks if TikTok was provided, otherwise it defaults to false.
    if len(tiktok) == 0:
        print(f"{YELLOW}![TIKTOK]{RESET} Defaulted to {BOLD}'False'{RESET}.")

    # Prints a new line
    print("")

    # API endpoint for tag generation
    url = "https://tags.notnick.io/api/v1/generate"

    # Build the payload with provided inputs (fallbacks to "none" if empty)
    payload = {
        "tiktok": "true" if tiktok.lower() in ["true", "t"] else "false",
        "shuffle": "true" if shuffle.lower() in ["true", "t", "yes", "y"] else "false",
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

    # Send GET request to API with an animated spinner while we wait.
    with Spinner("Generating tags"):
        response = requests.get(url, params=payload, headers=headers)

    # If request succeeded
    if response.status_code == 200:
        data = response.json()

        # Extract tags from JSON response
        tags = data["removedTags"]

        print(f"{GREEN}{BOLD}✓ Generated tags{RESET} {GRAY}({data['length']} characters){RESET}\n")
        print(f"{CYAN}{tags}{RESET}\n")

        # Print the response ID
        print(f"{GRAY}Response: {data['responseId']}{RESET}")

        # Optionally save all metadata to a text file.
        if metadata.lower() in ["true", "t", "yes", "y"]:
            filename = write_metadata(data)
            print(f"{GREEN}✓ Saved metadata to{RESET} {BOLD}{filename}{RESET}")

    # If request failed, show error
    else:
        error_message = response.json()["error"]
        print(f"{RED}{BOLD}✗ Error:{RESET} {error_message}")


# Call the generate method
generate(artist, title, features, channel_name, tiktok, format, genre, verse, shuffle, metadata)

