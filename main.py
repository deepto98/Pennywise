import os
import datetime
import interactions
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import re
import json
import logging

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger(__name__)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Build Google credentials dict from environment variables
GOOGLE_CREDS_DICT = {
    "type": os.getenv("GOOGLE_CREDENTIALS_TYPE"),
    "project_id": os.getenv("GOOGLE_CREDENTIALS_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_CREDENTIALS_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_CREDENTIALS_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("GOOGLE_CREDENTIALS_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CREDENTIALS_CLIENT_ID"),
    "auth_uri": os.getenv("GOOGLE_CREDENTIALS_AUTH_URI"),
    "token_uri": os.getenv("GOOGLE_CREDENTIALS_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GOOGLE_CREDENTIALS_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("GOOGLE_CREDENTIALS_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("GOOGLE_CREDENTIALS_UNIVERSE_DOMAIN"),
}

SETUP_FILE = "user_sheet_map.json"

def save_user_sheet(user_id, server_id, sheet_id):
    try:
        if os.path.exists(SETUP_FILE):
            with open(SETUP_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {}
        key = f"{user_id}_{server_id}"
        data[key] = sheet_id
        with open(SETUP_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Failed to save user sheet: {e}", exc_info=True)
        pass  # Silent fail, handled in command

def get_user_sheet(user_id, server_id):
    try:
        if not os.path.exists(SETUP_FILE):
            return None
        with open(SETUP_FILE, "r") as f:
            data = json.load(f)
        key = f"{user_id}_{server_id}"
        return data.get(key)
    except Exception as e:
        logger.error(f"Failed to get user sheet: {e}", exc_info=True)
        return None

# Google Sheets setup
def get_sheet(sheet_id):
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    try:
        creds = Credentials.from_service_account_info(GOOGLE_CREDS_DICT, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        worksheet = sh.sheet1
        return worksheet
    except Exception as e:
        logger.error(f"Failed to get sheet: {e}", exc_info=True)
        raise

# Discord bot setup
bot = interactions.Client(token=DISCORD_TOKEN, intents=interactions.Intents.DEFAULT)

@interactions.slash_command(
    name="add",
    description="Add an expense to your Google Sheet"
)
@interactions.slash_option(
    name="amount",
    description="Expense amount",
    opt_type=interactions.OptionType.NUMBER,
    required=False,
)
async def add(ctx: interactions.SlashContext, amount: float = None):
    if amount is None:
        await ctx.send("Please provide an amount.", ephemeral=True)
        return
    await ctx.defer(ephemeral=True)
    try:
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild_id)
        sheet_id = get_user_sheet(user_id, server_id)
        if not sheet_id:
            await ctx.send("Please run /setup to configure your Google Sheet.", ephemeral=True)
            return
        worksheet = get_sheet(sheet_id)
        now = datetime.datetime.now()
        user = f"{ctx.author.username}#{ctx.author.discriminator}"
        human_time = now.strftime("%-m/%-d/%y [%I:%M%p]").lower().replace(':0', ':')
        worksheet.append_row([human_time, user, amount])
        await ctx.send(f"💸 Added expense of **{amount}** for **{user}**! Your wallet thanks you. 🪙", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in /add: {e}", exc_info=True)
        await ctx.send("Server error", ephemeral=True)

@interactions.slash_command(
    name="setup",
    description="Setup your Google Sheet for Pennywise"
)
@interactions.slash_option(
    name="spreadsheet_url",
    description="Paste your Google Spreadsheet URL",
    opt_type=interactions.OptionType.STRING,
    required=True,
)
async def setup(ctx: interactions.SlashContext, spreadsheet_url: str):
    await ctx.defer(ephemeral=True)
    try:
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild_id)
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", spreadsheet_url)
        if not match:
            await ctx.send("Please provide a valid Google Spreadsheet URL.", ephemeral=True)
            return
        sheet_id = match.group(1)
        save_user_sheet(user_id, server_id, sheet_id)
        # Show client_email from credentials.json
        email = GOOGLE_CREDS_DICT.get("client_email", "<service account email>")
        await ctx.send(f"Your spreadsheet is setup for transactions! Go to Share > Add **{email}** as an Editor.", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in /setup: {e}", exc_info=True)
        await ctx.send("Server error", ephemeral=True)

@interactions.slash_command(
    name="columns",
    description="Add Time, User, Amount columns to your Google Sheet"
)
async def columns(ctx: interactions.SlashContext):
    await ctx.defer(ephemeral=True)
    try:
        user_id = str(ctx.author.id)
        server_id = str(ctx.guild_id)
        sheet_id = get_user_sheet(user_id, server_id)
        if not sheet_id:
            await ctx.send("Please run /setup to configure your Google Sheet.", ephemeral=True)
            return
        worksheet = get_sheet(sheet_id)
        worksheet.update('A1:C1', [["Time", "User", "Amount"]])
        await ctx.send("✅ Added columns: Time, User, Amount.", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in /columns: {e}", exc_info=True)
        await ctx.send("Server error", ephemeral=True)

@bot.event
async def on_ready():
    logger.info(f'Bot connected as {bot.me.name}')

if __name__ == "__main__":
    logger.info("Starting bot...")
    bot.start()
