# Jellyfin-Media-Server

Automated configuration tools for Jellyfin Media Server.

## Overview

This repository provides Python scripts to programmatically configure Jellyfin Media Server instances using the Jellyfin REST API.

The implementation follows the **Jellyfin OpenAPI stable specification** to ensure proper API integration and compatibility.

## Features

- 🔧 **Automated Library Configuration**: Create and configure media libraries via API
- 📝 **JSON-based Configuration**: Define all settings in `jellyfin.config.json`
- ⚡ **Scheduled Task Management**: Automate scans, chapter extraction, and intro detection
- 🎬 **Metadata & Image Settings**: Configure downloaders, fetchers, and savers
- 🔍 **Dry Run Mode**: Preview changes before applying

## Quick Start

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Get your Jellyfin API key:**
   - Navigate to Jellyfin Dashboard → API Keys
   - Create a new API key

3. **Configure settings:**
   ```bash
   cp jellyfin.config.example.json jellyfin.config.json
   # Edit jellyfin.config.json with your settings
   ```

4. **Run the configuration script:**
   ```bash
   python3 configure_jellyfin.py
   ```

## Documentation

- **[Configuration Guide](CONFIGURATION_GUIDE.md)** - Detailed usage instructions
- **[Examples](EXAMPLES.md)** - Practical usage examples and troubleshooting
- **[Configuration Plan](jellyfin-config-plan.md)** - Library settings recommendations
- **[API Reference](https://api.jellyfin.org/)** - Jellyfin REST API documentation
- **[OpenAPI Reference](research/openapi_reference.md)** - OpenAPI specification notes

## Files

- `configure_jellyfin.py` - Main configuration script
- `jellyfin.config.json` - Your configuration file (create from example)
- `jellyfin.config.example.json` - Example configuration
- `jellyfin-config-plan.md` - Detailed configuration recommendations
- `CONFIGURATION_GUIDE.md` - Usage and reference guide
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.6+
- Jellyfin Media Server (any recent version)
- API access to your Jellyfin server

## License

This project is provided as-is for use with Jellyfin Media Server.