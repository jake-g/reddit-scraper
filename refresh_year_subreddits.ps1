# Set Window Title
$Host.UI.RawUI.WindowTitle = "reddit-scraper"

Write-Host "Starting Reddit Scraper..."
Set-Location "D:\Projects\_Projects_Synced\music-library\reddit-scraper"

$subreddits = @(
    "house", "minimal", "deephouse", "theOverload", "TropicalHouse", "melodichouse", "frenchhouse", 
    "AtmosphericDnB", "funkhouse", "witch_house", "OldskoolRave", "Techno", "ElectronicMusic", 
    "futuresynth", "idm", "realdubstep", "ambientmusic", "MusicToSleepTo", "90sAlternative", "90sPunk", 
    "90sRock", "Punk_Rock", "dancepunk", "blues", "bluesrock", "folk", "bluegrass", "Rock", "shoegaze", 
    "ClassicRock", "krautrock", "synthrock", "chillwave", "futurebeats", "futurebass", "futuregarage", 
    "nudisco", "NewWave", "PostRock", "disco", "DreamPop", "indieheads", "indie", "indierock", "dub", 
    "reggae", "PsychedelicRock", "stonerrock", "SurfPunk", "DoomMetal", "IndieFolk", "GypsyJazz", 
    "jazznoir", "jazz", "80sHipHop", "Gfunk", "rap", "hiphop", "hiphopheads", "hiphopheadsnorthwest", 
    "lofihiphop", "hiphop101", "90shiphop", "jazzyhiphop", "trapmuzik", "triphop", "Instrumentals", 
    "2010smusic", "2000smusic", "90sMusic", "80sMusic", "70sMusic", "70s", "60sMusic", "50sMusic", 
    "OldiesMusic", "SoundsVintage", "VintageObscura", "AfricanMusic", "Flamenco", "WorldMusic", "animemusic", 
    "chillmusic", "bossanova", "bassheavy", "BinauralMusic", "rainymood", "deepcuts", "treemusic", 
    "HeadNodders", "MelancholyMusic", "Elephant6", "acidhouse", "ModernRockMusic", "monsterfuzz", 
    "neopsychedelia", "OutlawCountry", "Exotica", "SpaceMusic", "OldElectronicMusic", "industrialmusic", 
    "RootsMusic", "altcountry", "Samplehunters", "baroque"
)
$subredditsString = $subreddits -join ','

python scrape_subs.py `
    --sort=top `
    --time_range=year `
    --num_posts=1000 `
    --cache_dir="logs" `
    --use_cache `
    --log_filenames `
    --subs=$subredditsString | Tee-Object -FilePath "reddit_scraper_output.log"

Write-Host "Reddit Scraper has finished running."
pause  # (pause until enter is pressed)
