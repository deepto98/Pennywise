import os
import datetime
import interactions
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# Google Sheets setup
def get_sheet():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(GOOGLE_SHEET_ID)
    worksheet = sh.sheet1
    return worksheet

# Discord bot setup
bot = interactions.Client(token=DISCORD_TOKEN, intents=interactions.Intents.DEFAULT)

@interactions.slash_command(
    name="pennywise",
    description="Expense tracking commands"
)
@interactions.slash_option(
    name="amount",
    description="Expense amount",
    opt_type=interactions.OptionType.NUMBER,
    required=True,
)
async def add(ctx: interactions.SlashContext, amount: float):
    await ctx.defer(ephemeral=True)  # Respond to Discord instantly

    worksheet = get_sheet()
    now = datetime.datetime.now()
    user = f"{ctx.author.username}#{ctx.author.discriminator}"
    # Format: 2/12/25 [1:23am]
    human_time = now.strftime("%-m/%-d/%y [%I:%M%p]").lower().replace(':0', ':')
    worksheet.append_row([human_time, user, amount])
    await ctx.send(f"💸 Added expense of **{amount}** for **{user}**! Your wallet thanks you. 🪙", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.me.name}')

if __name__ == "__main__":
    bot.start()
