from random import randint
from enum import Enum



class Color:
    blurple = 0x7289da
    greyple = 0x99aab5
    d_grey = 0x546e7a
    d_theme = 0x36393F
    l_grey = 0x979c9f
    d_red = 0x992d22
    red = 0xff0000
    d_orange = 0xa84300
    orange = 0xe67e22
    d_gold = 0xc27c0e
    gold = 0xf1c40f
    magenta = 0xe91e63
    purple = 0x9b59b6
    d_blue = 0x206694
    blue = 0x0000ff
    green = 0x00ff00
    d_green = 0x1f8b4c
    pink = 0xff0066
    teal = 0x1abc9c
    cyan = 0x1abc9c
    d_teal = 0x11806a
    yellow = 0xffff00

    @staticmethod
    def random(colorRange: int = 0xFFFFFF):
        return randint(0, colorRange)
    



class ColorOptions(Enum):
    blurple = Color.purple
    red = Color.red
    orange = Color.orange
    gold = Color.gold
    magenta = Color.magenta
    purple = Color.purple
    blue = Color.blue
    green = Color.green
    deep_green = Color.d_green
    pink = Color.pink
    teal = Color.teal
    cyan = Color.cyan
    deep_teal = Color.d_teal
    yellow = Color.yellow
    grey = Color.greyple
    dark_grey = Color.d_grey
    dark_theme = Color.d_theme
    dark_red = Color.d_red