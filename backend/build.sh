#!/usr/bin/env bash
# Build script for Render

cd backend
pip install --upgrade pip setuptools wheel
pip install --no-cache-dir --only-binary=:all: -r requirements.txt || pip install --no-cache-dir -r requirements.txt
