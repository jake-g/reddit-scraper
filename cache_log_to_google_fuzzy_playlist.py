import os

from reddit_scraper_lib import log_files_in_folder

cache_dir = 'logs/gmusic_lists/'
dl_fold = 'D:\Reddit_Music_Scrape'
blacklist_search_str = ['_Track_Collections']

for search_str in os.listdir(dl_fold):
    if len(search_str.split('_')) == 3 and search_str not in blacklist_search_str:
        download_f = os.path.join(dl_fold, search_str)
        log_f = os.path.join(cache_dir, '%s_files.csv' % search_str)
        log_files_in_folder(log_f, download_f)
