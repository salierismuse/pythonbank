#!/usr/bin/env python3
"""
Run via: python batch_transactions.py
Or hook into cron / your Flask app.
"""

from database import process_all_pending

if __name__ == "__main__":
    msg = process_all_pending()
    print(msg)
