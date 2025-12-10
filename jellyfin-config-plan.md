# Jellyfin Library Settings Configuration Plan

## Creating/Editing a Library

**Dashboard → Libraries → Add Library** (or click pencil icon to edit existing)

-----

### **Display Tab**

- ✅ Set **Display name** to descriptive name (e.g., “Movies”, “TV Shows”)
- ❌ **Display missing episodes** → Uncheck
- ❌ **Display specials** → Uncheck (optional: leave checked if you want specials)

-----

### **Library Tab**

- ✅ Set **Content type** → Movies / Shows (match your content)
- ✅ Add **Folders** → `/Volumes/MediaLib/movies` (or `/tv`, etc.)
- ✅ **Enable real time monitoring** → Check

-----

### **Metadata Downloaders Tab**

**Reorder priority (drag to arrange):**

1. **TheMovieDb** (for Movies) / **TheTVDB** (for TV Shows)
1. **The Open Movie Database**
1. Uncheck all others

-----

### **Image Fetchers Tab**

**Reorder priority (drag to arrange):**

1. **TheMovieDb** (for Movies) / **TheTVDB** (for TV Shows)
1. **Fanart**
1. Uncheck all others (especially **Screen Grabber** unless needed)

-----

### **Metadata Savers Tab**

- ✅ **Nfo** → Check
- ❌ All others → Uncheck

-----

### **Advanced Tab**

#### Metadata Section

- ✅ Set **Preferred language** → `en`
- ✅ Set **Country** → `US`
- ❌ **Prefer embedded titles over file names** → Uncheck
- ✅ **Automatically refresh metadata from the internet** → Check
- ❌ **Save artwork into media folders** → Uncheck
- ✅ **Replace existing images** → Check

#### Images Section

- ✅ **Skip images during library scan if metadata nfo exists** → Check

#### Chapter Images Section

- ✅ **Enable chapter image extraction** → Check
- ✅ **Extract chapter images during the library scan** → Check

#### Trickplay Section

- ✅ **Enable Trickplay image extraction** → Check
  - Generates seek preview thumbnails when hovering over timeline
  - Storage cost: ~200-500MB per 2-hour movie, ~50-150MB per TV episode
  - One-time generation during initial scan or when adding new media

-----

### **Subtitles Tab**

- (Configure as needed; no specific recommendations)

-----

## Post-Library Creation

### **Dashboard → Scheduled Tasks**

#### Scan Media Library

- ✅ Keep enabled
- ✅ Set interval: **Every 30 minutes** or **Hourly**

#### Extract Chapter Images

- ✅ Verify task exists (appears after enabling chapter extraction)
- ✅ Run manually after adding new media, or set to daily off-peak

#### Trickplay Image Extraction

- ✅ Verify task exists (appears after enabling trickplay)
- ✅ Set to run **daily at 3 AM** (avoid peak usage times)
- Note: Initial library scan will take significantly longer (hours for large libraries)

#### Generate Intro Skip Data

- ✅ **For TV Shows library**: Enable intro detection
  - Analyzes episodes to identify recurring intro sequences
  - Adds “Skip Intro” button in clients during playback
  - Set to run **daily at 3 AM** (avoid peak usage)
- ❌ **For Movies library**: Leave disabled (not applicable)

-----

## Verify Sonarr/Radarr Settings

**Sonarr/Radarr → Settings → Media Management**

- ✅ **Use Hardlinks instead of Copy** → Enable
- ⚠️ **Import Extra Files** → Enable with whitelist (recommended)
  - ✅ Check **Import Extra Files**
  - ✅ Set **Extra File Extensions** to: `srt`
  - Alternative: Leave disabled if all media has embedded subtitles

### Why Whitelist Subtitles Only

**Problem with importing all extra files:**

- Torrent `.nfo` files contain uploader metadata (release info, tracker details) that conflicts with Jellyfin’s metadata system
- Scene releases include junk files: `Sample.mkv`, `proof.png`, `.txt` release notes
- These clutter your library and can break Jellyfin’s metadata parsing

**Solution - Import only `.srt` files:**

- ✅ Preserves external subtitle files from torrents
- ✅ Jellyfin auto-detects them (e.g., `Film (2024).en.srt`, `Film (2024).es.srt`)
- ✅ Users get subtitle options in player
- ✅ Blocks `.nfo`, samples, and other junk files
- ✅ Small files; doesn’t interfere with hardlink seeding

**Example import result:**

```
/movies/Film (2024)/
├── Film (2024).mkv          ← Hardlinked video
├── Film (2024).en.srt       ← Imported subtitle
├── Film (2024).es.srt       ← Imported subtitle
└── Film (2024).nfo          ← Written by Jellyfin (correct metadata)
```

**If all your media has embedded subtitles:** Disable this feature entirely for the cleanest setup.

-----

## Summary Checklist

- [ ] Real-time monitoring enabled
- [ ] Metadata downloaders ordered correctly
- [ ] Only Nfo saver enabled
- [ ] Chapter image extraction enabled
- [ ] Trickplay enabled
- [ ] Intro detection enabled for TV Shows
- [ ] Scheduled scans configured (every 30-60 min)
- [ ] Trickplay/intro detection tasks scheduled for 3 AM
- [ ] Sonarr/Radarr using hardlinks
- [ ] Import Extra Files disabled in *arr

-----

## Storage Locations Reference

### Jellyfin Data Directory

|OS         |Path                                    |
|-----------|----------------------------------------|
|**Linux**  |`/var/lib/jellyfin/`                    |
|**macOS**  |`/Users/USERNAME/.local/share/jellyfin/`|
|**Windows**|`C:\ProgramData\Jellyfin\Server\`       |

### What Gets Stored Where

- **NFO files**: Next to media files (`/Volumes/MediaLib/movies/Film (2024)/movie.nfo`)
- **Metadata cache**: `/var/lib/jellyfin/metadata/library/[itemID]/`
- **Chapter images**: `/var/lib/jellyfin/metadata/library/[itemID]/chapters/`
- **Trickplay images**: `/var/lib/jellyfin/trickplay/library/[itemID]/`
- **Database**: `/var/lib/jellyfin/data/library.db`

### Storage Impact Estimates

- **NFO files**: ~5-20KB per item (negligible)
- **Chapter images**: ~10-50KB per chapter (80KB-1MB per movie)
- **Trickplay images**: ~200-500MB per 2-hour movie
- **Metadata cache**: ~500KB-2MB per item (posters, backdrops)

-----

## Notes

- **Movies vs TV Shows**: Use TheMovieDb for Movies, TheTVDB for TV Shows
- **Local storage**: All settings optimized for local USB/internal drives
- **Hardlinks**: Critical for torrent seeding; NFO files won’t interfere
- **Trickplay**: Optional but recommended for Movies; consider storage budget
- **Intro detection**: TV Shows only; CPU-intensive but useful for binge-watching
