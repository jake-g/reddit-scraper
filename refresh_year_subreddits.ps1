<#
.SYNOPSIS
    Reddit Music Scraper - Yearly Update (All Subreddits)
    
    DESCRIPTION:
    This is the maintenance script to run once per year (e.g., Jan 1st).
    It aggregates ALL target subreddits (Original List + 2025 Deep Research Expansion),
    filters out banned communities, and scrapes the "Top of the Year".
    
    TARGETS:
    - 100+ Subreddits across 12 distinct clusters.
    - Time Range: YEAR
    - Sort: TOP
#>

# Set Window Title
$Host.UI.RawUI.WindowTitle = "reddit-scraper-yearly-update"
Write-Host "Starting Reddit Scraper (Yearly Update)..." -ForegroundColor Cyan
Set-Location "D:\Projects\_Projects_Synced\music-library\reddit-scraper"

# ==========================================
# 1. EXCLUSION LIST
# ==========================================
# Communities explicitly banned from the library (Too specific/broad/irrelevant/broken)


# Communities explicitly banned from the library (Too specific/broad/irrelevant/broken)
$Banned = @(
    # Artists (Too Specific/Pop Fandoms)
    "CarlyRaeJepsen", "CharliXCX", "LanaDelRey", "FrankOcean", "TheWeeknd", 
    "TaylorSwift", "Bangtan", "BlackPink", "Drake", "Kanye",
    
    # Q&A / Requests / Too Broad (Not link aggregators)
    "musicsuggestions", "MusicRecommendations", "ifyoulikeblank", "WhereDoIStart",
    "IdentifyThisTrack", "listentothis", "ListenToUs", "LetsTalkMusic", 
    "tipofmytongue", "NameThatSong", "MakeMeAPlaylist", "ThisIsOurMusic",

    # Broken / Private / Does Not Exist (Added Dec 2025)
    "glitch", "highlife", "thespicecabinet", "FreshMusic",

    # 2025 Cleanup: Text-Only / Discussion / No Media Links
    # These consistently return 0 downloads because they are for talking, not listening.
    "WeAreTheMusicMakers", "Composer", "MusicProduction", "HipHop101", 
    "KpopHelp"

    # 2025 Cleanup: Inactive / Dead / Ultra-Low Yield
    # These returned 0 new entries in the yearly top charts.
    "BollywoodMusic", "Swing", "Hardcore", "Hardstyle", "Brostep", 
    "NuMetal", "VikingMetal", "MidwestEmo", 
    "RiotGrrrl", "PowerPopGirls", "IndianHipHopHeads",
)

# ==========================================
# 2. CLUSTERS
# ==========================================

# A. MODERN ERA & DISCOVERY (2010s-2020s & Hidden Gems)
$Cluster_ModernDiscovery = @(
    "2010smusic", "2020sMusic", "NewMusic", "IndieMusicFeedback", 
    "BedroomPop", "HyperPop", "lostwave", "UndergroundMusic", "UnheardOf",
    "deepcuts", "treemusic", "HeadNodders", "MelancholyMusic", "Elephant6",
    "Samplehunters", "vintageobscura", "TheOverload" 
)

# B. DECADES & VINTAGE (Pre-2010s)
$Cluster_Decades = @(
    "2000smusic", "90sMusic", "80sMusic", "70sMusic", "60sMusic", "50sMusic",
    "70s", "OldiesMusic", "SoundsVintage", "Exotica"
)

# C. ELECTRONIC: HOUSE & TECHNO (4/4 Rhythms)
$Cluster_HouseTechno = @(
    "house", "minimal", "deephouse", "tech_house", "melodichouse", "frenchhouse", 
    "funkhouse", "acidhouse", "Techno", "DubTechno", "OldskoolRave", "ElectronicMusic",
    "OldElectronicMusic", "industrialmusic", "Aggrotech", "EBM"
)

# D. ELECTRONIC: BASS, DUB & TRAP (Broken Beats)
$Cluster_Bass = @(
    "DnB", "AtmosphericDnB", "jungle", "breakcore", "Breakbeat", "BigBeat",
    "Dubstep", "realdubstep", "SpaceBass", "trapmuzik", "Trap",
    "bassheavy", "Grime", "UKGarage", "UKDrill", "GlitchHop",
    "dub", "reggae" # Often adjacent to bass culture
)

