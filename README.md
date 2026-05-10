# Reddit Scraper

This module contains scripts to scrape Reddit for music links (YouTube, SoundCloud) and manage the results.

## Files

* `scrape_subs.py`: Main script to scrape subreddits.
* `reddit_scraper_lib.py`: Library functions for fetching data and string processing.
* `reddit_scraper_tests.py`: Unit tests for library functions.
* `refresh_year_subreddits.ps1`: PowerShell script to refresh year-specific subreddits.
* `notebooks/`: Jupyter notebooks for data merging and ML experiments.

## Setup

Install dependencies from the root workspace or locally:

```bash
pip install -r requirements.txt
```

## Tests

To run the unit tests:

```bash
python reddit_scraper_tests.py
```

## Highlight Changelog

* **May 2026**: Modularized Reddit Scraper directory; moved notebooks to `notebooks/` and updated tracking.
* **Dec 2025**: Performed 2025 scrape with deep research additions and integrated Gemini-graded ratings
* **Jan 2025**: Experimented with Machine Learning for match pass/fail verification
* **Nov 2024**: Updated run scripts and performed a full-year run across expanded subreddits
* **May 2024**: Added manual labels using Gemini Advanced
* **Jan 2024**: Scraped and processed albums from 2023
* **Jan 2023**: Implemented grading for fuzzy YouTube-Reddit matches
* **Dec 2022**: Expanded scraping to include new 2022 subreddits
* **Dec 2021**: Refreshed all subreddits for all time and merged entries into the main database
* **Nov 2021**: Finalized the first set of subreddits with generated playlists
* **Aug 2019**: Initial commit and start of the Reddit scraper project
