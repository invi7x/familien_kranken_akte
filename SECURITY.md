# Security Policy

Familienakte stores sensitive health-related information. Treat every installation as a system containing confidential data.

## Supported versions

Until version 1.0, security fixes are provided for the current development release only.

## Reporting a vulnerability

Please do **not** publish security vulnerabilities as a public GitHub issue.

Use GitHub's private security reporting feature when it is enabled for this repository. If private reporting is not available, contact the repository maintainer privately.

Please include:

- affected version
- reproducible steps
- expected and actual behavior
- potential impact

Do not include real medical records, backups, credentials, access tokens, IP addresses, or other personal data in a report.

## Deployment notes

- Do not commit `.env` files, backups, databases, or exported medical data to Git.
- Create a private `.env` from `.env.example` and use a unique random `SECRET_KEY`. The Compose stack intentionally refuses to start without it.
- Prefer HTTPS behind a reverse proxy or access through a trusted VPN.
- Keep regular JSON backups and test restoring them.
- Restrict access to Docker volumes and backup files at operating-system level.

This project is not a certified medical device and is provided without warranty.
