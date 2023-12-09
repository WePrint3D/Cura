# Copyright (c) 2021 Ultimaker B.V.
# The PostProcessingPlugin is released under the terms of the AGPLv3 or higher.

# Modification 06.09.2020
# add checkbox, now you can choose and use configuration from the firmware itself.


import re #To perform the search and replace 

from typing import List
from ..Script import Script

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

            if (first_tool in layer or second_tool in layer) and init_state == 0:
                init_state = 1
                for line_number, line in enumerate(lines):
                    if first_tool in line :
                        active_tool = first_tool
                        break
                    elif second_tool in line:
                        active_tool = second_tool
                        break

            elif active_tool == second_tool and first_tool in layer and init_state == 1:
                #Create a str from layer after the first tool line number to the last four "\n" lines before ";TIME_ELAPSED:"
                n_layer = '\n'.join(lines[1:])
                new_layer = lines[0] + "\n" + first_tool + "\n" + n_layer.split(first_tool)[1]
                # Find the last line containing "Z"
                for line_number, line in enumerate(lines):
                    if "Z" in line:
                        last_z_line = line_number
                prev_last_four_first = '\n'.join(lines[last_z_line:])
                new_layer = new_layer.split(prev_last_four_first)[0] + "\n" + second_tool + "\n" + prev_last_four_second + "\n" + n_layer.split(first_tool)[0]
                active_tool = first_tool

            elif active_tool == first_tool and second_tool in layer and init_state == 1:
                #Create a str from layer after the second tool line number to the last four "\n" lines before ";TIME_ELAPSED:"
                new_layer = first_tool + "\n" + prev_last_four_first + layer
                for line_number, line in enumerate(lines):
                    if "Z" in line:
                        last_z_line = line_number
                prev_last_four_second = '\n'.join(lines[last_z_line:])
                new_layer = new_layer.split(prev_last_four_second)[0]
                active_tool = second_tool

            elif active_tool == second_tool and not first_tool in layer and init_state == 1:
                prev_last_four_second = '\n'.join(lines[-5:])

            data[layer_number] = new_layer
        return data
