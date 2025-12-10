# Jellyfin OpenAPI Specification Reference

## Overview

This document references the official Jellyfin OpenAPI specification to ensure accurate API integration.

Official API Documentation: https://api.jellyfin.org/

## Note on OpenAPI Specification

The user has provided a reference to `jellyfin-openapi-stable.json` which contains the complete OpenAPI 3.0 specification for Jellyfin's REST API. This specification should be used to:

1. Validate endpoint paths and HTTP methods
2. Ensure correct request/response formats
3. Verify parameter names and types
4. Check authentication requirements

## Key Endpoints Used in This Implementation

Based on the Jellyfin OpenAPI specification, the following endpoints are used:

### System Endpoints

**GET /System/Info**
- Description: Gets information about the server
- Authentication: Required (API Key via X-Emby-Token header)
- Response: System information including server version
- Used for: Connection testing

### Library Management Endpoints

**GET /Library/VirtualFolders**
- Description: Gets all virtual folders (libraries)
- Authentication: Required
- Response: Array of virtual folder objects
- Used for: Listing existing libraries

**POST /Library/VirtualFolders**
- Description: Adds a virtual folder (library)
- Authentication: Required
- Query Parameters:
  - `name` (string, required): Library name
  - `collectionType` (string, optional): Type of library (movies, tvshows, music, books)
  - `paths` (string, optional): Media folder path
  - `refreshLibrary` (boolean, optional): Whether to refresh after creation
- Used for: Creating new libraries

**POST /Library/VirtualFolders/LibraryOptions**
- Description: Updates library options
- Authentication: Required
- Query Parameters:
  - `id` (string, required): Library ItemId
- Request Body: LibraryOptions object containing:
  - `EnablePhotos` (boolean)
  - `EnableRealtimeMonitor` (boolean)
  - `EnableChapterImageExtraction` (boolean)
  - `EnableTrickplayImageExtraction` (boolean)
  - `ExtractChapterImagesDuringLibraryScan` (boolean)
  - `PreferredMetadataLanguage` (string)
  - `MetadataCountryCode` (string)
  - `TypeOptions` (array): Configuration per content type
    - `Type` (string): Content type name
    - `MetadataFetchers` (array of strings): Ordered list of metadata providers
    - `ImageFetchers` (array of strings): Ordered list of image providers
    - `MetadataSavers` (array of strings): List of metadata savers
- Used for: Configuring library metadata and image settings

### Scheduled Tasks Endpoints

**GET /ScheduledTasks**
- Description: Get the list of scheduled tasks
- Authentication: Required
- Response: Array of scheduled task information
- Used for: Listing available tasks

**GET /ScheduledTasks/{taskId}**
- Description: Get task by id
- Authentication: Required
- Path Parameters:
  - `taskId` (string, required): Task ID
- Used for: Getting task details

**POST /ScheduledTasks/{taskId}/Triggers**
- Description: Update specified task triggers
- Authentication: Required
- Path Parameters:
  - `taskId` (string, required): Task ID
- Request Body: Array of TaskTriggerInfo objects:
  - `Type` (string): Trigger type (DailyTrigger, IntervalTrigger, etc.)
  - `TimeOfDayTicks` (integer): For daily triggers, time in ticks
  - `IntervalTicks` (integer): For interval triggers, interval in ticks
- Used for: Configuring when tasks run

**POST /ScheduledTasks/Running/{taskId}**
- Description: Start specified task
- Authentication: Required
- Used for: Manually triggering tasks

**DELETE /ScheduledTasks/Running/{taskId}**
- Description: Stop specified task
- Authentication: Required
- Used for: Stopping running tasks

## Authentication

All API requests require authentication via one of:
1. API Key in `X-Emby-Token` header (recommended for scripts)
2. Session token from user authentication

Current implementation uses API Key authentication with `X-Emby-Token` header.

## Content Types

Supported library collection types:
- `movies`: Movie library
- `tvshows`: TV show library
- `music`: Music library
- `books`: Book library
- `homevideos`: Home video library
- `musicvideos`: Music video library
- `photos`: Photo library
- `mixed`: Mixed content library

## Metadata and Image Providers

Common provider names (may vary by Jellyfin version and installed plugins):
- **TheMovieDb**: The Movie Database (movies)
- **TheTVDB**: The TVDB (TV shows)
- **The Open Movie Database**: OMDb
- **Fanart**: Fanart.tv
- **Tvmaze**: TVmaze
- **ScreenGrabber**: Extract images from video files
- **Nfo**: NFO file metadata saver

## Ticks Conversion

Jellyfin uses Windows ticks (100-nanosecond intervals) for time values:
- 1 second = 10,000,000 ticks
- 1 minute = 600,000,000 ticks
- 1 hour = 36,000,000,000 ticks

## Data Models

### LibraryOptions
```json
{
  "EnablePhotos": boolean,
  "EnableRealtimeMonitor": boolean,
  "EnableChapterImageExtraction": boolean,
  "EnableTrickplayImageExtraction": boolean,
  "ExtractChapterImagesDuringLibraryScan": boolean,
  "PathInfos": [
    {
      "Path": "string",
      "NetworkPath": "string"
    }
  ],
  "SaveLocalMetadata": boolean,
  "PreferredMetadataLanguage": "string",
  "MetadataCountryCode": "string",
  "SeasonZeroDisplayName": "string",
  "AutomaticallyAddToCollection": boolean,
  "TypeOptions": [
    {
      "Type": "string",
      "MetadataFetchers": ["string"],
      "MetadataFetcherOrder": ["string"],
      "ImageFetchers": ["string"],
      "ImageFetcherOrder": ["string"],
      "MetadataSavers": ["string"]
    }
  ]
}
```

### TaskTriggerInfo
```json
{
  "Type": "string",
  "TimeOfDayTicks": integer,
  "IntervalTicks": integer,
  "DayOfWeek": "string",
  "MaxRuntimeTicks": integer
}
```

## Implementation Notes

1. The current implementation correctly uses `X-Emby-Token` for authentication
2. Endpoint paths match the OpenAPI specification
3. LibraryOptions structure should include all available fields
4. Task trigger types should match the specification
5. Content type names should match Jellyfin's collection types

## Recommendations for Improvement

Based on the OpenAPI specification:

1. **Add support for PathInfos**: Instead of just using `paths` parameter, use the proper PathInfos structure in LibraryOptions
2. **Validate collection types**: Ensure only valid collection types are used
3. **Add error handling**: Use proper HTTP status code checking (200, 201, 204, 400, 401, 403, 404, etc.)
4. **Support all trigger types**: Add support for WeeklyTrigger, StartupTrigger, etc.
5. **Add library folder management**: Implement adding/removing paths from existing libraries
6. **Validate provider names**: Check that provider names exist before configuring

## Version Compatibility

The OpenAPI specification is version-specific. The implementation should:
- Check server version on connection
- Adjust API calls based on version if needed
- Warn about features not available in older versions

## References

- Official API Documentation: https://api.jellyfin.org/
- Jellyfin GitHub: https://github.com/jellyfin/jellyfin
- API Client Libraries: https://github.com/jellyfin/jellyfin-apiclient-python
