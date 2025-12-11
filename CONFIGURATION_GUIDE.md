# Jellyfin Configuration Script

Automated configuration script for Jellyfin Media Server using Python 3 and the Jellyfin API.

## Overview

This script automates the configuration of Jellyfin Media Server instances based on the settings defined in `jellyfin-config-plan.md`. It uses the Jellyfin REST API to programmatically apply library settings, metadata configurations, and scheduled task settings.

## Features

- ✅ **Library Management**: Create and configure media libraries
- ✅ **Metadata Configuration**: Set metadata downloaders, image fetchers, and savers
- ✅ **Advanced Settings**: Configure language, country, chapter images, and trickplay
- ✅ **Scheduled Tasks**: Automate library scans, chapter extraction, and intro detection
- ✅ **Dry Run Mode**: Preview changes before applying them

## Requirements

- Python 3.6 or higher
- `requests` and `python-dotenv` libraries
- Jellyfin Media Server (any recent version)

## Installation

```bash
pip3 install -r requirements.txt
```

## Configuration

### 1. Get Your Jellyfin API Key

If you haven't completed the initial setup wizard yet:
1. Access your Jellyfin server web interface
2. Complete the initial setup wizard (create admin account, set up libraries, etc.)

Once the server is set up:
1. Log into your Jellyfin server web interface
2. Click on your **user icon** (top right) → **Dashboard**
3. In the left sidebar under **Advanced**, click **API Keys**
4. Click the **+** button to create a new API key
5. Give it a name (e.g., "Configuration Script")
6. Copy the generated API key

### 2. Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your values:
   ```bash
   JELLYFIN_URL=http://localhost:8096
   JELLYFIN_API_KEY=your_actual_api_key_here
   ```

### 3. Configure Library Settings

The `jellyfin.config.json` file contains all library and scheduled task configurations. Edit this file to customize:

- Library names and folder paths
- Metadata downloader priorities
- Image fetcher settings
- Advanced options (language, country, chapter images, trickplay)
- Scheduled task intervals

See `jellyfin-config-plan.md` for detailed configuration recommendations.

## Usage

### Basic Usage

Apply the configuration:
```bash
python3 configure_jellyfin.py
```

### Dry Run Mode

Preview changes without making actual changes:
```bash
python3 configure_jellyfin.py --dry-run
```

### Verbose Output

Enable detailed logging:
```bash
python3 configure_jellyfin.py --verbose
```

### Custom Configuration File

Use a different configuration file:
```bash
python3 configure_jellyfin.py --config custom-config.json
```

## API Reference

This script uses the Jellyfin REST API. For detailed API documentation, see:
https://api.jellyfin.org/

The implementation is based on the **Jellyfin OpenAPI stable specification** and follows the official API contract for:

- **Authentication**: X-Emby-Token header with API key
- **Library Management**: `/Library/VirtualFolders` endpoints
- **Library Options**: `/Library/VirtualFolders/LibraryOptions` for detailed configuration
- **Scheduled Tasks**: `/ScheduledTasks` endpoints for task management
- **Task Triggers**: `/ScheduledTasks/{taskId}/Triggers` for scheduling

### Key API Endpoints

- `GET /System/Info` - Connection testing
- `GET /Library/VirtualFolders` - List libraries
- `POST /Library/VirtualFolders` - Create library
- `POST /Library/VirtualFolders/LibraryOptions` - Configure library settings
- `GET /ScheduledTasks` - List scheduled tasks
- `POST /ScheduledTasks/{taskId}/Triggers` - Configure task triggers

## Troubleshooting

### Connection Failed
```
Failed to connect to Jellyfin server
```

**Solutions:**
- Verify the server URL in your `.env` file
- Ensure Jellyfin server is running
- Check that the server is accessible from your machine
- Verify firewall settings

### Authentication Failed
```
API request failed: 401 Unauthorized
```

**Solutions:**
- Verify your API key in the `.env` file
- Regenerate API key in Jellyfin Dashboard
- Ensure the API key hasn't been deleted or expired

### Environment Variables Not Found
```
API key not found in environment variables
```

**Solutions:**
- Ensure `.env` file exists in the same directory as the script
- Verify `.env` file has the correct format (see `.env.example`)
- Check that `JELLYFIN_API_KEY` is set in the `.env` file

## Security Notes

- **API Key Security**: Keep your API key secure. The `.env` file is gitignored by default.
- **Don't commit secrets**: Never commit the `.env` file to version control
- **Use HTTPS**: For production, use HTTPS URLs for your Jellyfin server

## Support

For issues related to:
- **This script**: Check the troubleshooting section above
- **Jellyfin API**: See https://api.jellyfin.org/
- **Jellyfin server**: See https://jellyfin.org/docs/
