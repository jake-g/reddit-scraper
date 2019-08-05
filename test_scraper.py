from secret import SECRET, CLIENT, APPNAME
from reddit_scraper_lib import RedditFetcher, RedditPost

import logging
logging.basicConfig(level=logging.DEBUG)

def get_n_hot_posts_from_each_subreddit(subreddits, reddit_api, n=20):
    logging.info('Fetching a total of %d posts from subreddits:\n\t%s' % (n, subreddits))
    res = reddit_api.search('+'.join(subreddits), sort_order='hot', time_filter='all', limit=n, content_type='media')
    return res.to_df(columns=['title', 'author',  'youtube_id', 'is_media'])


if __name__ == "__main__":

    reddit = RedditFetcher(CLIENT, SECRET, APPNAME)
    logging.debug(reddit)
    subs = ['psychedelicrock', 'indie_rock', 'hiphop', '90shiphop', 'futurebeats', 'treemusic']
    post_df = get_n_hot_posts_from_each_subreddit(subs, reddit, n=20)
    logging.info(post_df)