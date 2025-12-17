#!/usr/bin/env python3
"""
Tests for the global-only Jellyfin configuration script.

These tests validate basic functionality without requiring a live Jellyfin server.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path to import configure_jellyfin
sys.path.insert(0, str(Path(__file__).parent.parent))

import configure_jellyfin


class TestConfigLoading(unittest.TestCase):
    """Test configuration file loading."""

    def test_load_config(self):
        config_path = Path(__file__).parent.parent / "jellyfin.config.json"
        config = configure_jellyfin.load_config(str(config_path))

        self.assertIsInstance(config, dict)
        self.assertIn('libraries', config)
        self.assertIn('scheduled_tasks', config)

    def test_load_nonexistent_config(self):
        with self.assertRaises(FileNotFoundError):
            configure_jellyfin.load_config('nonexistent.json')

    def test_load_invalid_json(self):
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content }")
            temp_path = f.name

        try:
            with self.assertRaises(Exception):
                configure_jellyfin.load_config(temp_path)
        finally:
            os.unlink(temp_path)


class TestJellyfinConfigurator(unittest.TestCase):
    """Test JellyfinConfigurator class."""

    def setUp(self):
        self.server_url = "http://localhost:8096"
        self.api_key = "test-api-key"
        self.configurator = configure_jellyfin.JellyfinConfigurator(
            self.server_url,
            self.api_key,
            dry_run=True
        )

    def test_init(self):
        self.assertEqual(self.configurator.server_url, self.server_url)
        self.assertEqual(self.configurator.api_key, self.api_key)
        self.assertTrue(self.configurator.dry_run)
        self.assertIn('X-Emby-Token', self.configurator.headers)

    @patch('configure_jellyfin.requests.request')
    def test_dry_run_mode(self, mock_request):
        self.configurator._make_request('POST', '/test', data={'test': 'data'})
        mock_request.assert_not_called()

    @patch('configure_jellyfin.requests.request')
    def test_make_request_get(self, mock_request):
        configurator = configure_jellyfin.JellyfinConfigurator(
            self.server_url,
            self.api_key,
            dry_run=False
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'test': 'response'}
        mock_response.content = b'{"test": "response"}'
        mock_request.return_value = mock_response

        result = configurator._make_request('GET', '/test')

        self.assertEqual(result, {'test': 'response'})
        mock_request.assert_called_once()

    @patch('configure_jellyfin.requests.request')
    def test_make_request_no_content_returns_empty_dict(self, mock_request):
        configurator = configure_jellyfin.JellyfinConfigurator(
            self.server_url,
            self.api_key,
            dry_run=False
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b''
        mock_request.return_value = mock_response

        result = configurator._make_request('GET', '/empty')

        self.assertEqual(result, {})
        mock_request.assert_called_once()

    @patch('configure_jellyfin.requests.request')
    def test_make_request_handles_request_exception(self, mock_request):
        configurator = configure_jellyfin.JellyfinConfigurator(
            self.server_url,
            self.api_key,
            dry_run=False
        )

        mock_request.side_effect = configure_jellyfin.requests.exceptions.RequestException("boom")

        result = configurator._make_request('GET', '/fail')

        self.assertIsNone(result)
        mock_request.assert_called_once()

    @patch.object(configure_jellyfin.JellyfinConfigurator, '_make_request')
    def test_test_connection_failure(self, mock_request):
        mock_request.return_value = None
        result = self.configurator.test_connection()

        self.assertFalse(result)
        mock_request.assert_called_once_with('GET', '/System/Info')

    @patch.object(configure_jellyfin.JellyfinConfigurator, '_make_request')
    def test_disable_quick_connect_when_already_disabled(self, mock_request):
        mock_request.side_effect = [
            {'QuickConnectAvailable': False},  # GET
        ]

        result = self.configurator.disable_quick_connect()

        self.assertTrue(result)
        self.assertEqual(mock_request.call_count, 1)

    @patch.object(configure_jellyfin.JellyfinConfigurator, '_make_request')
    def test_disable_quick_connect_updates_when_enabled(self, mock_request):
        mock_request.side_effect = [
            {'QuickConnectAvailable': True},  # GET
            {},  # POST
        ]

        result = self.configurator.disable_quick_connect()

        self.assertTrue(result)
        self.assertEqual(mock_request.call_count, 2)
        post_call = mock_request.call_args_list[1]
        self.assertEqual(post_call.args[0], 'POST')
        self.assertIn('QuickConnectAvailable', post_call.kwargs['data'])
        self.assertFalse(post_call.kwargs['data']['QuickConnectAvailable'])

    @patch.object(configure_jellyfin.JellyfinConfigurator, '_make_request')
    def test_configure_global_trickplay_merge(self, mock_request):
        mock_request.side_effect = [
            {'TrickplayOptions': {'Enabled': True, 'Interval': 5}},  # GET
            {},  # POST
        ]

        options = {'Interval': 10}
        result = self.configurator.configure_global_trickplay(options)

        self.assertTrue(result)
        self.assertEqual(mock_request.call_count, 2)
        post_call = mock_request.call_args_list[1]
        self.assertEqual(post_call.args[0], 'POST')
        payload = post_call.kwargs['data']
        self.assertIn('TrickplayOptions', payload)
        self.assertEqual(payload['TrickplayOptions']['Interval'], 10)

    @patch.object(configure_jellyfin.JellyfinConfigurator, '_make_request')
    def test_configure_global_trickplay_empty_options(self, mock_request):
        result = self.configurator.configure_global_trickplay({})

        self.assertTrue(result)
        mock_request.assert_not_called()

    @patch.object(configure_jellyfin.JellyfinConfigurator, '_make_request')
    def test_configure_global_trickplay_already_up_to_date(self, mock_request):
        mock_request.side_effect = [
            {'TrickplayOptions': {'Interval': 5}},  # GET
        ]

        result = self.configurator.configure_global_trickplay({'Interval': 5})

        self.assertTrue(result)
        self.assertEqual(mock_request.call_count, 1)

    @patch.object(configure_jellyfin.JellyfinConfigurator, '_make_request')
    def test_disable_quick_connect_config_load_failure(self, mock_request):
        mock_request.return_value = None

        result = self.configurator.disable_quick_connect()

        self.assertFalse(result)
        mock_request.assert_called_once_with('GET', '/System/Configuration')

    @patch.object(configure_jellyfin.JellyfinConfigurator, '_make_request')
    def test_disable_quick_connect_post_failure(self, mock_request):
        mock_request.side_effect = [
            {'QuickConnectAvailable': True},  # GET
            None,  # POST fails
        ]

        result = self.configurator.disable_quick_connect()

        self.assertFalse(result)
        self.assertEqual(mock_request.call_count, 2)

    @patch.object(configure_jellyfin.JellyfinConfigurator, 'disable_quick_connect')
    @patch.object(configure_jellyfin.JellyfinConfigurator, 'configure_global_trickplay')
    def test_apply_configuration_disable_quick_connect_failure(self, mock_trickplay, mock_disable):
        mock_disable.return_value = False
        mock_trickplay.return_value = True

        result = self.configurator.apply_configuration({'trickplay_options': {}})

        self.assertFalse(result)
        mock_trickplay.assert_called_once()

    @patch.object(configure_jellyfin.JellyfinConfigurator, 'disable_quick_connect')
    @patch.object(configure_jellyfin.JellyfinConfigurator, 'configure_global_trickplay')
    def test_apply_configuration_handles_trickplay_exception(self, mock_trickplay, mock_disable):
        mock_disable.return_value = True
        mock_trickplay.side_effect = RuntimeError("boom")

        result = self.configurator.apply_configuration({'trickplay_options': {}})

        self.assertTrue(result)
        mock_trickplay.assert_called_once()


class TestMainEntrypoint(unittest.TestCase):
    """Cover CLI entry paths without exiting the interpreter."""

    @patch('configure_jellyfin.sys.exit')
    @patch('configure_jellyfin.JellyfinConfigurator')
    @patch('configure_jellyfin.load_config')
    @patch.object(sys, 'argv', ['configure_jellyfin.py'])
    def test_main_happy_path(self, mock_load_config, mock_cfg_class, mock_exit):
        mock_load_config.return_value = {'trickplay_options': {}}
        mock_cfg = mock_cfg_class.return_value
        mock_cfg.test_connection.return_value = True
        mock_cfg.apply_configuration.return_value = True
        mock_exit.side_effect = SystemExit(0)

        with patch.dict(os.environ, {'JELLYFIN_API_KEY': 'abc', 'JELLYFIN_URL': 'http://localhost:8096'}, clear=False):
            with self.assertRaises(SystemExit):
                configure_jellyfin.main()

        mock_exit.assert_called_once_with(0)
        mock_cfg.test_connection.assert_called_once()
        mock_cfg.apply_configuration.assert_called_once()

    @patch('configure_jellyfin.sys.exit')
    @patch('configure_jellyfin.load_config')
    @patch.object(sys, 'argv', ['configure_jellyfin.py'])
    def test_main_missing_api_key_exits(self, mock_load_config, mock_exit):
        mock_load_config.return_value = {}
        mock_exit.side_effect = SystemExit(1)

        with patch.dict(os.environ, {'JELLYFIN_URL': 'http://localhost:8096'}, clear=True):
            with self.assertRaises(SystemExit):
                configure_jellyfin.main()

        mock_exit.assert_called_once_with(1)


def run_tests():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
