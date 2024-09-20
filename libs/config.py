import os, yaml

class Config:
  def __init__(self, filename):
    self.__conf = {}
    with open(filename) as stream:
      self.__conf = yaml.safe_load(stream)
    self.app_port = self.__get_int("APP_PORT")
    self.db_url = self.__get_string("DB_URL")

  def __get_string(self, key):
    return os.environ.get(key) if key in os.environ else self.__conf[key]

  def __get_int(self, key):
    return int(self.__get_string(key))

config = Config(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yml"))
