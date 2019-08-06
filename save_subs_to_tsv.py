import argparse
import logging
import os
import time

from reddit_scraper_lib import RedditFetcher
from secret import SECRET, CLIENT, APPNAME


def save_tsv_for_sub(sub, args):
    search_str = '%s_%s-%s_%d' % (sub, args.sort, args.time_range, args.num_posts)
    logging.debug('Searching %s...' % search_str)
    res = reddit.search(sub, sort_order=str(args.sort), time_filter=args.time_range, limit=args.num_posts, content_type='media')
    post_df = res.to_df()
    logging.info('Reddit returned %d media posts from %s' % (len(post_df), sub))
    output_f = os.path.join(args.output_dir, '%s_%d.tsv' % (search_str, time.time()))
    post_df.to_csv(output_f, header=True, index=True, sep='\t')
    return output_f


if __name__ == "__main__":
    """
    # Example: Dump top all time
    python run_scraper.py \
        --subs=futurebeats,hiphop,hiphopheads,psychedelicrock,rap,indieheads,indie,indierock,treemusic,realdubstep,chillmusic,jazz,blues,triphop,lofihiphop,shoegaze,futuregarage,hiphop101,90shiphop,reggae,chillwave,futurebass,futurefunkairlines,nudisco,jazznoir,jazzyhiphop \
        --sort=top  --time_range=all -n=1000 --debug

    """
    parser = argparse.ArgumentParser(description="Scrape media from subreddits")
    parser.add_argument("--subs", type=str, help="Comma seperated list of subreddit names")
    parser.add_argument("--sort", "-s", default='hot', type=str,
                        help="Reddit sort order, can be: hot, top, new, rising, random or controversial.")
    parser.add_argument("--time_range", "-t", default='month', type=str,
                        help="Reddit time range, can be 'all', 'day', 'hour', 'month', 'week', 'year'.")
    parser.add_argument("--num_posts", "-n", default=20, type=int,
                        help="Max num posts to query (max 1000).")
    parser.add_argument("--output_dir", "-o", default='logs/', type=str,
                        help="Folder to files and logs save to.")
    parser.add_argument("--debug", action="store_true", help="Print debug info")
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
    output_files = [save_tsv_for_sub(sub, args) for sub in args.subs]
    print(output_files)
