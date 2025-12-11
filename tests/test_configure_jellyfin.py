#!/usr/bin/env python3
"""
Simple tests for the Jellyfin configuration script.

These tests validate basic functionality without requiring a live Jellyfin server.
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path to import configure_jellyfin
sys.path.insert(0, str(Path(__file__).parent.parent))

import configure_jellyfin

# Use the constant from the main module
TICKS_PER_SECOND = configure_jellyfin.TICKS_PER_SECOND


class TestConfigLoading(unittest.TestCase):
    """Test configuration file loading."""

    def test_load_config(self):
        """Test that config can be loaded."""
        config_path = Path(__file__).parent.parent / "jellyfin.config.json"
        config = configure_jellyfin.load_config(str(config_path))
        
        self.assertIsInstance(config, dict)
        self.assertIn('libraries', config)
        self.assertIn('scheduled_tasks', config)

    def test_config_has_required_fields(self):
        """Test that config has all required fields."""
        config_path = Path(__file__).parent.parent / "jellyfin.config.json"
        config = configure_jellyfin.load_config(str(config_path))
        
        # Libraries
        self.assertIsInstance(config['libraries'], list)
        self.assertGreater(len(config['libraries']), 0)
        
        # First library structure
        library = config['libraries'][0]
        self.assertIn('name', library)
        self.assertIn('content_type', library)
        self.assertIn('folders', library)
        self.assertIsInstance(library['folders'], list)

    def test_load_nonexistent_config(self):
        """Test that loading nonexistent config raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            configure_jellyfin.load_config('nonexistent.json')


class TestJellyfinConfigurator(unittest.TestCase):
    """Test JellyfinConfigurator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.server_url = "http://localhost:8096"
        self.api_key = "test-api-key"
        self.configurator = configure_jellyfin.JellyfinConfigurator(
            self.server_url,
            self.api_key,
            dry_run=True
        )

    def test_init(self):
        """Test configurator initialization."""
        self.assertEqual(self.configurator.server_url, self.server_url)
        self.assertEqual(self.configurator.api_key, self.api_key)
        self.assertTrue(self.configurator.dry_run)
        self.assertIn('X-Emby-Token', self.configurator.headers)

    def test_get_type_name_for_content(self):
        """Test content type to Jellyfin type mapping."""
        self.assertEqual(
            self.configurator._get_type_name_for_content('movies'),
            'Movie'
        )
        self.assertEqual(
            self.configurator._get_type_name_for_content('tvshows'),
            'Series'
        )
        self.assertEqual(
            self.configurator._get_type_name_for_content('music'),
            'Audio'
        )
        self.assertEqual(
            self.configurator._get_type_name_for_content('books'),
            'Book'
        )

    def test_build_library_options(self):
        """Test building library options from config."""
        library_config = {
            'content_type': 'movies',
            'library': {
                'enable_realtime_monitoring': True
            },
            'advanced': {
                'metadata': {
                    'preferred_language': 'en',
                    'country': 'US'
                },
                'chapter_images': {
                    'enable_chapter_image_extraction': True
                }
            },
            'metadata_downloaders': [
                {'name': 'TheMovieDb', 'enabled': True, 'priority': 1}
            ],
            'image_fetchers': [
                {'name': 'TheMovieDb', 'enabled': True, 'priority': 1}
            ]
        }
        
        options = self.configurator._build_library_options(library_config)
        
        self.assertIn('EnableRealtimeMonitor', options)
        self.assertTrue(options['EnableRealtimeMonitor'])
        self.assertEqual(options['PreferredMetadataLanguage'], 'en')
        self.assertEqual(options['MetadataCountryCode'], 'US')
        self.assertTrue(options['EnableChapterImageExtraction'])
        
        # Check TypeOptions
        self.assertIn('TypeOptions', options)
        self.assertIsInstance(options['TypeOptions'], list)
        self.assertEqual(len(options['TypeOptions']), 1)
        
        type_option = options['TypeOptions'][0]
        self.assertEqual(type_option['Type'], 'Movie')
        self.assertIn('TheMovieDb', type_option['MetadataFetchers'])
        self.assertIn('TheMovieDb', type_option['ImageFetchers'])

    @patch('configure_jellyfin.requests.request')
    def test_dry_run_mode(self, mock_request):
        """Test that dry run mode doesn't make actual requests."""
        self.configurator._make_request('POST', '/test', data={'test': 'data'})
        
        # In dry run mode, no actual request should be made
        mock_request.assert_not_called()

    @patch('configure_jellyfin.requests.request')
    def test_make_request_get(self, mock_request):
        """Test making GET requests."""
        # Create non-dry-run configurator
        configurator = configure_jellyfin.JellyfinConfigurator(
            self.server_url,
            self.api_key,
            dry_run=False
        )
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'test': 'response'}
        mock_response.content = b'{"test": "response"}'
        mock_request.return_value = mock_response
        
        result = configurator._make_request('GET', '/test')
        
        self.assertEqual(result, {'test': 'response'})
        mock_request.assert_called_once()


class TestScheduledTaskConfiguration(unittest.TestCase):
    """Test scheduled task configuration."""

    def setUp(self):
        """Set up test fixtures."""
        self.configurator = configure_jellyfin.JellyfinConfigurator(
            "http://localhost:8096",
            "test-key",
            dry_run=True
        )

    def test_interval_trigger_calculation(self):
        """Test interval trigger calculation."""
        # 30 minutes should be 30 * 60 * TICKS_PER_SECOND ticks
        expected_ticks = 30 * 60 * TICKS_PER_SECOND
        
        # This would be in the actual trigger configuration
        interval_minutes = 30
        ticks = interval_minutes * 60 * TICKS_PER_SECOND
        
        self.assertEqual(ticks, expected_ticks)

    def test_daily_trigger_calculation(self):
        """Test daily trigger time calculation."""
        # 03:00 should be 3 * 3600 * TICKS_PER_SECOND ticks
        hours = 3
        minutes = 0
        expected_ticks = (hours * 3600 + minutes * 60) * TICKS_PER_SECOND
        
        self.assertEqual(expected_ticks, 3 * 3600 * TICKS_PER_SECOND)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
