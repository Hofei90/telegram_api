import os

import toml

import telegram_bot_api as api


def config_laden():
    configfile = os.path.join(SKRIPTPFAD, "example_cfg.toml")
    with open(configfile) as file:
        return toml.loads(file.read())


SKRIPTPFAD = os.path.abspath(os.path.dirname(__file__))
CONFIG = config_laden()


def main():
    user = CONFIG["telegram"]["user"]
    bot = api.Bot(CONFIG["telegram"]["token"])
    bot.send_message(user, CONFIG["text"])


if __name__ == "__main__":
    main()