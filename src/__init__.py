"""
FastAPI Application Initialization

This script sets up the FastAPI app, configures settings,
and imports required modules (models, views, and routes).
"""

import os
from fastapi import FastAPI

SECRET_KEY = os.urandom(32)

app = FastAPI()
