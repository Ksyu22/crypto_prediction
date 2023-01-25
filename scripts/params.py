"""
Package params
load and validate the environment variables in the `.env`
"""

import os

COIN_API = os.environ.get("COIN_API")
