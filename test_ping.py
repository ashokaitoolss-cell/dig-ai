#!/usr/bin/env python3
"""Send a test notification to your ntfy topic.

Usage: python3 test_ping.py <topic>     (or set NTFY_TOPIC and omit the arg)
"""
import os
import sys

import requests

topic = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("NTFY_TOPIC")
if not topic:
    sys.exit("Usage: python3 test_ping.py <topic>  (or set NTFY_TOPIC)")

resp = requests.post("https://ntfy.sh", json={
    "topic": topic,
    "title": "dig.ai online 🟢",
    "message": "Test ping from the dig.ai radar. If you can read this, notifications work.",
    "tags": ["satellite"],
    "priority": 3,
}, timeout=15)
resp.raise_for_status()
print("Sent to https://ntfy.sh/%s — check your phone." % topic)
