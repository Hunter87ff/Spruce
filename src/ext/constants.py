"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2022 hunter87.dev@gmail.com
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

 This module contains all the constants used in the bot.
"""


__all__ = (
    "NaturalLang",
    "whois",
    "bws_replacement",
    "coin",
    "say",
    "history",
    "name",
    "unfair",
    "repl_yes",
)

from enum import Enum



class NaturalLang(Enum):
    Afrikaans = "af"
    Arabic = "ar"
    Assamese = "as"
    Bengali = "bn"
    Chinese = "zh-Hans"
    English = "en"
    French = "fr"
    Greek = "el"
    Gujarati = "gu"
    Hindi = "hi"
    Japanese = "ja"
    Kannada = "kn"
    Marathi = "mr"
    Nepali = "ne"
    Odia = "or"
    Polish = "pl"
    Portuguese = "pt"
    Punjabi = "pa"
    Russian = "ru"
    Spanish = "es"
    Vietnamese = "vi"


class TimeZone(Enum):
    Asia_Kolkata = "Asia/Kolkata"
    Asia_Tokyo = "Asia/Tokyo"
    Asia_Shanghai = "Asia/Shanghai"
    Asia_Singapore = "Asia/Singapore"
    Asia_Dubai = "Asia/Dubai"
    Asia_Bangkok = "Asia/Bangkok"
    Asia_Hong_Kong = "Asia/Hong_Kong"
    Asia_Bangladesh = "Asia/Dhaka"
    Asia_Nepal = "Asia/Kathmandu"



# whoiss command assets
whois = [
    "Noob","Unknown Person",
    "kya pata mai nehi janta",
    "bohot piro", 
    "Bohot E-smart",
    "Dusro Ko Jan Ne Se Pehle Khud Ko Jan Lo",
    "Nalla", 
    "Bohot achha",
    "bohooooooooot badaaaaa Bot",
    "Nehi bolunga kya kar loge", 
    "insan", 
    "bhoot", 
    "bhagwan", 
    "e-smart ultra pro max"
    ]


# good words about a person
bws_replacement = {
    "awesome",
    "amazing",
    "cool",
    "nice",
    "good",
    "great",
    "smart",
    "intelligent",
    "kind",
    "helpful",
    "friendly",
    "funny",
    "beautiful",
    "handsome",
    "pretty",
    "cute",
    "attractive",
    "charming",
    "lovely",
}

coin = [
    "975413333291335702", 
    "975413366493413476"
]

say:list[str] = [
    "bolo ki", 
    "say", 
    "bolo", 
    "bolie", 
    "kaho"
]

history=[
    {"role" : "model", "parts": [
        "I'm a Discord bot! named Spruce. I can manage esports tournaments, scrims, tickets, moderation and more!",
        "My developer is hunter87 I often also call him as friend(buddy)",
        "I love to chat in a short amount of words",
        "I'm a good bot but sometime I become savage(mostly), funny, helpful, creazy!",
        ]
    },
]

name = {
    "my name", 
    "mera nam kya hai", 
    "what is my name", 
    "do you know my name"
}

unfair = [
    {"q":"me harami", "a":"aap harami ho"}, 
    {"q":"me useless", "a":"me really useful yes i know"}, 
    {"q":"mein harami", "a":"aap harami nehi ho!! kya baat kar rhe ho"}, 
    {"q":"i am a dog", "a":"im a bot!! Spruce Bot 😎"}
]

repl_yes = [
    "ohh", 
    "okey", 
    "hm"
]
# TEXT CONSTANTS
PROCESSING = "Processing..."
