#!/bin/bash
echo "🚀 Deploying TenderHub India to Firebase..."

# Install dependencies
pip install -r backend/requirements.txt
playwright install chromium

# Deploy
firebase deploy --only hosting,functions

echo "✅ Deployed to https://your-project.web.app"
