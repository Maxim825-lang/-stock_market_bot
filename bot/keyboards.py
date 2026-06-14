"""
Inline keyboards for the Telegram bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown after /start."""
    keyboard = [
        [
            InlineKeyboardButton("📊 Сбербанк", callback_data="analyze:SBER.ME"),
            InlineKeyboardButton("⛽ Газпром", callback_data="analyze:GAZP.ME"),
        ],
        [
            InlineKeyboardButton("🍎 Apple", callback_data="analyze:AAPL"),
            InlineKeyboardButton("🚗 Tesla", callback_data="analyze:TSLA"),
        ],
        [
            InlineKeyboardButton("🎮 Nvidia", callback_data="analyze:NVDA"),
            InlineKeyboardButton("💼 Microsoft", callback_data="analyze:MSFT"),
        ],
        [
            InlineKeyboardButton("❓ Помощь", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data="start")]]
    return InlineKeyboardMarkup(keyboard)
