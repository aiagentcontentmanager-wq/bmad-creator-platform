"""
Telegram Bot for BMAD Creator Onboarding.
"""

import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, MessageHandler,
        ConversationHandler, CallbackQueryHandler, filters, ContextTypes,
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot not installed. Run: pip install python-telegram-bot>=20.0")

# Conversation states
CHOOSING_LANGUAGE, ENTERING_NAME, CHOOSING_PLATFORM, ENTERING_PERSONA, CONFIRMING_CONSENT = range(5)

LANGUAGES = {"en": "English", "de": "Deutsch", "ru": "Русский"}
PLATFORMS = {
    "instagram": "Instagram", "twitter": "Twitter/X",
    "onlyfans": "OnlyFans", "fanly": "Fanly", "telegram": "Telegram",
}

MESSAGES = {
    "en": {
        "welcome": "Welcome to BMAD! Let's set up your creator profile.\n\nChoose your language:",
        "ask_name": "Great! What's your creator name?",
        "ask_platform": "Hi {name}! Which platform are you on?",
        "ask_persona": "Describe your content style (casual, professional, playful):",
        "ask_consent": "Do you consent to data processing for content generation and analytics? (GDPR compliant)",
        "setup_complete": "Setup complete! Use /help to see commands.",
        "help": "/start - Setup profile\n/profile - View profile\n/content - Generate content\n/analytics - View stats\n/help - This message",
    },
    "de": {
        "welcome": "Willkommen bei BMAD! Lass uns dein Profil einrichten.\n\nWähle deine Sprache:",
        "ask_name": "Super! Wie ist dein Creator-Name?",
        "ask_platform": "Hi {name}! Auf welcher Plattform bist du?",
        "ask_persona": "Beschreibe deinen Content-Stil (casual, professionell, playful):",
        "ask_consent": "Stimmst du der Datenverarbeitung für Content-Generierung und Analytics zu? (DSGVO-konform)",
        "setup_complete": "Setup abgeschlossen! Benutze /help für Befehle.",
        "help": "/start - Profil einrichten\n/profile - Profil anzeigen\n/content - Content generieren\n/analytics - Statistiken\n/help - Diese Nachricht",
    },
}


class BMADTelegramBot:
    def __init__(self, token: str, api_base_url: str = "http://localhost:8000"):
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot not installed")
        self.token = token
        self.api_base_url = api_base_url
        self.application = Application.builder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                CHOOSING_LANGUAGE: [CallbackQueryHandler(self.choose_language, pattern="^lang_")],
                ENTERING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.enter_name)],
                CHOOSING_PLATFORM: [CallbackQueryHandler(self.choose_platform, pattern="^platform_")],
                ENTERING_PERSONA: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.enter_persona)],
                CONFIRMING_CONSENT: [CallbackQueryHandler(self.confirm_consent, pattern="^consent_")],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        self.application.add_handler(conv_handler)
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("profile", self.profile_command))

    def _msgs(self, lang: str) -> Dict[str, str]:
        return MESSAGES.get(lang, MESSAGES["en"])

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        keyboard = [[InlineKeyboardButton(name, callback_data=f"lang_{code}")] for code, name in LANGUAGES.items()]
        await update.message.reply_text(MESSAGES["en"]["welcome"], reply_markup=InlineKeyboardMarkup(keyboard))
        return CHOOSING_LANGUAGE

    async def choose_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        lang = query.data.replace("lang_", "")
        context.user_data["language"] = lang
        await query.edit_message_text(self._msgs(lang)["ask_name"])
        return ENTERING_NAME

    async def enter_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["name"] = update.message.text.strip()
        lang = context.user_data.get("language", "en")
        keyboard = [[InlineKeyboardButton(name, callback_data=f"platform_{c}")] for c, name in PLATFORMS.items()]
        await update.message.reply_text(
            self._msgs(lang)["ask_platform"].format(name=context.user_data["name"]),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSING_PLATFORM

    async def choose_platform(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        context.user_data["platform"] = query.data.replace("platform_", "")
        lang = context.user_data.get("language", "en")
        await query.edit_message_text(self._msgs(lang)["ask_persona"])
        return ENTERING_PERSONA

    async def enter_persona(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data["persona"] = {"style": update.message.text.strip()}
        lang = context.user_data.get("language", "en")
        keyboard = [
            [InlineKeyboardButton("Yes / Ja", callback_data="consent_yes")],
            [InlineKeyboardButton("No / Nein", callback_data="consent_no")],
        ]
        await update.message.reply_text(self._msgs(lang)["ask_consent"], reply_markup=InlineKeyboardMarkup(keyboard))
        return CONFIRMING_CONSENT

    async def confirm_consent(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        consent = query.data == "consent_yes"
        lang = context.user_data.get("language", "en")
        if consent:
            context.user_data["consent"] = True
            context.user_data["telegram_id"] = str(update.effective_user.id)
            logger.info(f"New creator: {context.user_data}")
            await query.edit_message_text(self._msgs(lang)["setup_complete"])
        else:
            await query.edit_message_text("No problem! Review our privacy policy and come back with /start")
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Cancelled. Use /start to try again.")
        return ConversationHandler.END

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        lang = context.user_data.get("language", "en")
        await update.message.reply_text(self._msgs(lang)["help"])

    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = context.user_data
        if not data.get("name"):
            await update.message.reply_text("No profile yet. Use /start")
            return
        await update.message.reply_text(
            f"Profile:\nName: {data.get('name')}\nPlatform: {data.get('platform')}\nStyle: {data.get('persona', {}).get('style')}"
        )

    def run(self):
        logger.info("Starting BMAD Telegram Bot...")
        self.application.run_polling()


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return
    BMADTelegramBot(token).run()


if __name__ == "__main__":
    main()
