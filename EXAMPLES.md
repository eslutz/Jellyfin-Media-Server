# Usage Examples

This document provides practical examples of using the Jellyfin configuration script.

## Quick Start Example

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Get Your API Key

1. Open Jellyfin web interface
2. Go to **Dashboard → API Keys**
3. Click **+** to create new key
4. Copy the generated key

### 3. Create Your Configuration

```bash
cp jellyfin.config.example.json jellyfin.config.json
```

Edit `jellyfin.config.json` and update:
- `server.url`: Your Jellyfin server URL
- `server.api_key`: Your API key from step 2
- `libraries[].folders`: Your media folder paths

### 4. Test with Dry Run

```bash
python3 configure_jellyfin.py --dry-run --verbose
```

This shows what would be changed without making actual changes.

### 5. Apply Configuration

```bash
python3 configure_jellyfin.py
```

## Example Configurations

### Example 1: Simple Movie Library

```json
{
  "server": {
    "url": "http://192.168.1.100:8096",
    "api_key": "your-api-key-here"
  },
  "libraries": [
    {
      "name": "Movies",
      "content_type": "movies",
      "folders": ["/mnt/media/movies"],
      "metadata_downloaders": [
        {"name": "TheMovieDb", "enabled": true, "priority": 1}
      ],
      "image_fetchers": [
        {"name": "TheMovieDb", "enabled": true, "priority": 1}
      ],
      "metadata_savers": [
        {"name": "Nfo", "enabled": true}
      ],
      "advanced": {
        "metadata": {
          "preferred_language": "en",
          "country": "US"
        }
      }
    }
  ],
  "scheduled_tasks": {
    "scan_media_library": {
      "enabled": true,
      "interval_minutes": 60
    }
  }
}
```

### Example 2: TV Shows with Intro Detection

```json
{
  "server": {
    "url": "http://localhost:8096",
    "api_key": "your-api-key-here"
  },
  "libraries": [
    {
      "name": "TV Shows",
      "content_type": "tvshows",
      "folders": ["/mnt/media/tv"],
      "metadata_downloaders": [
        {"name": "TheTVDB", "enabled": true, "priority": 1},
        {"name": "The Open Movie Database", "enabled": true, "priority": 2}
      ],
      "image_fetchers": [
        {"name": "TheTVDB", "enabled": true, "priority": 1},
        {"name": "Fanart", "enabled": true, "priority": 2}
      ],
      "metadata_savers": [
        {"name": "Nfo", "enabled": true}
      ],
      "advanced": {
        "metadata": {
          "preferred_language": "en",
          "country": "US"
        },
        "chapter_images": {
          "enable_chapter_image_extraction": true,
          "extract_during_library_scan": true
        }
      }
    }
  ],
  "scheduled_tasks": {
    "scan_media_library": {
      "enabled": true,
      "interval_minutes": 30
    },
    "generate_intro_skip_data": {
      "enabled": true,
      "schedule": "daily",
      "time": "03:00"
    }
  }
}
```

### Example 3: Complete Setup (Movies + TV Shows)

