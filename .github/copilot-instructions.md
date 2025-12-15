# Jellyfin Configuration Script - Copilot Instructions

## Naming Conventions

**Markdown files**: Use lowercase with hyphens as separators (e.g., `configuration-guide.md`, `api-endpoints.md`). Exceptions: `README.md`, `SECURITY.md`, `CONTRIBUTING.md`.

Python automation for configuring Jellyfin Media Server via REST API. Main flow: [configure_jellyfin.py](../configure_jellyfin.py) reads [jellyfin.config.json](../jellyfin.config.json), authenticates via `.env`, applies configuration through Jellyfin API.

## Critical Non-Obvious Patterns

**Jellyfin uses tick-based time** (100ns intervals): `TICKS_PER_SECOND = 10000000`

- Convert time to ticks: `(hours*3600 + minutes*60) * TICKS_PER_SECOND`
- Example: 3 AM daily = `(3*3600 + 0*60) * 10000000` ticks
- Used in `/ScheduledTasks/{taskId}/Triggers` for `IntervalTicks` and `TimeOfDayTicks`

**Authentication**: Must use `X-Emby-Token` header (Jellyfin standard), NOT Bearer tokens

**Multi-folder limitation**: API only adds first folder in `folders` array automatically. Log warning with manual UI steps for additional folders (see `_create_library` L285-295).

**Metadata fetcher names must match exactly**:

- Movies: `"TheMovieDb"`, `"The Open Movie Database"`
- TV Shows: `"TheTVDB"`, `"The Open Movie Database"`
- Case-sensitive strings passed to `TypeOptions.MetadataFetchers` array

**LibraryOptions API pattern** (L305-370):

1. Create library via `POST /Library/VirtualFolders`
2. Get `ItemId` from created library
3. Build `LibraryOptions` dict with `TypeOptions` array (content-type dependent)
4. POST to `/Library/VirtualFolders/LibraryOptions?id={ItemId}` with options body

**Content type mapping** (`_get_type_name_for_content`):

- `movies` → `Movie`, `tvshows` → `Series`, `music` → `Audio`, `books` → `Book`

## Development Workflow

**Always test with dry-run first**: `python3 configure_jellyfin.py --dry-run --verbose`

- Dry-run executes GET requests, only logs POST/PUT/DELETE (see `_make_request` L103-107)

**Testing**:

```bash
python tests/test_configure_jellyfin.py  # Unit tests (no live server)
python -m json.tool jellyfin.config.json  # Validate JSON syntax
```

**CI linting exceptions** (`.github/workflows/ci.yml`):

- Pylint: `--disable=C0111,R0913,R0914,R0912,R0915` (suppress docstring/complexity warnings)
- Flake8: `--select=E9,F63,F7,F82` for fatal errors only

## Configuration Reference

**Scheduled task name mapping** (config key → Jellyfin task name):

- `scan_media_library` → `"Scan Media Library"`
- `extract_chapter_images` → `"Extract Chapter Images"`
- `trickplay_image_extraction` → `"Trickplay Image Extraction"`
- `generate_intro_skip_data` → `"Detect Intros"` (TV shows only)

**Unsupported settings**: `skip_images_if_nfo_exists` has no API equivalent - log warning for manual UI config

**Logging conventions**:

- Log fetchers/savers as arrays: `logger.info(f"Metadata downloaders: {downloaders}")`
- Use `logger.warning()` for non-fatal issues requiring manual intervention

See [configuration-plan.md](../../docs/jellyfin-media-server/configuration-plan.md) for Jellyfin UI equivalents of all settings.
