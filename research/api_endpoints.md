# Jellyfin API Endpoints Research

Based on https://api.jellyfin.org/

## Key API Endpoints for Configuration:

### Library Management
- **GET /Library/VirtualFolders** - Get all virtual folders/libraries
- **POST /Library/VirtualFolders** - Create a new library
  - Query params: name, collectionType, paths, refreshLibrary
- **DELETE /Library/VirtualFolders** - Remove a library
- **POST /Library/VirtualFolders/Name** - Rename a library
- **POST /Library/VirtualFolders/LibraryOptions** - Update library options
  - This is the key endpoint for detailed library configuration

### Library Options Structure
The LibraryOptions contain:
- EnablePhotos, EnableRealtimeMonitor, EnableChapterImageExtraction
- MetadataCountryCode, PreferredMetadataLanguage
- PathInfos (folder paths)
- TypeOptions (metadata fetchers, image fetchers, etc.)

### System Configuration
- **GET /System/Configuration** - Get server configuration
- **POST /System/Configuration** - Update server configuration

### Scheduled Tasks
- **GET /ScheduledTasks** - Get all scheduled tasks
- **GET /ScheduledTasks/{taskId}** - Get specific task
- **POST /ScheduledTasks/Running/{taskId}** - Start a task
- **DELETE /ScheduledTasks/Running/{taskId}** - Stop a task
- **POST /ScheduledTasks/{taskId}/Triggers** - Update task triggers

### Authentication
- **POST /Users/AuthenticateByName** - Authenticate with username/password
- API Key can be used via X-Emby-Token header

## Important Notes:
1. Library detailed settings are in LibraryOptions
2. TypeOptions contains metadata fetchers, image fetchers priorities
3. Scheduled task triggers control when tasks run
4. Some settings may require restart to take effect
