# Copyright (c) 2021 Ultimaker B.V.
# The PostProcessingPlugin is released under the terms of the AGPLv3 or higher.

# Modification 06.09.2020
# add checkbox, now you can choose and use configuration from the firmware itself.


import re #To perform the search and replace 

from typing import List
from ..Script import Script

# TODO: Control of the Water Vaporizer 
# TODO: Define the Extruder control Parameter
#           - Voltage control
#           - Vaporizer time

class ExtruderControl(Script):

    """Performs a search-and-replace on all g-code.

    Due to technical limitations, the search can't cross the border between
    layers.
    """

    def getSettingDataString(self):
        return """{
            "name": "Extruder Control",
            "key": "ExtruderControl",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "VaporizerEnable":
                {
                    "label": "Enable Vaporizer",
                    "description": ".",
                    "type": "bool",
                    "default_value": false
                },
                "Time":
                {
                    "label": "Time",
                    "description": "Time that the part stays in the furnace in minutes.",
                    "type": "str",
                    "default_value": ""
                }
            }
        }"""

    def execute(self, data):
        # search_string = self.getSettingValueByKey("search")
        # if not self.getSettingValueByKey("is_regex"):
        #     search_string = re.escape(search_string) #Need to search for the actual string, not as a regex.
        # search_regex = re.compile(search_string)

        # replace_string = self.getSettingValueByKey("replace")

        # for layer_number, layer in enumerate(data):
        #     data[layer_number] = re.sub(search_regex, replace_string, layer) #Replace all.

        return data
