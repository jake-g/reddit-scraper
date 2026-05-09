<#
.SYNOPSIS
    Reddit Music Scraper - Yearly Update (All Subreddits)

    DESCRIPTION:
    This is the maintenance script to run once per year (e.g., Jan 1st).
    It aggregates ALL target subreddits, filters out banned communities,
    and scrapes the "Top of the Year".
#>

# Set Window Title
$Host.UI.RawUI.WindowTitle = "reddit-scraper-yearly-update"
Write-Host "Starting Reddit Scraper (Yearly Update)..." -ForegroundColor Cyan
Set-Location "D:\Projects\_Projects_Synced\music-library\reddit-scraper"

# ==========================================
# 1. EXCLUSION LIST (BANNED SUBREDDITS)
# ==========================================
# Communities banned for being off-topic, discussion-focused, or consistently inactive.
$Banned = @(
    # Artists (Too Specific/Pop Fandoms)
    "Bangtan", "BlackPink", "CarlyRaeJepsen", "CharliXCX", "Drake",
    "FrankOcean", "Kanye", "LanaDelRey", "TaylorSwift", "TheWeeknd",

    # Q&A / Requests / Too Broad (Not link aggregators)
    "IdentifyThisTrack", "ifyoulikeblank", "LetsTalkMusic", "ListenToUs",
    "listentothis", "MakeMeAPlaylist", "MusicRecommendations", "musicsuggestions",
    "NameThatSong", "ThisIsOurMusic", "tipofmytongue", "WhereDoIStart",

    # Broken / Private / Does Not Exist
    "FreshMusic", "glitch", "highlife", "thespicecabinet",

    # Discussion-Focused / Text-Only (Creator feedback, not general discovery)
    "BedroomBands", "Composer", "HipHop101", "IndieMusicFeedback", "KpopHelp",
    "MusicProduction", "WeAreTheMusicMakers",

    # CONFIRMED Inactive / Dead / Low-Yield (Cleanup Dec 2025)
    "BollywoodMusic", "Breakcore", "CityPop", "ClassicalMusic", "Emo", "FolkPunk",
    "Gabber", "Grunge", "Hardcore", "Hardstyle", "IndianHipHopHeads", "MidwestEmo",
    "NuMetal", "Opera", "Outrun", "pcmusic", "PowerPopGirls", "Reggaeton",
    "RiotGrrrl", "Swing", "UKDrill", "VGMvinyl"
)

# ==========================================
# 2. CLUSTERS
# ==========================================

# A. ROCK, METAL & PUNK (Guitar-driven, from Classic to Extreme)
$Cluster_Rock_And_Metal = @(
    "90sAlternative", "90sPunk", "90sRock", "AlternativeRock", "BlackMetal", "BritPop",
    "CelticPunk", "ClassicRock", "dancepunk", "DeathMetal", "deathcore", "Djent",
    "DoomMetal", "DreamPop", "FolkMetal", "GarageRock", "Grindcore", "IndustrialMetal",
    "krautrock", "MathCore", "MathRock", "Metal", "metalcore", "ModernRockMusic",
    "monsterfuzz", "neopsychedelia", "NewWave", "NoWave", "NoiseRock", "PostHardcore",
    "PostMetal", "PostPunk", "PostRock", "PowerMetal", "ProgMetal", "PsychedelicRock",
    "Punk_Rock", "Rock", "Screamo", "shoegaze", "Ska", "SkaPunk", "Sludge", "Slowcore",
    "SpeedMetal", "stonerrock", "SurfPunk", "SurfRock", "symphonicmetal", "synthrock",
    "ThrashMetal", "VikingMetal"
)

# B. ELECTRONIC (All forms of synth, beat, and sample-based music)
$Cluster_Electronic = @(
    "acidhouse", "Aggrotech", "ambientmusic", "AtmosphericDnB", "bassheavy", "BigBeat",
    "Breakbeat", "Brostep", "burial", "chillwave", "Coldwave", "Darkwave", "deephouse",
    "DnB", "downtempo", "dub", "Dubstep", "DubTechno", "EBM", "ElectronicMusic",
    "frenchhouse", "funkhouse", "futurebass", "futurebeats", "futuregarage",
    "futuresynth", "GlitchHop", "Grime", "house", "IDM", "industrialmusic", "jungle",
    "lofihiphop", "melodichouse", "minimal", "newretrowave", "OldElectronicMusic",
    "OldskoolRave", "psybient", "realdubstep", "SpaceBass", "synthwave", "tech_house",
    "Techno", "Trap", "trapmuzik", "TripHop", "triphop", "UKGarage", "vaporwave"
)

