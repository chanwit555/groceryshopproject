#!/usr/bin/env python
import os
import sys
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'grocery_shop.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Can't import Django. Did you install it?") from exc
    execute_from_command_line(sys.argv)
if __name__ == '__main__':
    main()
