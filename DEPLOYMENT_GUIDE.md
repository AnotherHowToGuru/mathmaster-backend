# MathMaster Backend Deployment Guide

This guide will walk you through deploying the MathMaster backend API to Heroku in simple steps.

## What You'll Need

- A [Heroku](https://www.heroku.com/) account (free to create)
- The [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed on your computer
- [Git](https://git-scm.com/downloads) installed on your computer
- A [Stripe](https://stripe.com/) account for payment processing (optional)

## Step 1: Download the Backend Code

1. Download the MathMaster backend code ZIP file
2. Extract the ZIP file to a folder on your computer
3. Open a command prompt or terminal in that folder

## Step 2: Log in to Heroku

1. Open a command prompt or terminal
2. Run the command:
   ```
   heroku login
   ```
3. A browser window will open. Click the "Log In" button
4. After logging in, close the browser window and return to the terminal

## Step 3: Create a Heroku App

1. In the terminal, run:
   ```
   heroku create mathmaster-api
   ```
   (If this name is taken, choose a different name like `mathmaster-api-yourusername`)

2. You'll see output like this:
   ```
   Creating ⬢ mathmaster-api... done
   https://mathmaster-api.herokuapp.com/ | https://git.heroku.com/mathmaster-api.git
   ```

## Step 4: Add a Database

1. Add a MySQL database to your Heroku app:
   ```
   heroku addons:create jawsdb:kitefin
   ```

2. This will create a free MySQL database for your app

## Step 5: Set Up Environment Variables

1. Set a secret key for your application:
   ```
   heroku config:set SECRET_KEY=your_secret_key_here
   heroku config:set JWT_SECRET_KEY=your_jwt_secret_key_here
   ```

2. If you have a Stripe account, add your Stripe keys:
   ```
   heroku config:set STRIPE_SECRET_KEY=your_stripe_secret_key
   heroku config:set STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
   ```

## Step 6: Deploy the Application

1. Initialize a Git repository in your backend folder:
   ```
   git init
   ```

2. Add all files to the repository:
   ```
   git add .
   ```

3. Commit the files:
   ```
   git commit -m "Initial commit"
   ```

4. Add the Heroku remote:
   ```
   heroku git:remote -a mathmaster-api
   ```
   (Replace `mathmaster-api` with your app name if you chose a different one)

5. Push the code to Heroku:
   ```
   git push heroku main
   ```
   (If you're on a `master` branch instead of `main`, use `git push heroku master`)

6. Wait for the deployment to complete. You'll see output ending with:
   ```
   remote: Verifying deploy... done.
   ```

## Step 7: Initialize the Database

1. Run the database initialization command:
   ```
   heroku run python -c "from src.main import app, db; app.app_context().push(); db.create_all()"
   ```

2. Seed the database with sample curriculum content:
   ```
   heroku run python src/data/curriculum_seed.py
   ```

## Step 8: Test Your API

1. Open your browser and go to:
   ```
   https://mathmaster-api.herokuapp.com/api/health
   ```
   (Replace `mathmaster-api` with your app name if you chose a different one)

2. You should see a response like:
   ```json
   {"message":"MathMaster API is running","status":"healthy"}
   ```

## Step 9: Connect Your Frontend

1. Update your frontend configuration to point to your new API:
   - Edit the file `src/config.js` in your frontend code
   - Set the `apiUrl` to your Heroku app URL + `/api`:
     ```javascript
     const config = {
       apiUrl: 'https://mathmaster-api.herokuapp.com/api'
     };
     
     export default config;
     ```

2. Redeploy your frontend on Vercel

## Troubleshooting

If you encounter any issues:

1. Check the Heroku logs:
   ```
   heroku logs --tail
   ```

2. Make sure your database was created properly:
   ```
   heroku addons
   ```

3. Verify your environment variables:
   ```
   heroku config
   ```

## Next Steps

Once your backend is deployed:

1. Create a parent account through the frontend
2. Add child profiles
3. Explore the curriculum content
4. Set up subscription plans in your Stripe dashboard

Need help? Feel free to ask for assistance with any step!

