#!/usr/bin/python3
"""
Telegram Bot API
Modul als Schnittstelle zur Kommunikation mit Telegram Bot API
"""

import json
import requests
from os import path

API_URL = "https://api.telegram.org/bot"


class Bot:
    def __init__(self, token):
        self.token = token
        self.botuser = None
        self.result = None
        self.file_ids = {}
        self.max_update_id = 0

    def get_me(self):
        """Auslesen der Botinformationen
        Das Resultat wird self.result abgelegt
        Das Userfeld in self.botuser

        Arg: None

        Returns:

        Bei erfolgreicher Abfrage: True
        Bei fehlerhafter Abfrage: False"""

        # Informationen abholen
        url = "{}{}/getMe".format(API_URL, self.token)
        r = requests.get(url)
        result = r.json()

        # Abfrage auswerten
        self.result = result
        if result["ok"]:
            self.botuser = result["result"]
            return True
        else:
            print("Abfrage fehlgeschlagen, Token ok?")
            return False

    def send_message(self, chat_id: str or int, text: str, parse_mode: str = None,
                     disable_web_page_preview: bool = None, disable_notification: bool = None,
                     reply_to_message_id: int = None, reply_markup=None):
        """Funktion zur Übermittlung von Nachrichten

        Args:
        chat_id: ID des Chats zur Übermittlung der Nachricht
        text: Inhalt der Nachricht
        parse_mode: optional, Stringinhalt nur "HTML" oder "Markdown", gibt an ob die Nachricht Formatierungen enthält
        disable_web_page_preview: optional,
        disable_notification: optional,
        reply_to_message_id: optional,
        reply_markup: optional,

        Returns:
        True: Sendung erfolgreich versendet
        False: Sendung fehlerhaft
        """

        params = {"chat_id": str(chat_id)}
        if isinstance(text, str):
            params["text"] = text
        if isinstance(parse_mode, str):
            params["pars_mode"] = parse_mode
        if isinstance(disable_web_page_preview, bool):
            params["disable_web_page_preview"] = disable_web_page_preview
        if isinstance(disable_notification, bool):
            params["disable_notification"] = disable_notification
        if isinstance(reply_to_message_id, int):
            params["reply_to_message_id"] = reply_to_message_id
        if reply_markup is not None:
            params["reply_markup"] = reply_markup

        url = "{}{}/sendMessage".format(API_URL, self.token)
        r = requests.get(url, params=params)
        result = check_results(r, "send_message")
        return result

    def send_photo(self, chat_id, photo, caption: str = None, parse_mode: str = None, disable_notification: bool = None,
                   reply_to_message_id: int = None, reply_markup = None):
        r = None
        new_file_id = False
        data = {"chat_id": chat_id}
        url = "{}{}/sendPhoto".format(API_URL, self.token)
        if photo in self.file_ids:
            data["photo"] = self.file_ids[photo]
            r = requests.get(url, params=data)
        elif path.isfile(photo):
            files = {"photo": open(photo, "rb")}
            r = requests.post(url, files=files, data=data)
            new_file_id = True
        else:
            try:
                anfrage = requests.get(photo)
            except requests.exceptions.MissingSchema:
                pass
            else:
                if "image" in anfrage.headers["Content-Type"]:
                    data["photo"] = photo
                    r = requests.get(url, params=data)
                    new_file_id = True
        result = check_results(r, "send_photo")
        if new_file_id:
            self.file_ids[str(photo)] = result["result"]["photo"][0]["file_id"]
        return result

    def get_updates(self, offset: int = None, limit: int = None, timeout: int = None, allowed_updates=None,
                    automatic_set_max_update_id: bool = True):
        """ Funktion zum Empfangen von neuen Nachrichten"""
        # Update anhand der Parameter vorbereiten
        url = "{}{}/getUpdates".format(API_URL, self.token)
        if automatic_set_max_update_id:
            offset = self.max_update_id
        if offset is not None:
            if isinstance(offset, int):
                url += "?offset={}".format(offset)
            else:
                raise TypeError("Nur Integer erlaubt!")
        if limit is not None:
            if isinstance(limit, int):
                if 0 <= limit <= 100:
                    url += "?limit={}".format(limit)
                else:
                    raise ValueError("Nur Zahlenbereich zwischen 0-100 erlaubt")
        if timeout is not None:
            if isinstance(timeout, int):
                url += "?timeout={}".format(timeout)
            else:
                raise TypeError("Nur Integer erlaubt!")
        if allowed_updates is not None:
            url += "?allowed_updates={}".format(allowed_updates)

        # Update abholen
        r = requests.get(url)
        self.result = r.json()
        if self.result["ok"]:
            self.set_max_update_id(self.result["result"])

        for message in self.result["result"]:
            yield message
        # Todo: Logging einbauen print(self.result)

    def set_max_update_id(self, result):
        update_ids = [update_id["update_id"] for update_id in result]
        if update_ids:
            self.max_update_id = max([update_id["update_id"] for update_id in result]) + 1
        else:
            self.max_update_id = None


def reply_keyboard_markup(data, resize_keyboard=None, one_time_keyboard=None, selective=None):
    """Funktion zur Erstellung der reply_markup Variable zur Übermittlung an die API
    data Format:
    Listindex 0: Keyboardfelder (Typ Liste) Kann alleine übermittelt werden
    Listindex 1:
    Beispiel:  [["Taste 1", ["Option1", "Option2"]], ["Taste 2"]]"""

    keyboard = {}
    buttons = []
    for daten in data:
        if len(daten) == 1:  # Nur Tasten ohne Optionen
            buttons.append({"text": str(daten[0])})
        if len(daten) == 2:  # Mit Optionen
            if isinstance(daten[1][0], bool) and isinstance(daten[1][1], bool):
                buttons.append({"text": str(daten[0]), "request_contact": daten[1][0], "request_location": daten[1][1]})
            else:
                raise ValueError("Nur Bool Werte übermitteln als Optionen")
    keyboard["keyboard"] = [buttons]
    if resize_keyboard is not None:
        keyboard["resize_keyboard"] = resize_keyboard
    if one_time_keyboard is not None:
        keyboard["one_time_keyboard"] = one_time_keyboard
    if selective is not None:
        keyboard["selective"] = selective
    reply_markup = json.dumps(keyboard)
    return reply_markup


def reply_keyboard_remove(selective=None):
    keyboard = {"remove_keyboard": True}
    if selective is not None:
        if isinstance(selective, bool):
            keyboard["selective"] = selective
        else:
            raise TypeError("Nur Boolean erlaubt")
    reply_markup = json.dumps(keyboard)
    return reply_markup


def force_reply(selective=None):
    daten = {"force_reply": True}
    if selective is not None:
        if isinstance(selective, bool):
            daten["selective"] = selective
        else:
            raise TypeError("Nur Boolean erlaubt")
    reply_markup = json.dumps(daten)
    return reply_markup


def check_results(result, text):
    result = result.json()
    if result["ok"]:
        print("{} erfolgreich".format(text))  # Todo: Logging einbauen
        print(result)
    else:
        print("{} fehlgeschlagen".format(text))
        print(result)
    return result
