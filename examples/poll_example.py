import os
import time

import toml

import telegram_bot_api as api


def config_laden():
    configfile = os.path.join(SKRIPTPFAD, "vorlage_example_cfg.toml")
    with open(configfile) as file:
        return toml.loads(file.read())


SKRIPTPFAD = os.path.abspath(os.path.dirname(__file__))
CONFIG = config_laden()

USER = CONFIG["telegram"]["user"]
BOT = api.Bot(CONFIG["telegram"]["token"])

ANTWORTEN = ["Komme gleich", "1 Min", "5 Min"]


class LiveNachricht:
    def __init__(self, options):
        self.antworten = {}
        self.option_id_mapping = {}
        for option_id, option in enumerate(options):
            self.option_id_mapping[option_id] = option
            self.antworten[option_id] = [0]
        self.id = None
        r = BOT.send_message(USER, self.text_generieren())
        print(r)
        self.message_id = r["result"]["message_id"]

    def text_generieren(self):
        text = ""
        for key, value in self.antworten.items():
            kategorie = option_id_mapping_value(self.option_id_mapping, key)
            anzahl = value[0]
            namen = ",".join(value[1:])
            text = f"{text} {kategorie}: Gesamt: {anzahl}, {namen}\n"
        return text

    def add_antwort(self, antwort):
        print(antwort["option_ids"][0])
        self.antworten[int(antwort["option_ids"][0])][0] += 1
        self.antworten[antwort["option_ids"][0]].append(antwort["user"]["first_name"])
        text = self.text_generieren()
        r = BOT.edit_message_text(USER, text, self.message_id)
        print(r)


def option_id_mapping_value(option_in_mapping, id_):
    return option_in_mapping[id_]


def einsatz_erstellen(poll_frage, optionen):
    result = BOT.send_poll(USER, poll_frage, optionen, is_anonymous=False)
    return result


def main():
    einsatz = "Einsatz XY"
    r = einsatz_erstellen(einsatz, ANTWORTEN)
    live_nachricht = LiveNachricht(ANTWORTEN)
    while True:
        r = BOT.get_updates()
        print(r)
        for antwort in r:
            if "poll_answer" in antwort:
                live_nachricht.add_antwort(antwort["poll_answer"])
        time.sleep(0.5)


if __name__ == "__main__":
    main()
