#!/usr/bin/env python
"""Console script for networkmonitor."""
import sys
from networkmonitor.cli import cli

def main():
    """Execute the CLI"""
    try:
        cli()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()