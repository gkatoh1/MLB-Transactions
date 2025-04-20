# Blue Jays Opponent Transactions Checker

This application monitors MLB transactions for the Toronto Blue Jays' upcoming opponents and sends email notifications when new transactions are detected.

## Features

- Checks MLB transactions page hourly
- Filters transactions to only include the Blue Jays' upcoming opponents
- Sends email notifications only when new transactions are detected
- Runs automatically on Render as a scheduled job

## Setup Instructions for Render

1. Create a new Render account if you don't have one at [render.com](https://render.com)

2. Create a new Blueprint on Render:
   - Go to your Render dashboard
   - Click on "New" and select "Blueprint"
   - Connect your GitHub repository that contains these files
   - Follow the prompts to deploy

3. Configure the Environment Variable:
   - Once deployed, go to your cron job service in the Render dashboard
   - Click on "Environment" tab
   - Add the `EMAIL_PASSWORD` environment variable with your Yahoo mail app password
   - Save changes

4. Verify the schedule:
   - The cron job is configured to run every hour
   - You can adjust the schedule in the `render.yaml` file if needed

## Local Development

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set your email password as an environment variable:
   - Linux/Mac: `export EMAIL_PASSWORD=your_password`
   - Windows: `set EMAIL_PASSWORD=your_password`
4. Run the script: `python bluejays_transactions.py`

## Notes

- The script will only email when new transactions are detected since the last check
- The data file `last_check.json` tracks when the script was last run
- For Yahoo Mail, you need to use an App Password (not your regular account password)
