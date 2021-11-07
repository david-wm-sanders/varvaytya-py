import sys

from app import app, db
from app.models import World, ItemGroup, ItemDef, Realm, Player, Account

from loguru import logger


@app.shell_context_processor
def sh():
    return {"db": db,
            "World": World, "ItemGroup": ItemGroup, "ItemDef": ItemDef,
            "Realm": Realm, "Player": Player, "Account": Account}


if __name__ == '__main__':
    # configure some logging
    log_fmt_c = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
                "<level>{level: <8}</level> |{level.icon}  " \
                "<level>{message}</level>"
    # clean up the default logger
    logger.remove()
    logger.configure(handlers=[{"sink": sys.stderr, "format": log_fmt_c, "level": "DEBUG"}])
    logger.level("INFO", icon="🔔")

    logger.info(f"Starting varvaytya!")
    app.run(debug=True)
