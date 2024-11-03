"""
This module contains all the constants used in the bot.
"""

__all__ = (
    "NaturalLang",
    "whois",
    "bws_replacement",
    "coin"
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