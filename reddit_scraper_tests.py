"""Unit tests for reddit_scraper_lib.py."""

import unittest
from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import reddit_scraper_lib


class TestRedditScraperUtils(unittest.TestCase):
  """Tests for utility functions in reddit_scraper_lib."""

  def test_get_yt_video_id(self):
    self.assertEqual(
        reddit_scraper_lib.get_yt_video_id("http://youtu.be/_lOT2p_FCvA"),
        "_lOT2p_FCvA",
    )
    self.assertEqual(
        reddit_scraper_lib.get_yt_video_id(
            "www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu"
        ),
        "_lOT2p_FCvA",
    )
    self.assertEqual(
        reddit_scraper_lib.get_yt_video_id(
            "https://www.youtube.com/watch?v=rTHlyTphWP0&index=6"
        ),
        "rTHlyTphWP0",
    )

  def test_title_similarity_score(self):
    # Based on docstring examples
    self.assertEqual(
        reddit_scraper_lib.title_similarity_score(
            "Bob Dylan - ok", "bob dylan by ok"
        ),
        100,
    )
    self.assertEqual(
        reddit_scraper_lib.title_similarity_score(
            "Bob Dylan - ok", "bob dylan - ok"
        ),
        100,
    )
    # Test trump effect (remix vs no remix)
    self.assertEqual(
        reddit_scraper_lib.title_similarity_score(
            "Bob Dylan - ok (remix)", "bob dylan - ok"
        ),
        0,
    )
    # Test remove tokens overlap (docstring example)
    self.assertEqual(
        reddit_scraper_lib.title_similarity_score(
            "Bob Dylan - ok", "bob dylan - ok (Official Video)"
        ),
        100,
    )

  @patch('os.listdir')
  @patch('builtins.open', new_callable=mock_open)
  def test_log_files_in_folder(self, mock_file, mock_listdir):
    mock_listdir.return_value = [
        "Song 1 (Official Video).mp3",
        "Song 2 [1080p].mp3",
        "Another Song.mp3",
    ]

    reddit_scraper_lib.log_files_in_folder("output.log", "/dummy/folder")

    mock_file.assert_called_once_with("output.log", "w", encoding="utf-8")
    handle = mock_file()

    calls = [
        unittest.mock.call("Another Song\n"),
        unittest.mock.call("Song 1\n"),
        unittest.mock.call("Song 2 [P]\n"),
    ]
    handle.write.assert_has_calls(calls, any_order=False)

  @patch('glob.glob')
  @patch('pandas.read_csv')
  def test_check_cache(self, mock_read_csv, mock_glob):
    # Mock glob to return two files with different timestamps
    mock_glob.return_value = [
        "/dummy/cache/sub_search_0_1000.tsv",
        "/dummy/cache/sub_search_0_2000.tsv",
    ]

    # Mock pandas to return a dummy DataFrame
    mock_df = MagicMock()
    mock_read_csv.return_value = mock_df

    df, path = reddit_scraper_lib.check_cache("search", "/dummy/cache")

    # Verify it selected the one with the larger timestamp (2000)
    self.assertEqual(path, "/dummy/cache/sub_search_0_2000.tsv")
    self.assertEqual(df, mock_df)
    mock_read_csv.assert_called_once_with("/dummy/cache/sub_search_0_2000.tsv", sep='\t', index_col=0)


if __name__ == "__main__":
  unittest.main()
