import random

def block_times(block):
    if block == "dirtseed":
        return 60
    elif block == "lavaseed":
        return 90
    elif block == "stoneseed":
        return 90
    elif block == "cloudseed":
        return 300
    elif block == "crateseed":
        return 180
    elif block == "whiteseed":
        return 180
    elif block == "platformseed":
        return 360
    elif block == "tuxedoshirtseed":
        return 720
    elif block == "fireshirtseed":
        return 720
    elif block == "cavebgseed":
        return 90
    elif block == "dirtbgseed":
        return 60
    else:
        return 60
