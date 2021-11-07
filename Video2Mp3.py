import sys
import os 
import subprocess

downloaded_files = sys.argv[1]
parent_dir = sys.argv[2]

downloaded_files = downloaded_files.replace("'","").replace("[","").replace("]","").strip().replace("\\\\","\\").split(',')


for file in downloaded_files:
    print("File "+file)
    new_filename = os.path.splitext(file)[0]+".mp3"
    already_exists = False
    print("New FileName: "+new_filename)

    for i in os.listdir(parent_dir):
        i = os.path.join(os.getcwd(),parent_dir, i)
        if new_filename == i:
            print("Already Existing File ", i)
            already_exists = True
            break

    if already_exists:
        continue
    else:
        print(
            f'ffmpeg -i "{os.path.join(file)}" "{os.path.join(new_filename)}"')
        os.system(
        f'ffmpeg -i "{(os.path.join(file)).strip()}" "{(os.path.join(new_filename)).strip()}"'
        )
        os.remove(file.strip())

