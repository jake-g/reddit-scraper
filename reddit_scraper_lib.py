import glob
import logging
import os
from urllib.parse import urlparse, parse_qs

import pandas as pd
import praw

from audio_scrape import download_track, valid_url


class Playlist(object):
    """Object containing Playlist of Posts."""

    def __init__(self, name, post_list, url=None):
        self.name = name  # playlist name str
        self.url = url  # optional url str to reproduce playlist
        self.posts = post_list  # list of Post objects

    def to_df(self, columns=None):
        """Convert a list of Post objects into a Pandas Dataframe.

        Returns:
          Post Pandas Dataframe.
        """
        df = pd.DataFrame([p.__dict__ for p in self.posts])
        if columns:
            return df[columns]
        else:
            return df

    def add_to_db(self, db, collection='playlists'):
        """Add playlist reference document to firebase playlist db collection.

        sets (overwrites) a playlist document

        Args:
          db: (firebase_admin obj) authenticated firebase db

        Returns:
          Result json from firebase.
        """
        # TODO attach db to self
        # Add playlist entry
        db.collection(collection).document(self.name).set({
            'url': self.url,
            'ids': [p.youtube_id for p in self.posts]
        })
        # Add individual song entries
        self.add_songs_to_db(db)

    def add_songs_to_db(self, db):
        """Add playlist songs document to firebse song db collection.

        Also adds option metadata to other collections (like reddit)

        Only works for songs with youtube_ids

        Args:
          db: (firebase_admin obj) authenticated firebase db

        Returns:
          Result json from firebase.
        """
        batch = db.batch()
        for p in self.posts:
            if p.youtube_id:
                song = p.__dict__
                song_entry = db.collection('songs').document(p.youtube_id)
                #         reddit_entry = db.collection('reddit_posts').document(p.youtube_id)
                if 'reddit' in song:
                    # key reddit meta with sub name in case it appears in multiple subs
                    reddit_post = song.pop('reddit')
                    song['r/{}'.format(reddit_post['sub'])] = reddit_post
            batch.set(song_entry, song, merge=True)
        return batch.commit()

    def search(self, q, limit=100, content_type=None, name=None):
        """Search based on query with filtering.

        Args:
          q: (str) subreddit name, multiple subreddits need to split with +: 'sub1+sub2'
          limit: (optional int) number of results to return from 0 to 50.
          name: (optional str) name for Playlist

        Returns:
          Playlist containing Posts from the query.

        """
        pass

    def __str__(self):
        return 'Playlist: %s, containing %s posts from %s' % (self.name.title(), len(self.posts), self.url)


class Post(object):
    """Object containing Playlist of Posts."""

    def __init__(self, submission):
        self.youtube_id = None
        self.title = None
        self.url = None
        self.author = None
        self.timestamp = None  # TODO make sure it is in UTC unix
        self.description = None
        self.likes = 0
        self.dislikes = 0
        self.num_comments = 0
        self.num_plays = 0
        self.is_media = False
        self.thumb_url = None
        self.create(submission)

    def create(self, submission):
        """Parse submission set post fields.

        Args:
          submission: (object) response from query.
        """
        pass

    def update_post(self, updated_post):
        # TODO write a way to update self with new or overwritten fields
        pass

    def __str__(self):
        return 'Title: %s, ID: %s containing: %s' % (self.title, self.youtube_id, self.__dict__)


class Fetcher(object):
    """Object to contain api wrapper for fetching data

    Put any api request query methods in here.
    """

    def __init__(self):
        self.api = None  # object containing authenticated api session
        self.provider = 'unknown'  # name of api provider

    def __str__(self):
        return '%s Fetcher with API instance: %s' % (self.provider.title(), self.api)


