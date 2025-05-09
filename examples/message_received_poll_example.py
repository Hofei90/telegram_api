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
    bot = api.Bot(CONFIG["telegram"]["token"])
    while True:
        messages = bot.get_updates()
        for message in messages:
            print("Gesamte Rückgabe mit sämlichen Informationen:")
            print(message)
            print(f"Nur Text: {message['message']['text']}")


if __name__ == "__main__":
    main()
