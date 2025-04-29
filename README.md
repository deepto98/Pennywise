# Pennywise

A general-purpose Discord bot to log expenses to Google Sheets using slash commands.

## How to Use (User's Guide)

1. **Invite the Bot** to your Discord server (with `applications.commands` and `bot` scopes).
2. **Start the Bot** (the bot owner/admin will run the bot for your server).
3. **Create a Google Sheet** (empty or new is fine).
4. **Run `/setup` in Discord** and paste your Google Spreadsheet URL when prompted.
5. **Give Access:**
    - The bot will reply with an email address (service account).
    - In your Google Sheet, click **Share > Add** that email as an **Editor**.
6. *(Optional)* Run `/columns` to add the `Time, User, Amount` headers to your sheet.
7. **Add Expenses:** Use `/add amount:<number>` to log an expense (e.g., `/add amount:20`).

---

## Example Workflow
- `/setup` → paste your sheet URL
- Bot replies: "Go to Share > Add [bot-email] as an Editor."
- In Google Sheets: Share with that email
- `/columns` (optional)
- `/add amount:50` → logs your expense

## No tokens or credentials needed from the user — just a sheet URL and sharing!

## Troubleshooting
- If you see "Server error", double check that you shared your sheet with the bot's email as Editor.
- You can re-run `/setup` at any time to change the sheet.

---

*Bot setup and admin instructions are in the code repository.*
