# api/index.py
# Cloudflare Workers Python API entry point
# Uses native WorkerEntrypoint pattern (no FastAPI - not supported in Workers)
#
# NOTE: FastAPI is NOT supported in Cloudflare Workers Python deployment.
# See: https://github.com/cloudflare/workers-sdk/issues/5608
#
# This file re-exports the main entry point from the project root.
# All functionality is defined in index.py at the project root.
# Any changes should be made to the root index.py file.

import sys
import os

# Add the project root to the Python path so we can import from index.py
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Re-export the Default class from the main index.py
# This ensures all routes, including /api/posts_multi and favicon support,
# are available when using this entry point
from index import Default

# Make Default available at module level
__all__ = ['Default']
