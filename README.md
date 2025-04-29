# Discord Expense Bot

A general-purpose Discord bot to log expenses to Google Sheets using slash commands.

## Features
- Add expenses with `/expense-bot add <amount>`
- Saves user, amount, and timestamp to your Google Sheet
- Easy setup for anyone (just provide your tokens and credentials)

## Setup

1. **Clone this repo**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Create a Google Cloud project**
   - Enable Google Sheets API
   - Create a Service Account and download the JSON credentials
   - Share your Google Sheet with the service account email
4. **Create a Google Sheet**
   - Note its ID (in the URL)
   - Add column headers: `Timestamp`, `User`, `Amount`
5. **Create a Discord bot**
   - Get your bot token from the Discord Developer Portal
   - Invite the bot to your server with `applications.commands` and `bot` scopes
6. **Configure environment**
   - Copy `.env.example` to `.env` and fill in your values
7. **Run the bot**
   ```bash
   python main.py
   ```

## Usage
- Use `/expense-bot add <amount>` in any server where the bot is present.

## Notes
- Each deployment is tied to one Google Sheet. For multi-user sheets, share access accordingly.
- The bot is general-purpose: just set up your own tokens and credentials.
