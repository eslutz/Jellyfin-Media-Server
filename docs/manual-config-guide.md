# Jellyfin Manual Configuration Guide

Use this when applying the non-global settings from `jellyfin.config.json` through the Jellyfin UI.

## Libraries
- Create libraries for Movies and TV Shows using the configured folder paths. Only the first folder in a list auto-adds via API; add any extra folders manually in the UI.
- Content types must match Jellyfin expectations: Movies → Movie, TV Shows → Series.
- After creation, open each library's settings:
  - **Metadata downloaders** (order matters): Movies → TheMovieDb (1), The Open Movie Database (2); TV Shows → TheTVDB (1), The Open Movie Database (2).
  - **Image fetchers** (order matters): Movies → TheMovieDb (1), Fanart (2); TV Shows → TheTVDB (1), Fanart (2).
  - **Metadata savers**: enable Nfo.
  - **Language/region**: Preferred language `en`, Country `US`, Prefer embedded titles off.
  - **Metadata refresh**: enable automatic refresh; allow image replacement; do not save artwork into media folders.
  - **Realtime monitoring**: enable.
  - **Display**: hide missing episodes and specials (disable both options) for TV libraries.
  - **Images**: `skip_images_if_nfo_exists` is UI-only; set manually if desired.
  - **Chapter images**: enable extraction and allow during library scan.
  - **Trickplay**: enable extraction for each library.

## Scheduled Tasks
Use Dashboard → Scheduled Tasks → each task's **Triggers** to configure intervals.
- Scan Media Library: enable, every 30 minutes (interval trigger).
- Extract Chapter Images: enable, daily at 03:00.
- Trickplay Image Extraction: enable, daily at 03:00.
- Detect Intros (generate intro skip data): enable, daily at 03:00; restrict to the TV Shows library.

## Authentication
Ensure your API key is created via Dashboard → API Keys and stored in `.env` as `JELLYFIN_API_KEY`. The script uses `X-Emby-Token` for auth, matching Jellyfin requirements.

## Logging Notes
When switching between script-driven global settings and manual UI steps, keep the logs from dry-run executions. Warnings will call out missing tasks or unsupported options (e.g., `skip_images_if_nfo_exists`).
