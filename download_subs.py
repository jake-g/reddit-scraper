import argparse
import logging
import os
import time
from pprint import pprint

from reddit_scraper_lib import RedditFetcher, check_cache, download_url
from secret import SECRET, CLIENT, APPNAME

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
            'preferredquality': '0'
        },
        {
            'key': 'EmbedThumbnail',
            'already_have_thumbnail': False
        }
    ]
}


def download_all_top_for_sub(sub, args):
    search_str = '%s_%s-%s_%d' % (sub, args.sort, args.time_range, args.num_posts)
    if args.use_cache:  # Load previous query.
        post_df, output_f = check_cache(search_str, args.cache_dir)
    else:  # Query reddit for all top posts in sub.
        logging.debug('Searching %s...' % search_str)
        res = reddit.search(sub, sort_order=args.sort, time_filter=args.time_range,
                            limit=args.num_posts, content_type='media')
        post_df = res.to_df()
        logging.info('Reddit returned %d media posts from %s' % (len(post_df), sub))
        if args.cache_dir:
            output_f = os.path.join(args.cache_dir, '%s_%d.tsv' % (search_str, time.time()))
            logging.info('Saving %s to cache: %s' % (sub, output_f))
            post_df.to_csv(output_f, header=True, index=True, sep='\t')

    if args.download_posts:
        logging.info('Attempting to download %d posts...' % len(post_df))
        download_folder = os.path.join(args.download_dir, search_str)
        dl_opts['outtmpl'] = download_folder + '/' + '%(title)s.%(ext)s'
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        for i, url in enumerate(post_df['url']):
            logging.info('(%d/%d)' % (i + 1, len(post_df)))
            download_url(url, dl_opts)


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
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Debug logging enabled...')
    else:
        logging.basicConfig(level=logging.INFO)

    reddit = RedditFetcher(CLIENT, SECRET, APPNAME)
    logging.debug(reddit)

    args.subs = args.subs.split(',')
    if args.num_posts > 1000:
        logging.warning('num_posts too large (%d), Reddit only makes a max of 1000 posts available' % args.num_posts)
    logging.info('Processing %d subreddits' % len(args.subs))
    [download_all_top_for_sub(sub, args) for sub in args.subs]