```json
{
  "server": {
    "url": "http://jellyfin.local:8096",
    "api_key": "your-api-key-here"
  },
  "libraries": [
    {
      "name": "Movies",
      "content_type": "movies",
      "folders": ["/media/movies"],
      "library": {
        "enable_realtime_monitoring": true
      },
      "metadata_downloaders": [
        {"name": "TheMovieDb", "enabled": true, "priority": 1},
        {"name": "The Open Movie Database", "enabled": true, "priority": 2}
      ],
      "image_fetchers": [
        {"name": "TheMovieDb", "enabled": true, "priority": 1},
        {"name": "Fanart", "enabled": true, "priority": 2}
      ],
      "metadata_savers": [
        {"name": "Nfo", "enabled": true}
      ],
      "advanced": {
        "metadata": {
          "preferred_language": "en",
          "country": "US",
          "automatically_refresh_metadata": true
        },
        "chapter_images": {
          "enable_chapter_image_extraction": true,
          "extract_during_library_scan": true
        },
        "trickplay": {
          "enable_trickplay_extraction": true
        }
      }
    },
    {
      "name": "TV Shows",
      "content_type": "tvshows",
      "folders": ["/media/tv"],
      "library": {
        "enable_realtime_monitoring": true
      },
      "metadata_downloaders": [
        {"name": "TheTVDB", "enabled": true, "priority": 1},
        {"name": "The Open Movie Database", "enabled": true, "priority": 2}
      ],
      "image_fetchers": [
        {"name": "TheTVDB", "enabled": true, "priority": 1},
        {"name": "Fanart", "enabled": true, "priority": 2}
      ],
      "metadata_savers": [
        {"name": "Nfo", "enabled": true}
      ],
      "advanced": {
        "metadata": {
          "preferred_language": "en",
          "country": "US",
          "automatically_refresh_metadata": true
        },
        "chapter_images": {
          "enable_chapter_image_extraction": true,
          "extract_during_library_scan": true
        }
      }
    }
  ],
  "scheduled_tasks": {
    "scan_media_library": {
      "enabled": true,
      "interval_minutes": 30
    },
    "extract_chapter_images": {
      "enabled": true,
      "schedule": "daily",
      "time": "03:00"
    },
    "trickplay_image_extraction": {
      "enabled": true,
      "schedule": "daily",
      "time": "03:00"
    },
    "generate_intro_skip_data": {
      "enabled": true,
      "schedule": "daily",
      "time": "03:00"
    }
  }
}
```

## Command Line Examples

### Show Help

```bash
python3 configure_jellyfin.py --help
```

### Dry Run (Preview Changes)

```bash
python3 configure_jellyfin.py --dry-run
```

### Verbose Output

```bash
python3 configure_jellyfin.py --verbose
```

### Custom Config File

```bash
python3 configure_jellyfin.py --config /path/to/custom-config.json
```

### Dry Run with Verbose Output

```bash
python3 configure_jellyfin.py --dry-run --verbose
```

### Apply Configuration from Custom File

```bash
python3 configure_jellyfin.py --config production.json
```

## Expected Output

### Successful Run

```
2025-12-10 12:00:00,000 - INFO - Loading configuration from jellyfin.config.json
2025-12-10 12:00:00,001 - INFO - Configuration loaded successfully
2025-12-10 12:00:00,002 - INFO - Testing connection to http://localhost:8096...
2025-12-10 12:00:00,150 - INFO - Connected to Jellyfin 10.8.13
2025-12-10 12:00:00,151 - INFO - ============================================================
2025-12-10 12:00:00,151 - INFO - Starting Jellyfin configuration...
2025-12-10 12:00:00,151 - INFO - ============================================================
2025-12-10 12:00:00,152 - INFO - Configuring 2 libraries...
2025-12-10 12:00:00,153 - INFO - Configuring library: Movies
2025-12-10 12:00:00,154 - INFO - Creating new library 'Movies'...
2025-12-10 12:00:00,300 - INFO - Library 'Movies' created successfully
2025-12-10 12:00:00,301 - INFO - Applying settings for library 'Movies'...
2025-12-10 12:00:00,302 - INFO -   Metadata downloaders: ['TheMovieDb', 'The Open Movie Database']
2025-12-10 12:00:00,302 - INFO -   Image fetchers: ['TheMovieDb', 'Fanart']
2025-12-10 12:00:00,302 - INFO -   Metadata savers: ['Nfo']
2025-12-10 12:00:00,302 - INFO -   Language: en
2025-12-10 12:00:00,302 - INFO -   Country: US
2025-12-10 12:00:00,302 - INFO -   Chapter image extraction: ENABLED
2025-12-10 12:00:00,302 - INFO -   Trickplay extraction: ENABLED
2025-12-10 12:00:00,450 - INFO - Library options applied successfully for 'Movies'
2025-12-10 12:00:00,451 - INFO - Configuring scheduled tasks...
2025-12-10 12:00:00,550 - INFO - Configuring task 'Scan Media Library' (ID: ScanLibrary)
2025-12-10 12:00:00,551 - INFO -   Setting interval: 30 minutes
2025-12-10 12:00:00,650 - INFO - Task 'Scan Media Library' configured successfully
2025-12-10 12:00:00,651 - INFO - Scheduled tasks configuration complete
2025-12-10 12:00:00,651 - INFO - ============================================================
2025-12-10 12:00:00,651 - INFO - Configuration completed successfully!
2025-12-10 12:00:00,651 - INFO - ============================================================
```

