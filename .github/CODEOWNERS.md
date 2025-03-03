# Code Owners Documentation

This document explains the code ownership structure of the NetworkMonitor project.

## Overview

The CODEOWNERS file is used to automatically request reviews from the appropriate team members when a pull request is opened.

## Current Ownership Structure

### Core Components
- **Network Monitoring Core** (@umerfarok)
  - `/networkmonitor/monitor.py`
  - `/networkmonitor/npcap_helper.py`

### Web Interface
- **Frontend Components** (@umerfarok)
  - `/networkmonitor/web/`

### Build & Deployment
- **Build System** (@umerfarok)
  - `/build.py`
  - `/installer.nsi`
  - `/.github/workflows/`

## Review Process

1. When a pull request is opened, GitHub automatically requests reviews from the appropriate code owners.
2. At least one approval from a code owner is required to merge changes.
3. Code owners should review changes within their area of responsibility within 3 business days.

## Becoming a Code Owner

To become a code owner:
1. Demonstrate expertise in the relevant area through contributions
2. Request ownership by opening an issue
3. Get approval from existing code owners

## Contact

For questions about code ownership, contact:
- Umer Farooq (@umerfarok)