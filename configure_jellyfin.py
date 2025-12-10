#!/usr/bin/env python3
"""
Jellyfin Configuration Script

This script reads configuration from jellyfin.config.json and applies it to a
Jellyfin media server instance via the Jellyfin API.

Based on the configuration plan in jellyfin-config-plan.md, this script automates:
- Library creation and configuration
- Metadata downloader settings
- Image fetcher settings
- Metadata saver settings
- Advanced settings (language, country, chapter images, trickplay)
- Scheduled task configuration

API Documentation: https://api.jellyfin.org/

Usage:
    python3 configure_jellyfin.py [--config jellyfin.config.json] [--dry-run]

Requirements:
    - Python 3.6+
    - requests library (install with: pip3 install requests)
"""

import argparse
import json
import logging
import sys
from typing import Dict, List, Any, Optional
import requests
from pathlib import Path


# Constants
TICKS_PER_SECOND = 10000000  # Windows/Jellyfin ticks are 100-nanosecond intervals


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JellyfinConfigurator:
    """Handles configuration of a Jellyfin server via API."""

    def __init__(self, server_url: str, api_key: str, dry_run: bool = False):
        """
        Initialize the Jellyfin configurator.

        Args:
            server_url: Base URL of the Jellyfin server (e.g., http://localhost:8096)
            api_key: API key for authentication
            dry_run: If True, only log actions without making changes
        """
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.dry_run = dry_run
        self.headers = {
            'X-Emby-Token': api_key,
            'Content-Type': 'application/json'
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make an API request to Jellyfin.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data (for POST/PUT)
            params: Query parameters

        Returns:
            Response data as dictionary, or None if request failed
        """
        url = f"{self.server_url}/{endpoint.lstrip('/')}"
        
        if self.dry_run and method.upper() != 'GET':
            logger.info(f"[DRY RUN] Would {method} {url}")
            if data:
                logger.info(f"[DRY RUN] With data: {json.dumps(data, indent=2)}")
            return {}

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None

    def test_connection(self) -> bool:
        """
        Test connection to Jellyfin server.

        Returns:
            True if connection successful, False otherwise
        """
        logger.info(f"Testing connection to {self.server_url}...")
        result = self._make_request('GET', '/System/Info')
        if result:
            logger.info(f"Connected to Jellyfin {result.get('Version', 'Unknown')}")
            return True
        logger.error("Failed to connect to Jellyfin server")
        return False

    def get_libraries(self) -> List[Dict]:
        """
        Get existing libraries from Jellyfin.

        Returns:
            List of library dictionaries
        """
        result = self._make_request('GET', '/Library/VirtualFolders')
        return result if result else []

    def get_library_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a library by its name.

        Args:
            name: Library name to search for

        Returns:
            Library dictionary if found, None otherwise
        """
        libraries = self.get_libraries()
        for library in libraries:
            if library.get('Name') == name:
                return library
        return None

    def create_or_update_library(self, library_config: Dict) -> bool:
        """
        Create or update a library based on configuration.

        Args:
            library_config: Library configuration dictionary

        Returns:
            True if successful, False otherwise
        """
        name = library_config.get('name')
        logger.info(f"Configuring library: {name}")

        existing_library = self.get_library_by_name(name)
        
        if existing_library:
            logger.info(f"Library '{name}' already exists, updating configuration...")
            return self._update_library(existing_library, library_config)
        else:
            logger.info(f"Creating new library '{name}'...")
            return self._create_library(library_config)

    def _create_library(self, library_config: Dict) -> bool:
        """
        Create a new library.

        Args:
            library_config: Library configuration dictionary

        Returns:
            True if successful, False otherwise
        """
        name = library_config.get('name')
        content_type = library_config.get('content_type', 'movies')
        folders = library_config.get('folders', [])

        # Map content type to Jellyfin collection type
        collection_type_map = {
            'movies': 'movies',
            'tvshows': 'tvshows',
            'music': 'music',
            'books': 'books'
        }
        collection_type = collection_type_map.get(content_type, 'movies')

        # Create library with basic settings
        # Note: The API expects multiple 'paths' parameters for multiple folders
        params = {
            'name': name,
            'collectionType': collection_type,
            'refreshLibrary': False
        }

        # For multiple folders, we need to add them one at a time via separate API calls
        # or use the proper array format for the API
        if folders:
            # Use the first folder for initial creation
            params['paths'] = folders[0]

        result = self._make_request('POST', '/Library/VirtualFolders', params=params)
        if result is not None:
            logger.info(f"Library '{name}' created successfully")
            
            # TODO: Add additional folders if there are more than one
            # This may require additional API calls to add paths
            if len(folders) > 1:
                logger.warning(f"Multiple folders detected. Only first folder added.")
                logger.warning(f"Additional folders may need to be added manually: {folders[1:]}")
            
            # Apply additional configuration settings
            return self._apply_library_settings(name, library_config)
        
        logger.error(f"Failed to create library '{name}'")
        return False

    def _update_library(self, existing_library: Dict, library_config: Dict) -> bool:
        """
        Update an existing library.

        Args:
            existing_library: Existing library data from API
            library_config: New library configuration

        Returns:
            True if successful, False otherwise
        """
        name = library_config.get('name')
        logger.info(f"Updating library '{name}' settings...")
        
        # Apply library settings
        return self._apply_library_settings(name, library_config)

    def _apply_library_settings(self, library_name: str, library_config: Dict) -> bool:
        """
        Apply detailed library settings using LibraryOptions API.

        Uses the /Library/VirtualFolders/LibraryOptions endpoint to configure
        detailed library settings including metadata fetchers, image fetchers, etc.

        API Reference: https://api.jellyfin.org/#tag/Library/operation/UpdateLibraryOptions

        Args:
            library_name: Name of the library
            library_config: Configuration to apply

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Applying settings for library '{library_name}'...")
        
        # Get the library to retrieve its ItemId
        library = self.get_library_by_name(library_name)
        if not library:
            logger.error(f"Cannot find library '{library_name}'")
            return False

        # Build LibraryOptions object
        library_options = self._build_library_options(library_config)
        
        # Log the settings that will be applied
        if library_config.get('metadata_downloaders'):
            logger.info(f"  Metadata downloaders: {[m['name'] for m in library_config['metadata_downloaders'] if m.get('enabled', True)]}")
        
        if library_config.get('image_fetchers'):
            logger.info(f"  Image fetchers: {[f['name'] for f in library_config['image_fetchers'] if f.get('enabled', True)]}")
        
        if library_config.get('metadata_savers'):
            logger.info(f"  Metadata savers: {[s['name'] for s in library_config['metadata_savers'] if s.get('enabled', True)]}")
        
        advanced = library_config.get('advanced', {})
        if advanced.get('metadata'):
            metadata = advanced['metadata']
            logger.info(f"  Language: {metadata.get('preferred_language')}")
            logger.info(f"  Country: {metadata.get('country')}")
        
        if advanced.get('chapter_images', {}).get('enable_chapter_image_extraction'):
            logger.info("  Chapter image extraction: ENABLED")
        
        if advanced.get('trickplay', {}).get('enable_trickplay_extraction'):
            logger.info("  Trickplay extraction: ENABLED")
        
        # Apply library options via API
        # Note: The exact API endpoint and payload structure may vary by Jellyfin version
        # This implementation is based on Jellyfin API documentation at https://api.jellyfin.org/
        
        params = {
            'id': library.get('ItemId')
        }
        
        result = self._make_request(
            'POST',
            '/Library/VirtualFolders/LibraryOptions',
            data=library_options,
            params=params
        )
        
        if result is not None:
            logger.info(f"Library options applied successfully for '{library_name}'")
            return True
        else:
            logger.warning(f"Failed to apply library options for '{library_name}'")
            logger.warning("This may require manual configuration in Jellyfin UI")
            return False

    def _build_library_options(self, library_config: Dict) -> Dict:
        """
        Build LibraryOptions object from configuration.

        Args:
            library_config: Library configuration dictionary

        Returns:
            LibraryOptions dictionary for API
        """
        options = {}
        
        # Basic library settings
        library_settings = library_config.get('library', {})
        if 'enable_realtime_monitoring' in library_settings:
            options['EnableRealtimeMonitor'] = library_settings['enable_realtime_monitoring']
        
        # Advanced settings
        advanced = library_config.get('advanced', {})
        
        # Metadata settings
        if advanced.get('metadata'):
            metadata = advanced['metadata']
            if 'preferred_language' in metadata:
                options['PreferredMetadataLanguage'] = metadata['preferred_language']
            if 'country' in metadata:
                options['MetadataCountryCode'] = metadata['country']
            if 'automatically_refresh_metadata' in metadata:
                options['AutomaticallyAddToCollection'] = metadata['automatically_refresh_metadata']
            if 'save_artwork_into_media_folders' in metadata:
                options['SaveLocalMetadata'] = metadata['save_artwork_into_media_folders']
        
        # Chapter images
        if advanced.get('chapter_images'):
            chapter_settings = advanced['chapter_images']
            if 'enable_chapter_image_extraction' in chapter_settings:
                options['EnableChapterImageExtraction'] = chapter_settings['enable_chapter_image_extraction']
            if 'extract_during_library_scan' in chapter_settings:
                options['ExtractChapterImagesDuringLibraryScan'] = chapter_settings['extract_during_library_scan']
        
        # Trickplay (may not be in standard API, depends on Jellyfin version)
        if advanced.get('trickplay'):
            trickplay_settings = advanced['trickplay']
            if 'enable_trickplay_extraction' in trickplay_settings:
                options['EnableTrickplayImageExtraction'] = trickplay_settings['enable_trickplay_extraction']
        
        # Image settings
        if advanced.get('images'):
            image_settings = advanced['images']
            if 'skip_images_if_nfo_exists' in image_settings:
                # Note: This setting may not be directly supported via LibraryOptions API
                # The actual implementation depends on Jellyfin version
                # Skipping this setting to avoid API errors
                logger.debug("Image skip setting noted but not applied via API (may require manual config)")
                pass
        
        # TypeOptions for metadata/image fetchers
        # This is a complex structure that needs to be built based on content type
        type_options = []
        
        # Build type option for the content type
        content_type = library_config.get('content_type', 'movies')
        type_name = self._get_type_name_for_content(content_type)
        
        type_option = {
            'Type': type_name,
            'MetadataFetchers': [],
            'ImageFetchers': [],
            'MetadataSavers': []
        }
        
        # Add metadata downloaders
        if library_config.get('metadata_downloaders'):
            for downloader in sorted(
                library_config['metadata_downloaders'],
                key=lambda x: x.get('priority', 999)
            ):
                if downloader.get('enabled', True):
                    type_option['MetadataFetchers'].append(downloader['name'])
        
        # Add image fetchers
        if library_config.get('image_fetchers'):
            for fetcher in sorted(
                library_config['image_fetchers'],
                key=lambda x: x.get('priority', 999)
            ):
                if fetcher.get('enabled', True):
                    type_option['ImageFetchers'].append(fetcher['name'])
        
        # Add metadata savers
        if library_config.get('metadata_savers'):
            for saver in library_config['metadata_savers']:
                if saver.get('enabled', True):
                    type_option['MetadataSavers'].append(saver['name'])
        
        type_options.append(type_option)
        options['TypeOptions'] = type_options
        
        return options

    def _get_type_name_for_content(self, content_type: str) -> str:
        """
        Get Jellyfin type name for content type.

        Args:
            content_type: Content type from config (movies, tvshows, etc.)

        Returns:
            Jellyfin type name
        """
        type_map = {
            'movies': 'Movie',
            'tvshows': 'Series',
            'music': 'Audio',
            'books': 'Book'
        }
        return type_map.get(content_type, 'Movie')

    def configure_scheduled_tasks(self, tasks_config: Dict) -> bool:
        """
        Configure scheduled tasks.

        Args:
            tasks_config: Scheduled tasks configuration

        Returns:
            True if successful, False otherwise
        """
        logger.info("Configuring scheduled tasks...")
        
        # Get current scheduled tasks
        current_tasks = self._make_request('GET', '/ScheduledTasks')
        if current_tasks is None:
            logger.error("Failed to retrieve scheduled tasks")
            return False

        # Map of task names to configuration
        task_mapping = {
            'scan_media_library': 'Scan Media Library',
            'extract_chapter_images': 'Extract Chapter Images',
            'trickplay_image_extraction': 'Trickplay Image Extraction',
            'generate_intro_skip_data': 'Detect Intros'
        }

        for config_key, task_name in task_mapping.items():
            if config_key in tasks_config:
                task_config = tasks_config[config_key]
                self._configure_scheduled_task(
                    current_tasks,
                    task_name,
                    task_config
                )

        logger.info("Scheduled tasks configuration complete")
        return True

    def _configure_scheduled_task(
        self,
        current_tasks: List[Dict],
        task_name: str,
        task_config: Dict
    ) -> bool:
        """
        Configure a specific scheduled task using Jellyfin API.

        Uses the /ScheduledTasks/{taskId}/Triggers endpoint to configure task schedules.
        API Reference: https://api.jellyfin.org/#tag/ScheduledTasks

        Args:
            current_tasks: List of current tasks from API
            task_name: Name of the task to configure
            task_config: Configuration for the task

        Returns:
            True if successful, False otherwise
        """
        # Find the task
        task = None
        for t in current_tasks:
            if task_name.lower() in t.get('Name', '').lower():
                task = t
                break

        if not task:
            logger.warning(f"Task '{task_name}' not found in scheduled tasks")
            return False

        task_id = task.get('Key') or task.get('Id')
        enabled = task_config.get('enabled', True)
        
        logger.info(f"Configuring task '{task_name}' (ID: {task_id})")
        
        if not enabled:
            logger.info(f"  Task disabled - removing triggers")
            # Remove all triggers to disable
            result = self._make_request(
                'POST',
                f'/ScheduledTasks/{task_id}/Triggers',
                data=[]
            )
            return result is not None
        
        # Build triggers based on configuration
        triggers = []
        
        if 'interval_minutes' in task_config:
            interval = task_config['interval_minutes']
            logger.info(f"  Setting interval: {interval} minutes")
            triggers.append({
                'Type': 'IntervalTrigger',
                'IntervalTicks': interval * 60 * TICKS_PER_SECOND
            })
        
        elif 'schedule' in task_config and task_config['schedule'] == 'daily':
            time_str = task_config.get('time', '03:00')
            logger.info(f"  Setting daily schedule at {time_str}")
            
            # Parse time (format: HH:MM)
            try:
                hours, minutes = map(int, time_str.split(':'))
                triggers.append({
                    'Type': 'DailyTrigger',
                    'TimeOfDayTicks': (hours * 3600 + minutes * 60) * TICKS_PER_SECOND
                })
            except ValueError:
                logger.error(f"Invalid time format: {time_str}. Expected HH:MM")
                return False
        
        # Apply triggers
        if triggers:
            result = self._make_request(
                'POST',
                f'/ScheduledTasks/{task_id}/Triggers',
                data=triggers
            )
            
            if result is not None:
                logger.info(f"Task '{task_name}' configured successfully")
                return True
            else:
                logger.error(f"Failed to configure task '{task_name}'")
                return False
        else:
            logger.info(f"Task '{task_name}' - no triggers configured")
            return True

    def apply_configuration(self, config: Dict) -> bool:
        """
        Apply full configuration from config dictionary.

        Args:
            config: Complete configuration dictionary

        Returns:
            True if all configurations applied successfully
        """
        success = True

        # Configure libraries
        if 'libraries' in config:
            logger.info(f"Configuring {len(config['libraries'])} libraries...")
            for library_config in config['libraries']:
                if not self.create_or_update_library(library_config):
                    success = False

        # Configure scheduled tasks
        if 'scheduled_tasks' in config:
            if not self.configure_scheduled_tasks(config['scheduled_tasks']):
                success = False

        return success


def load_config(config_path: str) -> Dict:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    logger.info(f"Loading configuration from {config_path}")
    
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(path, 'r') as f:
        config = json.load(f)
    
    logger.info("Configuration loaded successfully")
    return config


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Configure Jellyfin server from JSON configuration file'
    )
    parser.add_argument(
        '--config',
        default='jellyfin.config.json',
        help='Path to configuration file (default: jellyfin.config.json)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        # Load configuration
        config = load_config(args.config)

        # Extract server configuration
        server_config = config.get('server', {})
        server_url = server_config.get('url', 'http://localhost:8096')
        api_key = server_config.get('api_key', '')

        if not api_key or api_key == 'YOUR_API_KEY_HERE':
            logger.error("API key not configured in jellyfin.config.json")
            logger.error("Please set 'server.api_key' to your Jellyfin API key")
            logger.error("Get an API key from: Jellyfin Dashboard → API Keys")
            sys.exit(1)

        # Create configurator
        configurator = JellyfinConfigurator(
            server_url=server_url,
            api_key=api_key,
            dry_run=args.dry_run
        )

        # Test connection
        if not configurator.test_connection():
            logger.error("Cannot connect to Jellyfin server. Please check:")
            logger.error(f"  - Server URL: {server_url}")
            logger.error("  - API key is valid")
            logger.error("  - Server is running and accessible")
            sys.exit(1)

        # Apply configuration
        logger.info("=" * 60)
        logger.info("Starting Jellyfin configuration...")
        logger.info("=" * 60)

        if args.dry_run:
            logger.info("DRY RUN MODE - No changes will be made")

        success = configurator.apply_configuration(config)

        logger.info("=" * 60)
        if success:
            logger.info("Configuration completed successfully!")
        else:
            logger.warning("Configuration completed with some warnings")
        logger.info("=" * 60)

        sys.exit(0 if success else 1)

    except FileNotFoundError as e:
        logger.error(f"Configuration file error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nConfiguration interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