### Dry Run Output

```
2025-12-10 12:00:00,000 - INFO - Loading configuration from jellyfin.config.json
2025-12-10 12:00:00,001 - INFO - Configuration loaded successfully
2025-12-10 12:00:00,002 - INFO - Testing connection to http://localhost:8096...
2025-12-10 12:00:00,150 - INFO - Connected to Jellyfin 10.8.13
2025-12-10 12:00:00,151 - INFO - ============================================================
2025-12-10 12:00:00,151 - INFO - Starting Jellyfin configuration...
2025-12-10 12:00:00,151 - INFO - ============================================================
2025-12-10 12:00:00,151 - INFO - DRY RUN MODE - No changes will be made
2025-12-10 12:00:00,152 - INFO - Configuring 1 libraries...
2025-12-10 12:00:00,153 - INFO - Configuring library: Movies
2025-12-10 12:00:00,154 - INFO - Creating new library 'Movies'...
2025-12-10 12:00:00,154 - INFO - [DRY RUN] Would POST http://localhost:8096/Library/VirtualFolders
2025-12-10 12:00:00,155 - INFO - Library 'Movies' created successfully
2025-12-10 12:00:00,156 - INFO - Applying settings for library 'Movies'...
2025-12-10 12:00:00,156 - INFO - [DRY RUN] Would POST http://localhost:8096/Library/VirtualFolders/LibraryOptions
2025-12-10 12:00:00,156 - INFO - [DRY RUN] With data: {...}
...
```

## Troubleshooting Examples

### Error: API Key Not Set

```
ERROR - API key not configured in jellyfin.config.json
ERROR - Please set 'server.api_key' to your Jellyfin API key
ERROR - Get an API key from: Jellyfin Dashboard → API Keys
```

**Solution:** Edit your config file and add a valid API key.

### Error: Connection Refused

```
ERROR - Cannot connect to Jellyfin server. Please check:
ERROR -   - Server URL: http://localhost:8096
ERROR -   - API key is valid
ERROR -   - Server is running and accessible
```

**Solution:** Verify Jellyfin is running and the URL is correct.

### Error: Library Missing Name

```
ERROR - Library configuration missing required 'name' field
```

**Solution:** Add a `"name"` field to each library in your config.

## Tips and Best Practices

1. **Always use dry-run first**:
   ```bash
   python3 configure_jellyfin.py --dry-run
   ```

2. **Use verbose mode for debugging**:
   ```bash
   python3 configure_jellyfin.py --dry-run --verbose
   ```

3. **Keep your config in version control** (but gitignore the API key):
   ```bash
   git add jellyfin.config.example.json
   # Don't add jellyfin.config.json (contains API key)
   ```

4. **Test with one library first**:
   Start with a simple config with just one library, verify it works, then add more.

5. **Back up your config**:
   ```bash
   cp jellyfin.config.json jellyfin.config.backup.json
   ```

## Advanced Usage

### Environment Variables for API Key

Instead of storing the API key in the config file, you could modify the script to read from an environment variable:

```bash
export JELLYFIN_API_KEY="your-api-key"
python3 configure_jellyfin.py
```

### Multiple Configurations

Maintain different configs for different environments:

```bash
python3 configure_jellyfin.py --config configs/production.json
python3 configure_jellyfin.py --config configs/staging.json
python3 configure_jellyfin.py --config configs/development.json
```

### Automation with Cron

Schedule regular configuration checks:

```cron
# Check configuration daily at 2 AM
0 2 * * * cd /path/to/repo && python3 configure_jellyfin.py --dry-run > /var/log/jellyfin-config.log 2>&1
```

## Reference

For more information, see:
- [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) - Detailed configuration reference
- [README.md](README.md) - Project overview
- [jellyfin-config-plan.md](jellyfin-config-plan.md) - Configuration recommendations
