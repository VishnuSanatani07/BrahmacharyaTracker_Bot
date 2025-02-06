import os
import json
import logging
from datetime import datetime
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load bot token securely
BOT_TOKEN = "7862439625:AAFgl1ZGrJF7g_1X1QjdfKALv7Au09VHtXQ"  # Replace with your actual bot token
LEADERBOARD_FILE = "leaderboard.json"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load leaderboard from file
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as file:
            return json.load(file)
    return []

# Save leaderboard to file
def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as file:
        json.dump(leaderboard, file, indent=4)

leaderboard = load_leaderboard()

async def track_submission(update: Update, context: CallbackContext):
    if update.message.photo and update.message.caption and "#BT" in update.message.caption:
        user = update.message.from_user
        username = user.username or user.first_name

        if username not in [entry['username'] for entry in leaderboard]:
            leaderboard.append({"username": username, "timestamp": datetime.now().isoformat()})
            save_leaderboard(leaderboard)
            await update.message.reply_text(f"Sita Ram 🙏🙏 {username}, you have been added to the leaderboard!")
        else:
            await update.message.reply_text(f"{username}, you are already on the leaderboard!")

async def show_leaderboard(update: Update, context: CallbackContext):
    if not leaderboard:
        await update.message.reply_text("Leaderboard is empty!")
        return
    
    sorted_leaderboard = sorted(leaderboard, key=lambda x: x['timestamp'])
    message = "🏆 Brahmacharya Tracker Leaderboard 🏆\n\n"
    for idx, entry in enumerate(sorted_leaderboard, start=1):
        message += f"{idx}. {entry['username']}\n"
    
    await update.message.reply_text(message)

async def reset_leaderboard(update: Update, context: CallbackContext):
    user = update.message.from_user
    chat = await context.bot.get_chat(update.message.chat_id)
    member = await chat.get_member(user.id)
    
    if member.status in ('administrator', 'creator'):
        global leaderboard
        leaderboard = []
        save_leaderboard(leaderboard)
        await update.message.reply_text("Leaderboard has been reset by an admin!")
    else:
        await update.message.reply_text("You do not have permission to reset the leaderboard!")

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to Brahmacharya Tracker Bot! Send an image with '#BT' in the caption to join the leaderboard.")

# Main function to run the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("leaderboard", show_leaderboard))
    application.add_handler(CommandHandler("reset", reset_leaderboard))
    application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex("#BT"), track_submission))
    
    application.run_polling()

if __name__ == "__main__":
    main()
