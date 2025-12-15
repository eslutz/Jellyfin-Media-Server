# Security Policy

## Supported Versions

This project is a configuration repository and does not follow semantic versioning.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these guidelines:

1. **Do not open a public issue** on GitHub.
2. Report security vulnerabilities by emailing the maintainer at [security@ericslutz.dev](mailto:security@ericslutz.dev).
3. Include as much information as possible:
   - A description of the vulnerability
   - Steps to reproduce the issue
   - Possible impact of the vulnerability
   - Any suggested fixes (if you have them)

We will make every effort to acknowledge your report promptly.

## Security Best Practices

When deploying this stack:

1. **Network Isolation**: Deploy this service in a dedicated network segment isolated from other local networks.
2. **Authentication**: Enable authentication and use strong passwords for all user accounts.
3. **External Access**: Use a reverse proxy with SSL/TLS termination for external access rather than exposing directly.
4. **Secrets Management**: Use `.env` files for API keys and passwords; never commit them to the repository.
5. **Regular Updates**: Keep Jellyfin server and dependencies updated to receive security patches.
