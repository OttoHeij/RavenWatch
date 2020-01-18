#!/usr/bin/env python
__author__ = "James Burnett"
__copyright__ = "Copyright (C) James Burnett (https://jamesburnett.io)"
__license__ = "GNU AGPLv3"
__maintainer__ = "James Burnett"
__email__ = "james@jamesburnett.io"
__status__ = "Development"

import json

class Config:
    def __init__(self,config_file):
        self.data = None
        self.isloaded = False
        try:
            with open(config_file) as f:
                self.data = json.load(f)
                self.isloaded = True
        except json.decoder.JSONDecodeError:
            print("Json syntax problem in config file.")
        except:
            print("Problem with config file")

            
