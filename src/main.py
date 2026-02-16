"""
FastAPI Application Initialization

This script sets up the FastAPI app, configures settings,
and imports required modules (models, views, and routes).
"""


import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.controllers.health_controller import health_router

SECRET_KEY = os.urandom(32)


app = FastAPI(
    title="My Agent Lab API",
    version="0.1.0",
    description="""
**My Agent Lab**

A personal experimental API for building, testing, and evolving agent systems.

Focus areas:
-  LangGraph-based agent workflows
-  Multi-agent reasoning systems
-  Agent memory & state machines
-  Tool-using agents
-  RAG pipelines
-  Graph-based reasoning
- Rapid prototyping of AI architectures

This repo is a research playground for intelligent agent design.
""",
    docs_url="/swagger",
    redoc_url="/docs",
)

ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_origins=ALLOWED_ORIGINS,
    expose_headers=["*"],
    max_age=600,
)


app.include_router(health_router)