# E. ELECTRONIC: SYNTH & CHILL (Vibe-focused)
$Cluster_SynthChill = @(
    "IDM", "ambientmusic", "MusicToSleepTo", "chillmusic", "chillwave", 
    "psybient", "downtempo", "TripHop", "triphop", "lofihiphop", "burial",
    "futuresynth", "futurebeats", "futurebass", "futuregarage", 
    "vaporwave", "outrun", "newretrowave", "synthwave", "Darkwave", "Coldwave"
)

# F. ROCK: INDIE & ALTERNATIVE (General)
$Cluster_IndieRock = @(
    "indieheads", "indie", "indierock", "Rock", "ClassicRock", "ModernRockMusic",
    "90sAlternative", "90sRock", "AlternativeRock", "PostPunk", "GarageRock", 
    "BritPop", "Slowcore", "dancepunk", "NewWave", "NoWave"
)

# G. ROCK: NICHE, PSYCH & SHOEGAZE (Textures)
$Cluster_PsychShoegaze = @(
    "shoegaze", "DreamPop", "PostRock", "MathRock", "krautrock", "synthrock",
    "PsychedelicRock", "neopsychedelia", "stonerrock", "SpaceMusic",
    "monsterfuzz", "NoiseRock", "SurfPunk", "SurfRock"
)

# H. METAL & PUNK (Heavy)
$Cluster_Heavy = @(
    "Metal", "HeavyMetal", "DoomMetal", "BlackMetal", "DeathMetal", 
    "ThrashMetal", "SpeedMetal", "PowerMetal", "Sludge", "PostMetal",
    "metalcore", "deathcore", "MathCore", "Grindcore", "Djent", "ProgMetal", 
    "symphonicmetal", "folkmetal", "IndustrialMetal",
    "Punk_Rock", "90sPunk", "PostHardcore", "Emo", "Screamo", 
    "Ska", "SkaPunk", "FolkPunk", "CelticPunk"
)

# I. HIPHOP & URBAN (Beats & Rhymes)
$Cluster_HipHop = @(
    "hiphopheads", "hiphop", "rap", "80sHipHop", "90shiphop",
    "hiphopheadsnorthwest", "GermanRap", "FrenchRap",
    "Gfunk", "jazzyhiphop", "Instrumentals", "AfroBeat", "Dancehall", "Reggaeton"
)

# J. POP & MAINSTREAM (Fandoms)
$Cluster_Pop = @(
    "popheads", "pcmusic", "boybands",
    "kpop", "jpop", "cpop", "latinpopheads", "ArtPop",
    "Soca", "nudisco", "disco"
)

# K. JAZZ, CLASSICAL & ROOTS (Organic)
$Cluster_Organic = @(
    "jazz", "ModernJazz", "FreeJazz", "JazzFusion", "jazznoir", "GypsyJazz", 
    "DarkJazz", "NuJazz", "BigBand",
    "blues", "bluesrock", "folk", "IndieFolk", "bluegrass", "RootsMusic", 
    "altcountry", "OutlawCountry", "Americana",
    "ClassicalMusic", "ElitistClassical", "baroque", "contemporary", "EarlyMusic", 
    "Opera", "ChoralMusic", "icm"
)

# L. REGIONAL & WORLD (Global Sounds)
$Cluster_Global = @(
    "WorldMusic", "AfricanMusic", "AfroPop", "DesertBlues", 
    "brazilianmusic", "bossanova", "Flamenco", "ItalianMusic", 
    "japanesemusic", "citypop", "koreanrock", "kindie", "IndianIndie"
)

# M. FUNCTIONAL & CREATOR (Tools & Moods)
$Cluster_Functional = @(
    "MusicForConcentration", "codingmusic", "Liftingmusic", "runningmusic",
    "nightdrive", "rainymood", "gamemusic", "VGMvinyl", "Cyberpunk_Music", 
    "Frisson", "GuiltyPleasureMusic", "BinauralMusic", "animemusic",
    "BedroomBands"
)

# ==========================================
# 3. AGGREGATION & CLEANING
# ==========================================

$AllCandidates = $Cluster_ModernDiscovery + $Cluster_Decades + $Cluster_HouseTechno + `
                 $Cluster_Bass + $Cluster_SynthChill + $Cluster_IndieRock + `
                 $Cluster_PsychShoegaze + $Cluster_Heavy + $Cluster_HipHop + `
                 $Cluster_Pop + $Cluster_Organic + $Cluster_Global + $Cluster_Functional

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