# C. HIP-HOP & RHYTHM (Rap, R&B, Funk, and adjacent genres)
$Cluster_HipHop_And_Rhythm = @(
    "80sHipHop", "90shiphop", "AfroBeat", "Dancehall", "FrenchRap", "GermanRap",
    "Gfunk", "hiphop", "hiphopheadsnorthwest", "hiphopheads", "Instrumentals",
    "jazzyhiphop", "rap"
)

# D. POP & INDIE (Mainstream, Alternative Pop, and general discovery hubs)
$Cluster_Pop_And_Indie = @(
    "2010smusic", "2020sMusic", "ArtPop", "BedroomPop", "boybands", "cpop",
    "disco", "HyperPop", "indie", "indieheads","indierock",
    "jpop", "kpop", "LatinPopHeads", "NewMusic", "nudisco", "popheads", "Soca"
)

# E. JAZZ, FOLK & ROOTS (Acoustic, Organic, and traditional sounds)
$Cluster_Jazz_Folk_And_Roots = @(
    "altcountry", "Americana", "baroque", "BigBand", "bluegrass", "blues", "bluesrock",
    "ChoralMusic", "contemporary", "DarkJazz", "EarlyMusic", "ElitistClassical",
    "Exotica", "folk", "FreeJazz", "GypsyJazz", "icm", "IndieFolk", "jazz",
    "JazzFusion", "jazznoir", "ModernJazz", "NuJazz", "OldiesMusic", "OutlawCountry",
    "RootsMusic"
)

# F. BY ERA & REGION (Music defined by time or place)
$Cluster_By_Era_And_Region = @(
    "2000smusic", "50sMusic", "60sMusic", "70s", "70sMusic", "80sMusic", "90sMusic",
    "AfricanMusic", "AfroPop", "bossanova", "brazilianmusic", "DesertBlues",
    "Flamenco", "IndianIndie", "ItalianMusic", "japanesemusic", "kindie", "koreanrock",
    "SoundsVintage", "vintageobscura", "WorldMusic"
)

# G. BY MOOD & FUNCTION (Music for a specific purpose, feeling, or context)
$Cluster_By_Mood_And_Function = @(
    "animemusic", "BinauralMusic", "chillmusic", "codingmusic",
    "Cyberpunk_Music", "deepcuts", "Elephant6", "Frisson", "gamemusic",
    "GuiltyPleasureMusic", "HeadNodders", "Liftingmusic", "lostwave", "MelancholyMusic",
    "MusicForConcentration", "MusicToSleepTo", "nightdrive", "rainymood", "Samplehunters",
    "SpaceMusic", "TheOverload", "treemusic", "UnheardOf", "UndergroundMusic"
)

# ==========================================
# 3. AGGREGATION & CLEANING
# ==========================================

$AllCandidates = $Cluster_Rock_And_Metal + $Cluster_Electronic + $Cluster_HipHop_And_Rhythm + `
                 $Cluster_Pop_And_Indie + $Cluster_Jazz_Folk_And_Roots + `
                 $Cluster_By_Era_And_Region + $Cluster_By_Mood_And_Function

# 1. Sort and Unique (Removes any accidental duplicates between clusters)
$UniqueCandidates = $AllCandidates | Select-Object -Unique | Sort-Object

# 2. Remove BANNED items
# Note: Case sensitivity doesn't matter much here if we used .lower() in python,
# but -notcontains is case-insensitive in PowerShell anyway.
$FinalTargetList = $UniqueCandidates | Where-Object { $Banned -notcontains $_ }

# ==========================================
# 4. EXECUTION
# ==========================================

$SubredditString = $FinalTargetList -join ","

Write-Host "----------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "Reddit Scraper: YEARLY UPDATE" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------------"
Write-Host "Time Range       : YEAR (Top posts of the last 365 days)" -ForegroundColor Gray
Write-Host "Total Candidates : $( $UniqueCandidates.Count )" -ForegroundColor Gray
Write-Host "Banned / Removed : $( ($UniqueCandidates.Count - $FinalTargetList.Count) )" -ForegroundColor Red
Write-Host "Active Targets   : $( $FinalTargetList.Count )" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------"

if ($FinalTargetList.Count -eq 0) {
    Write-Host "Error: Target list is empty." -ForegroundColor Red
} else {
    Write-Host "Starting scrape..." -ForegroundColor Green

    # Run the Python script
    # Note: --time_range=year is set for the yearly update
    python scrape_subs.py `
        --sort=top `
        --time_range=year `
        --num_posts=1000 `
        --cache_dir="logs" `
        --use_cache `
        --log_filenames `
        --subs=$SubredditString | Tee-Object -FilePath "reddit_scraper_yearly_update.log"
}

Write-Host "Yearly Update Finished."
pause
