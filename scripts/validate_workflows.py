#!/usr/bin/env python3
"""Validate GitHub Actions workflow YAML files."""

import sys
import glob
import yaml


def main():
    errors = 0
    for workflow in sorted(glob.glob('.github/workflows/*.yml')):
        print(f"Validating {workflow}...")
        try:
            with open(workflow, 'r') as f:
                data = yaml.safe_load(f)

            for field in ('name', 'on', 'jobs'):
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            print(f"  ✅ {workflow} — syntax and structure OK")
        except Exception as e:
            print(f"  ❌ {workflow} — {e}")
            errors += 1

    if errors:
        print(f"\n❌ {errors} workflow(s) failed validation")
        sys.exit(1)

    print("\n✅ All workflows validated successfully")


if __name__ == "__main__":
    main()
