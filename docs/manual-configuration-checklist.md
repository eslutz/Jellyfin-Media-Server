# Full Manual Configuration Checklist

Use this checklist if you want to configure everything in the Jellyfin UI without automation.

## Prereqs
- Confirm server URL and API key are known; store `JELLYFIN_URL` and `JELLYFIN_API_KEY` in `.env` for future script use.
- Validate `jellyfin.config.json` with `python -m json.tool jellyfin.config.json` if you plan to mirror its values.

## Server-Wide Settings
- Disable Quick Connect (Dashboard → Advanced → Quick Connect).
- Set global Trickplay options as desired (Dashboard → Playback → Trickplay). Mirror any values from `trickplay_options` in `jellyfin.config.json`.

## Libraries
- Create Movies library with folder `/Volumes/MediaLib/movies`; type Movie.
- Create TV Shows library with folder `/Volumes/MediaLib/tv`; type Series.
- For each library:
  - Enable realtime monitoring.
  - Metadata downloaders: Movies → TheMovieDb (1), The Open Movie Database (2); TV → TheTVDB (1), The Open Movie Database (2).
  - Image fetchers: Movies → TheMovieDb (1), Fanart (2); TV → TheTVDB (1), Fanart (2).
  - Metadata savers: enable Nfo.
  - Language/region: Preferred language `en`, Country `US`; prefer embedded titles off.
  - Auto-refresh metadata on; allow image replacement; do not save artwork into media folders.
  - Display (TV): hide missing episodes; hide specials.
  - Images: set `skip_images_if_nfo_exists` if desired (UI-only).
  - Chapter images: enable extraction and allow during scan.
  - Trickplay: enable extraction.

## Scheduled Tasks (Triggers)
- Scan Media Library: every 30 minutes.
- Extract Chapter Images: daily at 03:00.
- Trickplay Image Extraction: daily at 03:00.
- Detect Intros: daily at 03:00; scope to TV Shows library.

## Post-Config Verification
- Run a library scan once to confirm monitoring and tasks trigger.
- Check recent activity/logs for metadata fetchers ordering and NFO writes.
- Spot-check a movie and a TV series for artwork, chapter images, and trickplay tiles.
- Confirm scheduled task next-run times reflect the above triggers.

## Optional: Script Reuse
- After manual setup, you can still run `python3 configure_jellyfin.py --dry-run --verbose` to verify global settings align with config. Non-global items remain manual by design.
