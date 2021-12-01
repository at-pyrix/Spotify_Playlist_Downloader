# Importing libraries
import requests
import keyboard
import subprocess
import playsound
from Refresh_Token import Refresh
from simplejson.errors import JSONDecodeError
from pytube import *
import urllib
from colorama import Fore as fc
import os
from win10toast import ToastNotifier
import re
from threading import Thread
from itertools import cycle
from time import time, sleep
from sys import stdout

notify = ToastNotifier()
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


def play():
    import playsound
    playsound.playsound('Sound/notification.wav')


def notifypls():
    message = f"Your Playlist {playlist_Name} has been downloaded.\nSaved in \'{os.path.join('Music',playlist_Name)}\'"

    notify.show_toast(title="Download Complete ✔️", msg=message,
                      icon_path="images/spotify.ico", duration=4, threaded=True)


def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               "]+", flags=re.UNICODE)
    return (emoji_pattern.sub(r'', text))


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
    f"\nEnter your Spotify Playlist URL/Embed Code/URI: \n{fc.CYAN}>>{fc.GREEN} ")
# Removes the url part, so we are only left with the Playlist ID
if "iframe src" in playlist_uri:
    playlist_id = playlist_uri.split(
        'https://open.spotify.com/embed/playlist/')[1].split('" width')[0]
elif "https://open.spotify.com/playlist/" in playlist_uri:
    playlist_id = playlist_uri.split(
        'https://open.spotify.com/playlist/')[1].split('?')[0]
else:
    playlist_id = playlist_uri.replace("spotify:playlist:", "").strip()

print(fc.RESET)


url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"


# Generates a new access token from Refresh Token
# See: https://developer.spotify.com/documentation/general/guides/authorization/, https://developer.spotify.com/documentation/web-api/quick-start/
token = Refresh().refresh()


# Passing the headers to the url

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
        f"\r{fc.LIGHTRED_EX}mError {data['error']['status']}: {data['error']['message']}{fc.RESET}")

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
    file = ys[-1].download(output_path=os.path.join('Music',playlist_Name))
    downloaded_files.append(file)


# Appends the songs with the artist name in a dictionary nested inside an array
for i in items:
    track = i['track']['name']
    artist = i['track']['album']['artists'][0]['name']
    songs.append({'name': track, 'artist': artist})

print(f"{fc.YELLOW}Total Songs - {len(songs)}{fc.RESET}\n")

playlist_Name = input(
    f"Enter the name of the Playlist: {fc.CYAN}\n>>{fc.GREEN} ")
playlist_Name.replace(" ", "_").encode("ascii", "ignore").decode().strip()
print("\n")


yt_links = []


start = time()

# Downloads all the songs from the playlist
counter = 4

view = "Basic"


def listen_to_keyboard():
    while not timeOver:
        if keyboard.is_pressed('pause'):
            global view
            view = "Advanced"
            break
        pass


timeOver = False
for i in range(1, 4):
    eventListener = Thread(target=listen_to_keyboard).start()
    print(f"{fc.LIGHTCYAN_EX}Download Starting in {counter-1} {fc.LIGHTBLACK_EX}Press Pause Break to show advanced view{fc.RESET}", end="\r")
    counter -= 1
    sleep(1)
timeOver = True

if view == "Advanced":
    print(f"\r{fc.CYAN}>> {fc.LIGHTGREEN_EX}Advanced View {fc.RESET}"+" "*60, end="\r")
else:
    print(" "*90, end="\r")
sleep(0.7)
print("                                                        ", end="\r")

songCounter = 1

for i in songs:
    done = False
    if "Various Artists" not in i['artist']:
        search_query = F"{i['name']}{i['artist']} song"
        search_query = remove_emojis(search_query)
    else:
        search_query = i['name'] + " song"
        search_query = remove_emojis(search_query)

    arguments = []
    if view == "Advanced":
        arguments.append(f'Downloading: {fc.RESET}{i["name"]}')
    else:
        arguments.append(
            f"{fc.CYAN}Downloaded {songCounter-1} of {len(songs)}{fc.RESET}")

    t = Thread(target=animate, args=arguments)
    t.start()
    song_url = urlFinder(search_query.encode("ascii", "ignore").decode())
    try:
        download(song_url)
    except Exception:
        done = True
        if view == "Advanced":
            print(
                f'\r{fc.RED}❌  Failed to Download: {fc.RESET}{i["name"]} by {i["artist"]} \n')
        else:
            songCounter += 1
    else:
        done = True
        if view == "Advanced":
            print(
                f'\r{fc.CYAN}[✓]{fc.GREEN} Downloaded: {fc.RESET}{i["name"]} by {i["artist"]}\n')

    done = True
    t.join()
    songCounter += 1
print(f'\r{fc.CYAN}[✓]{fc.GREEN} Downloaded Complete {fc.RESET}\n')


notifypls()
play()

print(fc.LIGHTBLACK_EX +
      f"\n\nThe files Downloaded are in a video format. Would you like to convert them to Mp3? [Y/n]")
convert_to_mp3 = input(fc.CYAN + "\n>> " + fc.GREEN)
print(fc.RESET)

# Converts into mp3
if convert_to_mp3.lower() == "y" or convert_to_mp3.lower() == "yes":
    parent_dir = os.path.join('Music',playlist_Name)
    done = False
    tt = Thread(target=animate, args=("Converting To Mp3",))
    tt.start()
    # Converting into mp3
    for file in downloaded_files:
        file = remove_emojis(file)
        new_filename = os.path.splitext(file)[0]+".mp3"
        new_filename = remove_emojis(new_filename)
        already_exists = False

        for i in os.listdir(parent_dir):
            i = os.path.join(os.getcwd(), parent_dir, i)
            i = remove_emojis(i)
            if new_filename == i:
                already_exists = True
                break

        if already_exists:
            os.remove(file.strip())
            continue
        else:
            try:
                subprocess.getoutput(
                    f'ffmpeg -i "{remove_emojis((os.path.join(file)).strip())}" "{remove_emojis(os.path.join(new_filename)).strip()}" '
                )
                os.remove(file.strip())
            except:
                pass

    done = True
    tt.join()
    print(fc.CYAN+'\r[✓] '+fc.GREEN+'Successfully Converted'+fc.RESET)
    notify.show_toast(title="Coversion Complete ✅", msg="Successfully Converted the Playlist to Mp3",
                      icon_path="images/spotify.ico", duration=4, threaded=True)
    play()
sleep(2)
