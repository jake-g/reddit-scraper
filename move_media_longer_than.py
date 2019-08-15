import os
import time

from mutagen.mp3 import MP3

# import eyed3

DRY_RUN = False
DEBUG = True
max_track_length = 15 * 60
rootdir = 'D:/Reddit_Music_Scrape/'

unknown_dir = os.path.join(rootdir, '_Track_Collections/unknown/')
album_dir = os.path.join(rootdir, '_Track_Collections/albums/')
album_strings = ['full album', 'ep', 'mixtape', 'album', 'full tape']
mix_dir = os.path.join(rootdir, '_Track_Collections/mixes_performances/')
mix_strings = ['boiler room', 'compilation', 'mix', 'concert', 'live', 'dj set', 'tiny desk', 'fabriclive']
spam_dir = os.path.join(rootdir, '_Track_Collections/spam/')
spam_strs = ['eating spicy wings', 'twitch']


def move_file(src_f, dest_f, dry=False, verbose=False):
    if verbose: print(src_f, ' --> ', dest_f)
    if dry: return
    dest_dir = os.path.dirname(dest_f)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    os.rename(src_f, dest_f)


for subdir, dirs, files in os.walk(rootdir):
    for f in files:
        f_str = f.lower()
        if f_str.endswith('mp3'):
            fpath = os.path.join(subdir, f)
            t0 = time.time()
            audio = MP3(fpath)
            if audio.info.length > max_track_length:
                if any(x.lower() in f_str for x in spam_strs):
                    move_file(fpath, fpath.replace(rootdir, spam_dir), dry=DRY_RUN, verbose=DEBUG)
                elif any(x.lower() in f_str for x in album_strings):
                    move_file(fpath, fpath.replace(rootdir, album_dir), dry=DRY_RUN, verbose=DEBUG)
                elif any(x.lower() in f_str for x in mix_strings):
                    move_file(fpath, fpath.replace(rootdir, mix_dir), dry=DRY_RUN, verbose=DEBUG)
                else:
                    move_file(fpath, fpath.replace(rootdir, unknown_dir), dry=DRY_RUN, verbose=DEBUG)
