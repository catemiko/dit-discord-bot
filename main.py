import logging
from discord.ext import commands

import sys

from bot import Bot
from database.db import DatabaseClient
import settings


def main() -> int:
    database_client = DatabaseClient(settings.DATABASE_URL, echo=False)
    database_client.init_db()

    logger = logging.getLogger("database.db")
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    help_command = commands.DefaultHelpCommand(no_category="Commands")
    bot = Bot(database=database_client, command_prefix="!", help_command=help_command)
    bot.run(settings.BOT_TOKEN)
    return 0


if __name__ == "__main__":
    sys.exit(main())
