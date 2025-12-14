<#
.SYNOPSIS
    Reddit Music Scraper - Deep Research Expansion (Final Polish)
    
    LOGIC:
    1. Defines the 'Archive' (Already scraped 2024/2025).
    2. Defines 'Banned' (Too specific artists or too broad Q&A).
    3. Defines 'Target Clusters' (New Eras, Regions, Genres).
    4. FILTERS: Candidates - Banned - Archive = Final Target List.
    5. EXECUTES: Scraper with --time_range=all.
#>

# Set Window Title
$Host.UI.RawUI.WindowTitle = "reddit-scraper-deep-research-final"
Write-Host "Starting Reddit Scraper (Deep Research Final)..." -ForegroundColor Cyan
Set-Location "D:\Projects\_Projects_Synced\music-library\reddit-scraper"

# ==========================================
# 1. EXCLUSION LISTS
# ==========================================

# GROUP A: THE ARCHIVE (Already Scraped)
$AlreadyScraped = @(
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

# GROUP B: BANNED (Too specific, too broad, or irrelevant)
$Banned = @(
    # Artists (Too Specific)
    "CarlyRaeJepsen", "CharliXCX", "LanaDelRey", "FrankOcean", "TheWeeknd", 
    "TaylorSwift", "Bangtan", "BlackPink", "Drake", "Kanye",
    
    # Recommendation/Q&A/Broad (Not link aggregators)
    "musicsuggestions", "MusicRecommendations", "ifyoulikeblank", "WhereDoIStart",
    "IdentifyThisTrack", "listentothis", "ListenToUs", "LetsTalkMusic", 
    "tipofmytongue", "NameThatSong", "MakeMeAPlaylist", "ThisIsOurMusic"
)

# ==========================================
# 2. RESEARCH CLUSTERS (Candidates)
# ==========================================

# 1. ERAS & DISCOVERY (2010s-2020s & Underground)
$Cluster_Modern = @(
    "2020sMusic", "NewMusic", "IndieMusicFeedback", 
    "BedroomPop", "HyperPop", "lostwave", "UndergroundMusic", "UnheardOf"
)

# 2. ELECTRONIC EXPANSION (Harder, Faster, Weirder)
# Note: 'TheOverload' and 'vintageobscura' removed (Already Scraped)
$Cluster_Electronic = @(
    "breakcore", "jungle", "DnB", "gabber", "hardstyle", 
    "psybient", "vaporwave", "outrun", "newretrowave", "synthwave", 
    "SpaceBass", "burial", "dubstep", "GlitchHop", 
    "ElectroSwing", "Complextro", "UKGarage"
)

# 3. ORGANIC, ROCK & METAL (Heavier, Emo, Punk)
$Cluster_RockMetal = @(
    "MathRock", "GaragePunk", "BlackMetal", "DeathMetal", "ProgMetal", 
    "folkmetal", "symphonicmetal", "metalcore", "deathcore", "Emo", 
    "hardcore", "folkpunk", "Screamo", "MidwestEmo", "NoiseRock", 
    "Grunge", "BritPop", "Ska", "SkaPunk"
)

# 4. POP, HIPHOP & URBAN (Excluding Artist Subs)
$Cluster_PopUrban = @(
    "popheads", "pcmusic", "powerpopgirls", "boybands",
    "kpop", "kpophelp", "jpop", "Grime", "UKDrill", "latinpopheads", "ArtPop"
)

# 5. JAZZ, CLASSICAL & GLOBAL (Academic & Regional)
$Cluster_World = @(
    "ElitistClassical", "contemporary", "EarlyMusic", "Opera",
    "ChoralMusic", "Composer", "JazzFusion", "ModernJazz", "FreeJazz", 
    "icm", "DarkJazz", "Swing", "Motown", "NeoSoul",
    "IndianIndie", "IndianHipHopHeads", "AfroPop", "AfroBeat",
    "DesertBlues", "brazilianmusic", "japanesemusic", "koreanrock", "kindie",
    "GermanRap", "FrenchRap", "ItalianMusic", "citypop", "BollywoodMusic", "Soca"
)

# 6. FUNCTIONAL & CREATOR (Vibe, Focus, Production)
$Cluster_Functional = @(
    "MusicForConcentration", "codingmusic", "Liftingmusic", "runningmusic",
    "nightdrive", "gamemusic", "VGMvinyl", "Cyberpunk_Music", 
    "Frisson", "GuiltyPleasureMusic",
    "WeAreTheMusicMakers", "musicproduction", "BedroomBands"
)

# ==========================================
# 3. AGGREGATION & FILTERING
# ==========================================

$AllCandidates = $Cluster_Modern + $Cluster_Electronic + $Cluster_RockMetal + $Cluster_PopUrban + $Cluster_World + $Cluster_Functional

# 1. Sort and Unique
$UniqueCandidates = $AllCandidates | Select-Object -Unique | Sort-Object

# 2. Remove BANNED items
$CleanCandidates = $UniqueCandidates | Where-Object { $Banned -notcontains $_ }

# 3. Remove ALREADY SCRAPED items (The final target list)
$FinalTargetList = $CleanCandidates | Where-Object { $AlreadyScraped -notcontains $_ }

# ==========================================
# 4. EXECUTION
# ==========================================

$SubredditString = $FinalTargetList -join ","

Write-Host "----------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "Music Subreddit Deep Research Aggregation Script" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------"
Write-Host "Candidates Initial    : $( $UniqueCandidates.Count )" -ForegroundColor Gray
Write-Host "Removed (Banned)      : $( ($UniqueCandidates.Count - $CleanCandidates.Count) )" -ForegroundColor Red
Write-Host "Removed (Already Done): $( ($CleanCandidates.Count - $FinalTargetList.Count) )" -ForegroundColor Red
Write-Host "ACTUAL New Targets    : $( $FinalTargetList.Count )" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------"

if ($FinalTargetList.Count -eq 0) {
    Write-Host "No new subreddits found to scrape!" -ForegroundColor Red
} else {
    Write-Host "Scraping now... (Time Range: All | Sort: Top)" -ForegroundColor Green
    
    # Run the Python script
    python scrape_subs.py `
        --sort=top `
        --time_range=all `
        --num_posts=1000 `
        --cache_dir="logs" `
        --use_cache `
        --log_filenames `
        --subs=$SubredditString | Tee-Object -FilePath "reddit_scraper_deep_research_2025_new_subs.log"
}

Write-Host "Run Finished."
pause