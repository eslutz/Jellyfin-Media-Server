# Jellyfin API Research Notes

## Key Points:
1. Jellyfin provides a REST API for configuration
2. API documentation: https://api.jellyfin.org/
3. Authentication via API key or username/password
4. Libraries are configured via the API endpoints
5. Scheduled tasks can be managed via API

## API Endpoints for Library Configuration:
- GET/POST /Library/VirtualFolders - Manage libraries
- GET/POST /ScheduledTasks - Manage scheduled tasks
- GET/POST /System/Configuration - System configuration

## Configuration Approach:
- Use Jellyfin API to programmatically set configuration
- Store desired state in jellyfin.config.json
- Python script reads config and applies via API calls
