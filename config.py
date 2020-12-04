from configparser import ConfigParser

config = ConfigParser()
config.optionxform = str

config.read('config.ini')


def get(section, option):
    return config.get(section, option, fallback=None)


def getint(section, option):
    return config.getint(section, option, fallback=-1)