class RedditFetcher(Fetcher):
    """Connect to Reddit readonly api"""

    def __init__(self, client, secret, app_name, service='reddit'):
        """Set self.api as readonly PRAW reddit object.

        Args:
          client: (obj) Reddit client id.
          secret: (str) Reddit secret key.
          app_name: (str) Reddit app name.

        Raises:
          ValueError: if the instance is not read only.
        """
        super().__init__()
        reddit = praw.Reddit(client_id=client, client_secret=secret, user_agent=app_name)
        if not reddit.read_only:
            raise ValueError('Only need read only access!')
        self.api = reddit
        self.provider = service

    def search(self, q, sort_order='hot', time_filter='all', limit=100, content_type=None, name=None):
        """Query reddit for one or multiple subreddits.

        Args:
          q: (str) subreddit name, multiple subreddits need to split with +: 'sub1+sub2'
          sort_order: (optional str) either 'hot' (default), 'new', 'rising', 'random', 'top' or 'controversial'.
          time_filter: (optional str) either 'all' (default), or 'day', 'hour', 'month', 'week' or 'year'.
          limit: (optional int) number of results to return from 0 to 50.
          content_type: (optional str) only 'media' supported, otherwise None will contain non-media posts too
          name: (optional str) name for Playlist

        Returns:
          Playlist containing Posts from the query.

        """
        _subs = self.api.subreddit(q)
        url = 'https://www.reddit.com/' + _subs._path
        assert time_filter in ['all', 'day', 'hour', 'month', 'week', 'year']
        if sort_order == 'hot':
            post_list = [RedditPost(p) for p in _subs.hot(limit=limit)]
        elif sort_order == 'new':
            post_list = [RedditPost(p) for p in _subs.new(limit=limit)]
        elif sort_order == 'rising':
            post_list = [RedditPost(p) for p in _subs.rising(limit=limit)]
        elif sort_order == 'random':
            post_list = [RedditPost(p) for p in _subs.posts.random(limit=limit)]
        elif sort_order == 'top':
            post_list = [RedditPost(p) for p in _subs.top(time_filter=time_filter, limit=limit)]
        elif sort_order == 'controversial':
            post_list = [RedditPost(p) for p in _subs.controversial(time_filter=time_filter, limit=limit)]
        else:
            raise ValueError('Sort_order must be: hot, new, rising, random, top or controversial')
        if content_type is 'media':
            post_list = [p for p in post_list if p.is_media]

        if name is None:
            name = 'Subreddits (%s): %s' % (sort_order, q.replace('+', ' '))

        return Playlist(name, post_list, url=url)


class RedditPost(Post):
    """Object containing a reddit post.

    Additional fileds to Post defined in init.
    """

    def __init__(self, submission):
        self.reddit = {}  # extra reddit metadata
        Post.__init__(self, submission)

    def create(self, submission):
        """Parse Reddit post response and set post fields.

        Args:
          submission: (object) response from PRAW reddit query.

        """
        self.url = submission.url
        self.timestamp = submission.created_utc  # TODO standardize timestamp
        self.num_comments = submission.num_comments
        self.likes = submission.ups
        self.dislikes = submission.downs
        self.reddit['source'] = submission.domain
        self.reddit['num_comments'] = submission.num_comments
        self.reddit['score'] = submission.score
        self.reddit['sub'] = submission.subreddit.display_name
        self.reddit['author'] = getattr(submission.author, 'name', '')  # can be unset
        self.reddit['title'] = submission.title
        self.reddit['url'] = 'https://www.reddit.com' + submission.permalink

        post_media = submission.media
        if post_media is not None and self.reddit['source'] in ['soundcloud.com', 'youtube.com']:
            media = post_media['oembed']
            self.is_media = True
            self.author = media.get('author_name', '')
            self.description = media.get('description', '')
            self.title = media.get('title', submission.title)
            self.thumb_url = media.get('thumbnail_url', '')
            if self.reddit['source'] == 'youtube.com':
                self.youtube_id = get_yt_video_id(submission.url)

        # TODO set the following:
        self.num_views = None  # TODO set this from soundcloud or youtube somehow


