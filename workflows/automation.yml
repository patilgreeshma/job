name: Daily Telegram Job Tracker

on:
  schedule:
    - cron: '0 4,14 * * *' # Runs automatically twice a day (9:30 AM and 7:30 PM IST)
  workflow_dispatch: # Allows you to tap "Run Workflow" manually inside GitHub anytime

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Setup Python Runtime
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Network Dependencies
        run: pip install requests

      - name: Execute Tracker Script
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python whatsapp_job_agent.py

      - name: Auto-Commit Database Changes
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "Sync tracked job history logs"
          file_pattern: 'india_jobs.db'
