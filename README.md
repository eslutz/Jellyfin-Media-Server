# Jellyfin Media Server Configuration

Automated configuration tools for Jellyfin Media Server using Python 3 and the Jellyfin REST API.

## Overview

This repository provides a Python script to programmatically configure Jellyfin Media Server instances using the Jellyfin REST API. The implementation follows the **Jellyfin OpenAPI stable specification** to ensure proper API integration and compatibility.

## Features

- 🔧 **Automated Library Configuration**: Create and configure media libraries via API
- 📝 **JSON-based Configuration**: Define all settings in `jellyfin.config.json`
- 🔐 **Secure Credentials**: Store API keys in `.env` file (not committed to git)
- ⚡ **Scheduled Task Management**: Automate scans, chapter extraction, and intro detection
- 🎬 **Metadata & Image Settings**: Configure downloaders, fetchers, and savers
- 🔍 **Dry Run Mode**: Preview changes before applying
- ✅ **CI/CD Pipeline**: Automated testing, linting, and security scanning

## Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy the example file and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Jellyfin server details:
```bash
JELLYFIN_URL=http://localhost:8096
JELLYFIN_API_KEY=your_api_key_here
```

**Getting an API Key:**
1. Log into Jellyfin web interface
2. Click user icon → **Dashboard**
3. Under **Advanced**, click **API Keys**
4. Click **+** to create a new key
5. Copy the generated key to your `.env` file

### 3. Configure Libraries

Edit `jellyfin.config.json` to customize:
- Library names and folder paths
- Metadata downloader priorities
- Image fetcher settings
- Scheduled task intervals

See `jellyfin-config-plan.md` for detailed configuration recommendations.

### 4. Run the Script

Preview changes (dry run):
```bash
python3 configure_jellyfin.py --dry-run
```

Apply configuration:
```bash
python3 configure_jellyfin.py
```

## Documentation

- **[Configuration Guide](CONFIGURATION_GUIDE.md)** - Complete usage documentation
- **[Configuration Plan](jellyfin-config-plan.md)** - Recommended library settings
- **[API Reference](https://api.jellyfin.org/)** - Jellyfin REST API documentation
- **[OpenAPI Reference](docs/openapi_reference.md)** - OpenAPI specification notes
- **[API Endpoints](docs/api_endpoints.md)** - Endpoint documentation
- **[API Notes](docs/jellyfin_api_notes.md)** - Implementation notes

## Project Structure

```
.
├── configure_jellyfin.py          # Main configuration script
├── jellyfin.config.json           # Library and task configuration
├── .env.example                   # Example environment variables
├── .env                           # Your credentials (not committed)
├── requirements.txt               # Python dependencies
├── tests/
│   └── test_configure_jellyfin.py # Unit tests
├── docs/                          # API documentation
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI/CD pipeline
└── README.md                      # This file
```

## Requirements

- Python 3.6+
- Jellyfin Media Server (any recent version)
- Network access to your Jellyfin server

## Configuration File Format

The `jellyfin.config.json` file defines:

### Libraries
- Content type (movies, tvshows, music, books)
- Folder paths
- Display settings
- Metadata downloader priorities (TheMovieDb, TheTVDB, OMDb)
- Image fetcher priorities
- Advanced options (language, country, chapter images, trickplay)

### Scheduled Tasks
- Scan intervals (e.g., every 30 minutes)
- Daily schedules (e.g., 3 AM for background processing)
- Task-specific settings

See the included `jellyfin.config.json` for a complete example based on `jellyfin-config-plan.md`.

## CI/CD Pipeline

The repository includes a GitHub Actions workflow that automatically:
- Runs unit tests on all pull requests
- Performs linting with flake8 and pylint
- Executes CodeQL security analysis
- Validates JSON configuration files

## Security

- **API Keys**: Stored in `.env` file (gitignored)
- **No Secrets in Config**: `jellyfin.config.json` contains no sensitive data
- **HTTPS Support**: Use HTTPS URLs for production
- **CodeQL Scanning**: Automated security analysis in CI/CD

## Troubleshooting

### Environment Variables Not Found
```
API key not found in environment variables
```
**Solution**: Create `.env` file from `.env.example` and set your API key

### Connection Failed
```
Cannot connect to Jellyfin server
```
**Solution**: Verify server URL in `.env` and ensure Jellyfin is running

### Authentication Failed
```
401 Unauthorized
```
**Solution**: Verify API key is correct and hasn't been deleted

See [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) for more troubleshooting tips.

## Contributing

Contributions are welcome! Please ensure:
- All tests pass (`python tests/test_configure_jellyfin.py`)
- Code passes linting (automatically checked in CI)
- Security scans pass (CodeQL in CI)

## License

This project is provided as-is for use with Jellyfin Media Server.