def get_yt_video_id(url):
    """Returns Video_ID extracting from the given url of Youtube

    Examples of URLs:
      Valid:
        'http://youtu.be/_lOT2p_FCvA',
        'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
        'http://www.youtube.com/embed/_lOT2p_FCvA',
        'http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US',
        'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
        'youtube.com/watch?v=_lOT2p_FCvA',

      Invalid:
        'youtu.be/watch?v=_lOT2p_FCvA',
    """

    if url.startswith(('youtu', 'www')):
        url = 'http://' + url

    query = urlparse(url)

    if 'youtube' in query.hostname:
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        elif query.path.startswith(('/embed/', '/v/')):
            return query.path.split('/')[2]
    elif 'youtu.be' in query.hostname:
        return query.path[1:]
    else:
        raise ValueError


def title_similarity_score(str1, str2):
    """Jaccard similarity score of two titles, between 0 and 100 where 100 is identical.

    Tokens in `ignore_set` are ignored, tokens in `trump_set` must be in both sets

    Examples:
      title_similarity_score('Jake garrison - ok', 'jake garrison by ok') --> 60
      title_similarity_score('Jake garrison - ok', 'jke garison by ok') --> 14
      title_similarity_score('Jake garrison - ok', 'jake garrison - ok') --> 100
      title_similarity_score('Jake garrison - ok', 'jake garrison - ok (Official Video)') --> 100
      title_similarity_score('Jake garrison - ok (remix)', 'jake garrison - ok') --> 0 # trump

    """
    # TODO unit test

    remove = ['(', ')', '-', '|', ':', ';', '[', ']', '<', '>', 'fresh', 'official', 'video', 'music', 'by', 'lyrics']
    trump_set = set(['remix', 'edit', 'live', 'cover', 'mashup', 'mix'])
    str1 = str1.lower()
    str2 = str2.lower()
    for c in remove:
        str1 = str1.replace(c, ' ')
        str2 = str2.replace(c, ' ')
    str1_toks = set(str1.split(' '))
    str2_toks = set(str2.split(' '))
    # when str1 or str2 has a trump_set tok, but the other doesnt, score should be 0
    non_overlap = str1_toks.symmetric_difference(str2_toks)
    if len(non_overlap.intersection(trump_set)) > 0:
        return 0
    else:
        overlap = str1_toks.intersection(str2_toks)
        jaccard_score = int(100 * float(len(overlap)) / (len(str1_toks) + len(str2_toks) - len(overlap)))
        return jaccard_score


def download_url(url, opts):
    class logger(object):
        def debug(self, msg):
            logging.debug(msg)
            pass

        def warning(self, msg):
            logging.warning(msg)

        def error(self, msg):
            logging.error(msg)

    try:
        if valid_url(url):
            download_track(str(url), opts, logger=logger())
        else:
            logging.warning('Skipping invalid url: %s' % url)
    except Exception as e:
        logging.error('Failed to download url: %s...\n%s' % (url, e))


def check_cache(search_str, cache_dir):
    logging.debug('Looking in cache (%s) for %s...' % (cache_dir, search_str))
    cached_queries = glob.glob(os.path.join(cache_dir, search_str + '*'))
    logging.debug('Found %d cached entries for %s...\n Entries: %s' % (len(cached_queries), search_str, cached_queries))
    last_timestamp = 0
    newest_cache_entry = cached_queries[0]
    for res in cached_queries:
        name, ext = os.path.splitext(os.path.basename(res))
        sub, search, num, timestamp = name.split('_')
        if int(timestamp) > last_timestamp:
            newest_cache_entry = res
            last_timestamp = int(timestamp)

    post_df = pd.read_csv(newest_cache_entry, sep='\t', index_col=0)
    logging.debug('Loaded %s as post df with %d entries' % (search_str, len(post_df)))
    return post_df, newest_cache_entry
