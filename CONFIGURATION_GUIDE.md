# Jellyfin Configuration Script

Automated configuration script for Jellyfin Media Server using Python 3 and the Jellyfin API.

## Overview

This script automates the configuration of Jellyfin Media Server instances based on the settings defined in `jellyfin-config-plan.md`. It uses the Jellyfin REST API (documented at https://api.jellyfin.org/) to programmatically apply library settings, metadata configurations, and scheduled task settings.

## Features

- ✅ **Library Management**: Create and configure media libraries
- ✅ **Metadata Configuration**: Set metadata downloaders, image fetchers, and savers
- ✅ **Advanced Settings**: Configure language, country, chapter images, and trickplay
- ✅ **Scheduled Tasks**: Automate library scans, chapter extraction, and intro detection
- ✅ **Dry Run Mode**: Preview changes before applying them
- ✅ **JSON Configuration**: Store all settings in `jellyfin.config.json`

## Requirements

- Python 3.6 or higher
- `requests` library

## Installation

1. Install Python 3 and pip (if not already installed)
2. Install the required Python package:

```bash
pip3 install requests
```

## Configuration

### 1. Get Your Jellyfin API Key

1. Log into your Jellyfin server
2. Navigate to **Dashboard → API Keys**
3. Click **+** to create a new API key
4. Give it a name (e.g., "Configuration Script")
5. Copy the generated API key

### 2. Configure `jellyfin.config.json`

Edit the `jellyfin.config.json` file and update:

```json
{
  "server": {
    "url": "http://localhost:8096",
    "api_key": "YOUR_API_KEY_HERE"
  },
  ...
}
```

Replace:
- `url`: Your Jellyfin server URL
- `api_key`: The API key you created in step 1

### 3. Customize Library Settings

The configuration file includes two example libraries (Movies and TV Shows). Customize them according to your needs:

```json
{
  "libraries": [
    {
      "name": "Movies",
      "content_type": "movies",
      "folders": ["/path/to/your/movies"],
      "metadata_downloaders": [...],
      "image_fetchers": [...],
      ...
    }
  ]
}
```

## Usage

### Basic Usage

Apply the configuration:

```bash
python3 configure_jellyfin.py
```

### Dry Run Mode

Preview what would be changed without making actual changes:

```bash
python3 configure_jellyfin.py --dry-run
```

### Custom Configuration File

Use a different configuration file:

```bash
python3 configure_jellyfin.py --config my-config.json
```

### Verbose Output

Enable detailed logging:

```bash
python3 configure_jellyfin.py --verbose
```

### Combined Options

```bash
python3 configure_jellyfin.py --config my-config.json --dry-run --verbose
```

## Configuration Reference

### Server Settings

```json
{
  "server": {
    "url": "http://localhost:8096",
    "api_key": "your-api-key-here",
    "comment": "Get API key from Jellyfin Dashboard → API Keys"
  }
}
```

### Library Configuration

Each library can have the following settings:

```json
{
  "name": "Movies",
  "content_type": "movies",  // movies, tvshows, music, books
  "folders": ["/path/to/media"],
  
  "display": {
    "display_missing_episodes": false,
    "display_specials": false
  },
  
  "library": {
    "enable_realtime_monitoring": true
  },
  
  "metadata_downloaders": [
    {
      "name": "TheMovieDb",  // or TheTVDB for TV shows
      "enabled": true,
      "priority": 1
    }
  ],
  
  "image_fetchers": [
    {
      "name": "TheMovieDb",
      "enabled": true,
      "priority": 1
    }
  ],
  
  "metadata_savers": [
    {
      "name": "Nfo",
      "enabled": true
    }
  ],
  
  "advanced": {
    "metadata": {
      "preferred_language": "en",
      "country": "US",
      "prefer_embedded_titles": false,
      "automatically_refresh_metadata": true,
      "save_artwork_into_media_folders": false,
      "replace_existing_images": true
    },
    "images": {
      "skip_images_if_nfo_exists": true
    },
    "chapter_images": {
      "enable_chapter_image_extraction": true,
      "extract_during_library_scan": true
    },
    "trickplay": {
      "enable_trickplay_extraction": true
    }
  }
}
```

### Scheduled Tasks Configuration

```json
{
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
      "libraries": ["TV Shows"],
      "schedule": "daily",
      "time": "03:00"
    }
  }
}
```

## Common Content Types

- **movies**: Movie libraries
- **tvshows**: TV Show libraries
- **music**: Music libraries
- **books**: Book libraries

## Common Metadata Downloaders

- **TheMovieDb**: Best for movies
- **TheTVDB**: Best for TV shows
- **The Open Movie Database**: Alternative/supplementary source

## Common Image Fetchers

- **TheMovieDb**: Primary source for movies
- **TheTVDB**: Primary source for TV shows
- **Fanart**: High-quality fan art
- **Screen Grabber**: Extract images from video (disable to save resources)

## Scheduled Task Types

- **scan_media_library**: Regular library scans for new content
- **extract_chapter_images**: Extract chapter images from videos
- **trickplay_image_extraction**: Generate timeline preview thumbnails
- **generate_intro_skip_data**: Detect TV show intros for skip functionality

## Troubleshooting

### Connection Failed

```
Failed to connect to Jellyfin server
```

**Solutions:**
- Verify the server URL is correct
- Ensure Jellyfin server is running
- Check that the server is accessible from your machine
- Verify firewall settings

### Authentication Failed

```
API request failed: 401 Unauthorized
```

**Solutions:**
- Verify your API key is correct
- Regenerate API key in Jellyfin Dashboard
- Update `api_key` in `jellyfin.config.json`

### Task Not Found

```
Task 'X' not found in scheduled tasks
```

**Solutions:**
- The task may not be available in your Jellyfin version
- Some tasks only appear after enabling related features
- Check task names in Jellyfin Dashboard → Scheduled Tasks

### Library Options Failed

```
Failed to apply library options
```

**Solutions:**
- Some options may not be available in older Jellyfin versions
- Try updating Jellyfin to the latest version
- Some settings may require manual configuration in the UI

## API Reference

This script uses the Jellyfin REST API. For detailed API documentation, see:
https://api.jellyfin.org/

The implementation is based on the **Jellyfin OpenAPI stable specification** (`jellyfin-openapi-stable.json`) and follows the official API contract for:

- **Authentication**: X-Emby-Token header with API key
- **Library Management**: `/Library/VirtualFolders` endpoints
- **Library Options**: `/Library/VirtualFolders/LibraryOptions` for detailed configuration
- **Scheduled Tasks**: `/ScheduledTasks` endpoints for task management
- **Task Triggers**: `/ScheduledTasks/{taskId}/Triggers` for scheduling

### OpenAPI Compliance

The script follows the OpenAPI specification for:
- Proper HTTP methods (GET, POST, DELETE)
- Correct request/response formats
- Required authentication headers
- Query parameters and request bodies
- Error handling and status codes

For the complete OpenAPI specification, refer to the official Jellyfin API documentation.

Key endpoints used:
- `GET/POST /Library/VirtualFolders` - Library management
- `POST /Library/VirtualFolders/LibraryOptions` - Library settings
- `GET /ScheduledTasks` - Scheduled task information
- `POST /ScheduledTasks/{taskId}/Triggers` - Task scheduling

## Examples

### Configure a Single Movie Library

```json
{
  "server": {
    "url": "http://192.168.1.100:8096",
    "api_key": "abc123..."
  },
  "libraries": [
    {
      "name": "Movies",
      "content_type": "movies",
      "folders": ["/mnt/movies"],
      "metadata_downloaders": [
        {"name": "TheMovieDb", "enabled": true, "priority": 1}
      ],
      "advanced": {
        "metadata": {
          "preferred_language": "en",
          "country": "US"
        },
        "trickplay": {
          "enable_trickplay_extraction": true
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

### Test Connection

```bash
python3 configure_jellyfin.py --dry-run --verbose
```

This will test the connection and show what would be configured without making changes.

## Security Notes

- **API Key Security**: Keep your API key secure. Don't commit it to version control.
- **Use `.gitignore`**: Add `jellyfin.config.json` to `.gitignore` if it contains sensitive data
- **Environment Variables**: Consider using environment variables for sensitive data

## Support

For issues related to:
- **This script**: Check the troubleshooting section above
- **Jellyfin API**: See https://api.jellyfin.org/
- **Jellyfin server**: See https://jellyfin.org/docs/

## License

This script is provided as-is for use with Jellyfin Media Server.
