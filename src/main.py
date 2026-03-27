import sys
import os
from pathlib import Path

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from bot.twitch_bot import TwitchBot


def main():
    load_dotenv()

    app_id = os.getenv("CLIENT_ID", "")
    secret = os.getenv("SECRET", "")
    token = os.getenv("TOKEN", "")
    refresh_token = os.getenv("REFRESH_TOKEN", "")
    channel = os.getenv("CHANNEL", "")
    config_path = os.getenv("CONFIG_PATH", "config/config.json")

    # Qt app
    app = QApplication(sys.argv)
    window = MainWindow()

    # Bot
    bot = TwitchBot(
        app_id=app_id,
        secret=secret,
        token=token,
        refresh_token=refresh_token,
        channel=channel,
        config_path=config_path,
    )

    # Connect bot signals to GUI
    bot.signals.message_received.connect(window.append_chat_message)
    bot.signals.log.connect(window.append_log)
    bot.signals.error.connect(lambda e: window.append_log(f"ERROR: {e}"))

    # Start bot and show window
    bot.start()
    window.show()

    app.aboutToQuit.connect(bot.stop)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
