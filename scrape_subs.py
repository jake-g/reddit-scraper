import argparse
import glob
import logging
import os
import time

from secret import APPNAME
from secret import CLIENT
from secret import SECRET

from reddit_scraper_lib import check_cache
from reddit_scraper_lib import download_url
from reddit_scraper_lib import log_files_in_folder
from reddit_scraper_lib import RedditFetcher

# Any subreddit yielding fewer posts than this will not have a .tsv file saved.
MINIMUM_ENTRIES_TO_SAVE = 3

dl_opts = {  # Settings for youtube-dl
    'format': 'bestaudio/best',
    'forcejson': True,
    'outtmpl': './downloads/%(title)s.%(ext)s',
    'writethumbnail': True,
    'postprocessors': [
        {
            'key': 'MetadataFromTitle',
            'titleformat': "%(artist)s - %(title)s"
        },
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        },
        {
            'key': 'EmbedThumbnail',
            'already_have_thumbnail': False
        }
    ]
}


def scrape_sub(sub, args):
    # Sanitize sub name (replace underscores with dashes for filename consistency)
    clean_sub_name = sub.replace('_', '-')
    search_str = '%s_%s-%s_%d' % (clean_sub_name, args.sort, args.time_range, args.num_posts)

    # AUTO-RESUME LOGIC
    # Check if a file matching this search_str already exists in the cache folder.
    # We use glob because the existing files have a timestamp suffix we can't predict.
    if args.use_cache and os.path.exists(args.cache_dir):
        # Pattern: logs/SubName_top-all_1000_*.tsv
        search_pattern = os.path.join(args.cache_dir, search_str + '*.tsv')
        existing_files = glob.glob(search_pattern)

        if existing_files:
            logging.info(f"Skipping scrape for '{sub}': Found existing log {existing_files[0]}")

            # If we are NOT downloading, we are done with this sub.
            if not args.download_posts:
                return

            # If we ARE downloading, we assume check_cache will load the existing file below.
            # But usually, if you just want to update the log index, you can return here.

    if args.use_cache:  # Load previous query.
        cached_data = check_cache(search_str, args.cache_dir)
    else:
        cached_data = None

    if cached_data:
        post_df, output_f = cached_data
    else:
        # CRASH PROTECTION (Try/Except)
        try:
            logging.debug('Searching %s...' % search_str)
            # Query reddit for all top posts in sub.
            res = reddit.search(sub, sort_order=args.sort, time_filter=args.time_range,
                                limit=args.num_posts, content_type='media')
            post_df = res.to_df()
            logging.info('Reddit returned %d media posts from %s' % (len(post_df), sub))

            # Check if the number of posts meets our minimum threshold before saving.
            if len(post_df) < MINIMUM_ENTRIES_TO_SAVE:
                logging.warning(
                    f"Subreddit '{sub}' yielded only {len(post_df)} posts. "
                    f"Skipping TSV file creation to avoid clutter (threshold is {MINIMUM_ENTRIES_TO_SAVE})."
                )
            elif args.cache_dir:
                # This block only runs if we have enough entries AND a cache dir is specified.
                if not os.path.exists(args.cache_dir):
                    os.makedirs(args.cache_dir)

                output_f = os.path.join(args.cache_dir, '%s_%d.tsv' % (search_str, time.time()))
                # Improved log message includes the count
                logging.info(f'Saving {len(post_df)} posts from {sub} to cache: {output_f}')
                post_df.to_csv(output_f, header=True, index=True, sep='\t')

        except Exception as e:
            # This catches the PRAW/Network error for missing sub
            logging.error(f"CRITICAL ERROR scraping subreddit '{sub}': {e}")
            logging.error("Skipping this subreddit and continuing...")
            return

    # DOWNLOAD LOGIC
    if args.download_posts:
        if post_df is None or len(post_df) == 0:
            logging.warning(f"No posts found to download for {sub}")
            return

        logging.info('Attempting to download %d posts...' % len(post_df))
        download_folder = os.path.join(args.download_dir, search_str)
        dl_opts['outtmpl'] = download_folder + '/' + '%(title)s.%(ext)s'
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        for i, url in enumerate(post_df['url']):
            logging.info('(%d/%d) %s' % (i + 1, len(post_df), url))
            try:
                download_url(url, dl_opts)
            except Exception as e:
                logging.error(f"Failed to download {url}: {e}")

        if args.log_filenames:
            log_f = os.path.join(args.cache_dir, '%s_files.csv' % search_str)
            log_files_in_folder(log_f, download_folder)

if __name__ == "__main__":
    """
    python run_scraper.py \
        --subs=futurebeats,hiphop,hiphopheads,psychedelicrock,rap,indieheads,indie,indierock,treemusic,realdubstep,chillmusic,jazz,blues,triphop,lofihiphop,shoegaze,futuregarage,hiphop101,90shiphop,reggae,chillwave,futurebass,futurefunkairlines,nudisco,jazznoir,jazzyhiphop \
        --sort=top \
        --time_range=all \
        -n=1000 \
        --debug \
        --use_cache \
        --download_posts

    """
    parser = argparse.ArgumentParser(description="Scrape media from subreddits")
    parser.add_argument("--subs", type=str, help="Comma seperated list of subreddit names")
    parser.add_argument("--sort", "-s", default='hot', type=str,
                        help="Reddit sort order, can be: hot, top, new, rising, random or controversial.")
    parser.add_argument("--time_range", "-t", default='month', type=str,
                        help="Reddit time range, can be 'all', 'day', 'hour', 'month', 'week', 'year'.")
    parser.add_argument("--num_posts", "-n", default=20, type=int,
                        help="Max num posts to query (max 1000).")
    parser.add_argument("--cache_dir", "-c", default='logs/', type=str,
                        help="Folder cached queries save to.")
    parser.add_argument("--download_dir", "-o", default='downloads/', type=str,
                        help="Folder media files save to.")
    parser.add_argument("--debug", "-d", action="store_true", help="Print debug info")
    parser.add_argument("--use_cache", action="store_true", help="Load Reddit results from cached_file.")
    parser.add_argument("--download_posts", action="store_true", help="Downloads the media file.")
    parser.add_argument("--log_filenames", action="store_true", help="Saves a log of the filenames.")
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Debug logging enabled...')
    else:
        logging.basicConfig(level=logging.INFO)

    reddit = RedditFetcher(CLIENT, SECRET, APPNAME)
    logging.debug(reddit)

    # Split by comma, Strip whitespace, Convert to .lower() so filenames are always consistent
    args.subs = [s.strip().lower() for s in args.subs.split(',')]

    if args.num_posts > 1000:
        logging.warning('num_posts too large (%d), Reddit only makes a max of 1000 posts available' % args.num_posts)
    logging.info('Processing %d subreddits' % len(args.subs))
    [scrape_sub(sub, args) for sub in args.subs]
