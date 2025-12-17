#!/usr/bin/env python3
"""
Jellyfin Global Configuration Script

This script reads configuration from jellyfin.config.json and applies only
global Jellyfin settings via the API. Scope is intentionally limited to
server-wide options (e.g., Quick Connect disablement and TrickplayOptions).

API Documentation: https://api.jellyfin.org/
OpenAPI Specification: Based on jellyfin-openapi-stable.json

The implementation follows the Jellyfin OpenAPI specification for:
- Authentication via X-Emby-Token header
- Global configuration endpoints (/System/Configuration)

Usage:
    python3 configure_jellyfin.py [--config jellyfin.config.json] [--dry-run]

Requirements:
    - Python 3.6+
    - requests library (install with: pip3 install requests)
    - python-dotenv library (install with: pip3 install python-dotenv)
    - .env file with JELLYFIN_URL and JELLYFIN_API_KEY
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, Optional
import requests
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JellyfinConfigurator:
    """Handles global configuration of a Jellyfin server via API."""

    def __init__(self, server_url: str, api_key: str, dry_run: bool = False):
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
                timeout=30,
                verify=True
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
        """Verify connectivity to the Jellyfin server."""
        logger.info(f"Testing connection to {self.server_url}...")
        result = self._make_request('GET', '/System/Info')
        if result:
            logger.info(f"Connected to Jellyfin {result.get('Version', 'Unknown')}")
            return True
        logger.error("Failed to connect to Jellyfin server")
        return False

    def disable_quick_connect(self) -> bool:
        """Disable Quick Connect via the system configuration endpoint."""
        logger.info("Ensuring Quick Connect is disabled...")

        config = self._make_request('GET', '/System/Configuration')
        if config is None:
            logger.error("Unable to load system configuration")
            return False

        if not config.get('QuickConnectAvailable', False):
            logger.info("Quick Connect already disabled")
            return True

        config['QuickConnectAvailable'] = False

        result = self._make_request('POST', '/System/Configuration', data=config)
        if result is not None:
            logger.info("Quick Connect disabled")
            return True

        logger.error("Failed to disable Quick Connect")
        return False

    def configure_global_trickplay(self, trickplay_options: Dict) -> bool:
        """Merge provided TrickplayOptions into /System/Configuration."""
        if not trickplay_options:
            return True

        cfg = self._make_request('GET', '/System/Configuration')
        if cfg is None:
            logger.error("Unable to load system configuration for TrickplayOptions")
            return False

        existing = cfg.get('TrickplayOptions') or {}
        updated = dict(existing)
        updated.update(trickplay_options)

        if updated == existing:
            logger.info("Global TrickplayOptions already up to date")
            return True

        cfg['TrickplayOptions'] = updated
        result = self._make_request('POST', '/System/Configuration', data=cfg)
        if result is not None:
            logger.info("Global TrickplayOptions updated")
            return True

        logger.error("Failed to update Global TrickplayOptions")
        return False

    def apply_configuration(self, config: Dict) -> bool:
        """Apply global configuration values from the provided config."""
        success = True

        if not self.disable_quick_connect():
            success = False

        try:
            if 'trickplay_options' in config:
                if not self.configure_global_trickplay(config['trickplay_options']):
                    success = False
        except Exception as e:
            logger.warning(f"TrickplayOptions setup encountered an issue: {e}")

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

        # Get server configuration from environment variables
        server_url = os.getenv('JELLYFIN_URL', 'http://localhost:8096')
        api_key = os.getenv('JELLYFIN_API_KEY', '')

        if not api_key:
            logger.error("API key not found in environment variables")
            logger.error("Please set JELLYFIN_API_KEY in your .env file")
            logger.error("Copy .env.example to .env and fill in your API key")
            logger.error("Get an API key from: Jellyfin Dashboard → API Keys")
            sys.exit(1)

        logger.info(f"Using Jellyfin server at: {server_url}")

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
            logger.error("  - Check your .env file configuration")
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
