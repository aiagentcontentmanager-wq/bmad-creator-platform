#!/bin/bash
# BMAD Fly.io Deployment Script
set -e

echo "=== BMAD Fly.io Deployment ==="

if ! command -v fly &> /dev/null; then
    echo "Install flyctl: https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

echo "Logging in..."
fly auth login

if ! fly apps list | grep -q "bmad-api"; then
    echo "Creating app..."
    fly launch --name bmad-api --region fra --copy-config --now
fi

if ! fly volumes list | grep -q "bmad_data"; then
    echo "Creating volume..."
    fly volumes create bmad_data --region fra --size 1
fi

echo "Deploying..."
fly deploy

echo "=== Done! ==="
echo "API: https://bmad-api.fly.dev"
echo "Set secrets: fly secrets set SECRET_KEY=\$(openssl rand -hex 32)"
