#!/bin/bash

# MathMaster Backend Deployment Script for Heroku
# This script automates the deployment of the MathMaster backend to Heroku

# Exit on error
set -e

# Configuration
APP_NAME="mathmaster-api"
DATABASE_PLAN="jawsdb:kitefin"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "Heroku CLI is not installed. Please install it first."
    echo "Visit: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "You are not logged in to Heroku. Please login first."
    heroku login
fi

# Create Heroku app if it doesn't exist
if ! heroku apps:info "$APP_NAME" &> /dev/null; then
    echo "Creating Heroku app: $APP_NAME"
    heroku create "$APP_NAME"
else
    echo "Heroku app $APP_NAME already exists."
fi

# Add JawsDB MySQL add-on if not already added
if ! heroku addons:info --app "$APP_NAME" JawsDB &> /dev/null; then
    echo "Adding JawsDB MySQL add-on"
    heroku addons:create "$DATABASE_PLAN" --app "$APP_NAME"
else
    echo "JawsDB MySQL add-on already exists."
fi

# Create Procfile if it doesn't exist
if [ ! -f "Procfile" ]; then
    echo "Creating Procfile"
    echo "web: gunicorn src.main:app" > Procfile
    echo "Procfile created."
else
    echo "Procfile already exists."
fi

# Create runtime.txt if it doesn't exist
if [ ! -f "runtime.txt" ]; then
    echo "Creating runtime.txt"
    echo "python-3.9.16" > runtime.txt
    echo "runtime.txt created."
else
    echo "runtime.txt already exists."
fi

# Check if gunicorn is in requirements.txt
if ! grep -q "gunicorn" requirements.txt; then
    echo "Adding gunicorn to requirements.txt"
    echo "gunicorn==20.1.0" >> requirements.txt
    echo "Added gunicorn to requirements.txt"
fi

# Set environment variables
echo "Setting environment variables"
heroku config:set SECRET_KEY="$(openssl rand -hex 32)" --app "$APP_NAME"
heroku config:set JWT_SECRET_KEY="$(openssl rand -hex 32)" --app "$APP_NAME"

# Prompt for Stripe API keys
read -p "Enter your Stripe Secret Key (leave blank to skip): " STRIPE_SECRET_KEY
if [ ! -z "$STRIPE_SECRET_KEY" ]; then
    heroku config:set STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY" --app "$APP_NAME"
fi

read -p "Enter your Stripe Webhook Secret (leave blank to skip): " STRIPE_WEBHOOK_SECRET
if [ ! -z "$STRIPE_WEBHOOK_SECRET" ]; then
    heroku config:set STRIPE_WEBHOOK_SECRET="$STRIPE_WEBHOOK_SECRET" --app "$APP_NAME"
fi

# Initialize Git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "Initializing Git repository"
    git init
    git add .
    git commit -m "Initial commit for Heroku deployment"
fi

# Add Heroku remote if not already added
if ! git remote | grep -q "heroku"; then
    echo "Adding Heroku remote"
    heroku git:remote --app "$APP_NAME"
fi

# Deploy to Heroku
echo "Deploying to Heroku"
git push heroku main

# Run database migrations
echo "Running database migrations"
heroku run python -c "from src.main import app, db; app.app_context().push(); db.create_all()" --app "$APP_NAME"

# Seed curriculum data if requested
read -p "Do you want to seed the curriculum data? (y/n): " SEED_DATA
if [ "$SEED_DATA" = "y" ] || [ "$SEED_DATA" = "Y" ]; then
    echo "Seeding curriculum data"
    heroku run python src/data/curriculum_seed.py --app "$APP_NAME"
fi

echo "Deployment completed successfully!"
echo "Your API is now available at: https://$APP_NAME.herokuapp.com/"

