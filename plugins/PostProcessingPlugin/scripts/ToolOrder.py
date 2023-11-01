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

class ToolOrder(Script):

    """Performs a search-and-replace on all g-code.

    Due to technical limitations, the search can't cross the border between
    layers.
    """

    def getSettingDataString(self):
        return """{
            "name": "Tool Order",
            "key": "ToolOrder",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "first_tool":
                {
                    "label": "First tool name",
                    "description": "Name of the first tool each layer.",
                    "type": "str",
                    "default_value": "T1"
                },
                "second_tool":
                {
                    "label": "Second tool name",
                    "description": "Name of the second tool each layer.",
                    "type": "str",
                    "default_value": "T0"
                }
            }
        }"""


    def execute(self, data):
        first_tool = self.getSettingValueByKey("first_tool")
        second_tool = self.getSettingValueByKey("second_tool")

        active_tool = ''
        init_state = 0

        for layer_number,layer in enumerate(data):
            lines = layer.split("\n")
            new_layer = layer

            if first_tool in layer and second_tool in layer and init_state == 0:
                init_state = 1
                for line_number, line in enumerate(lines):
                    if first_tool in line :
                        active_tool = first_tool
                        break
                    elif second_tool in line:
                        active_tool = second_tool
                        break


            elif active_tool == first_tool and second_tool in layer:
                lines[0] = lines[0] + "\n" + first_tool
                active_tool = second_tool
                new_layer = "\n".join(lines)

            elif active_tool == second_tool and first_tool in layer:
                #Create a list from lines after the first tool line number
                new_layer = first_tool + "\n" + layer.split(first_tool)[1] + "\n" + second_tool + "\n" + layer.split(first_tool)[0]
                active_tool = first_tool

            prev_last_four = lines[-4:] 
            data[layer_number] = new_layer
        return data
