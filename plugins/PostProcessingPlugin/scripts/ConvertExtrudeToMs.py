# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
# Created by Wayne Porter

from ..Script import Script

class ConvertExtrudeToMs(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Convert Extrude to M codes",
            "key": "ConvertExtrudeToMs",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "M_activate":
                {
                    "label": "M code to activate the extruder pin",
                    "description": "M code to activate the extruder pin",
                    "type": "str",
                    "default_value": "84"
                },
                "M_deactivate":
                {
                    "label": "M code to deactivate the extruder pin",
                    "description": "M code to deactivate the extruder pin",
                    "type": "str",
                    "default_value": "85"
                }
            }
        }"""

    def execute(self, data):
        M_activate = self.getSettingValueByKey("M_activate")
        M_deactivate = self.getSettingValueByKey("M_deactivate")
        for layer_number,layer in enumerate(data):
            lines = layer.split("\n")
            for line_number, line in enumerate(lines):
                if ';' in line:
                    lines[line_number] = line
                elif 'G92' in line:
                    lines[line_number] = ''
                elif 'G0' in line:
                    lines[line_number] = line.split('\n')[0] + M_deactivate
                elif 'G1' in line:
                    lines[line_number] = line.split('E')[0] + M_activate
                else:
                    lines[line_number] = line
            new_layer = "\n".join(lines)
            data[layer_number] = new_layer
        return data
