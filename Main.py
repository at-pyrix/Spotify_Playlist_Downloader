# Importing libraries
import requests
from Refresh_Token import Refresh
from simplejson.errors import JSONDecodeError
from pytube import *
import urllib
from colorama import Fore as fc
import os
import re
from threading import Thread
from itertools import cycle
from time import time, sleep
from sys import stdout


error = False
done = False

def animate(message):
    for c in cycle([f'⡿ {message}', f'⣟ {message}', f'⣯ {message}', f'⣷ {message}', f'⣾ {message}', f'⣽ {message}', f'⣻ {message}', f'⢿ {message}']):
        if error:
            print(f'\r{" "*len(message) }')
            break
        elif done:
            break
        stdout.write('\r' + fc.CYAN + c)
        stdout.flush()
        sleep(0.06)



def urlFinder(search_keyword):
    # Replace the empty spaces to %20 for the youtube URL
    # Searching youtube for the keyword
    search_keyword = search_keyword.strip().replace(" ", "%20")
    url_base = "https://www.youtube.com/results?search_query=" + search_keyword
    html = urllib.request.urlopen(url_base)

    try:
        # Finds all the links to the videos on the page using the base URL
        # video_ids[0] returns the first video on the page
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        url = ("https://www.youtube.com/watch?v=" + video_ids[0])

    except IndexError:
        # Used to colorize the output
        print(f"\r{fc.LIGHTRED_EX}No Video Found :/{fc.RESET}")
        url = None

    return url


playlist_uri = input(
    f"\nEnter your Spotify Playlist URI: \n{fc.CYAN}>>{fc.GREEN} ")
print("\u001B[0m")

# Removes the "spotify:playlist" part from the URI so we are only left with the Playlist ID
playlist_id = playlist_uri.replace("spotify:playlist:", "").strip()

url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

# * Your OAuth Token
# ? Get it from https://developer.spotify.com/console/get-playlist/?playlist_id=&market=&fields=&additional_types=
# ? Click GET TOKEN > Request Token
# Generates a new access token from Refresh Token
# See: https://developer.spotify.com/documentation/general/guides/authorization/, https://developer.spotify.com/documentation/web-api/quick-start/
token = Refresh().refresh()


# Passing the headers to the url which translates to:
# `curl -X "GET" "https://api.spotify.com/v1/playlists/" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {access_token}`

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}',
}

response = requests.get(url, headers=headers)

try:
    data = response.json()
except JSONDecodeError:
    error = True
    print(fc.LIGHTRED_EX+"Invalid Spotify PlayList URI"+fc.RESET)
    exit()


# Prints the error if it get's an error
try:
    print(
        f"\r\u001B[31mError {data['error']['status']}: {data['error']['message']}\u001B[0m")

except KeyError:
    pass

else:
    error = True
    exit()

items = data['items']

songs = []

downloaded_files = []

# Downloads the videos from youtube 
# Saves the path it into a list
def download(url):
    yt = YouTube(urlFinder(url))
    ys = yt.streams.filter(only_audio=True)
    file = ys[-1].download(output_path=playlist_Name)
    downloaded_files.append(file)


# Appends the songs with the artist name in a dictionary nested inside an array
for i in items:
    track = i['track']['name']
    artist = i['track']['album']['artists'][0]['name']
    songs.append({'name': track, 'artist': artist})

print(f"{fc.YELLOW}Total Songs - {len(songs)}{fc.RESET}\n")

playlist_Name = input(
    f"Enter the name of the Playlist: {fc.CYAN}\n>>{fc.GREEN} ")
print("\n")


yt_links = []

Thread(target=animate, args=('Downloading Playlist ',)).start()
start = time()

# Downloads all the songs from the playlist
for i in songs:
    if "Various Artists" not in i['artist']:
        search_query = F"{i['name']}{i['artist']}"
    else:
        search_query = i['name'] + " song"
    # Get's the url for the song
    song_url = urlFinder(search_query)
    download(song_url)

done = True
print(
    f'\r{fc.GREEN}✔️  All Songs Downloaded in \u001B[33m{str (round(time() - start, 2))}s')

print(fc.LIGHTBLACK_EX +
      f"\n\nThe files Downloaded are in a video format. Would you like to convert them to Mp3? [Y\\n]")
convert_to_mp3 = input(fc.CYAN + "\n>> " + fc.GREEN)
print(fc.RESET)

# Converts into mp3
if "y" in convert_to_mp3.lower():
    parent_dir = playlist_Name
    Thread(target=animate, args=("Converting To Mp3",)).start()
    os.system(
        f'py Video2Mp3.py "{downloaded_files}" "{parent_dir}"')
    done = True
    print(fc.GREEN+'\rSuccessfully Converted'+fc.RESET)
else:
    pass

# spotify:playlist:49H2za6xCqCiITkfVHcAnk

# spotify:playlist:5mc4thG3yqdzuJErdmjUL8
# this is *our*
