# Copyright (c) 2021 Ultimaker B.V.
# The PostProcessingPlugin is released under the terms of the AGPLv3 or higher.

# Modification 06.09.2020
# add checkbox, now you can choose and use configuration from the firmware itself.


import re #To perform the search and replace 

from typing import List
from ..Script import Script

class ExtrusionControl(Script):

    """Performs a search-and-replace on all g-code.

    Due to technical limitations, the search can't cross the border between
    layers.
    """

    def getSettingDataString(self):
        return """{
            "name": "Extrusion Control",
            "key": "ExtrusionControl",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "M_start_extrusion":
                {
                    "label": "M code to start extrusion",
                    "description": "M code to start extrusion.",
                    "type": "str",
                    "default_value": "M803"
                },
                "M_stop_extrusion":
                {
                    "label": "M code to stop extrusion",
                    "description": "M code to stop extrusion.",
                    "type": "str",
                    "default_value": "M805"
                },
                "Extrusion_stop_time":
                {
                    "label": "Extrusion stop time",
                    "description": "Time for the extruder to stop add the end of a move in miliseconds",
                    "type": "str",
                    "default_value": "1200"
                },
                "Vaporisation_enable":
                {
                    "label": "Water Vaporisation",
                    "description": "Enable Water Vaporisation between layers.",
                    "type": "bool",
                    "default_value": false
                },
                "Vaporisation_each":
                {
                    "label": "Vaporisation each k layer",
                    "description": "Choose the number of layer between each vaporisation.",
                    "type": "enum",
                    "options": {
                        "1": "1",
                        "2": "2",
                        "3": "3",
                        "4": "4",
                        "5": "5",
                        "6": "6",
                        "7": "7",
                        "8": "8",
                        "9": "9",
                        "10": "10"
                    },
                    "default_value": "1",
                    "enabled": "Vaporisation_enable"
                },
                "M_vaporiation_start":
                {
                    "label": "M code to start vaporisation",
                    "description": "M code to start water vaporisation.",
                    "type": "str",
                    "default_value": "M807",
                    "enabled": "Vaporisation_enable"
                },
                "M_vaporiation_stop":
                {
                    "label": "M code to stop vaporisation",
                    "description": "M code to stop water vaporisation.",
                    "type": "str",
                    "default_value": "M808",
                    "enabled": "Vaporisation_enable"
                },
                "Vaporisation_time":
                {
                    "label": "Vapor time",
                    "description": "Time of activation of the water vaporisation between layers in miliseconds.",
                    "type": "str",
                    "default_value": "1000",
                    "enabled": "Vaporisation_enable"
                },
                "Vaporisation_wait":
                {
                    "label": "Vapor wait to print time",
                    "description": "Time to wait before the restart of the print in miliseconds.",
                    "type": "str",
                    "default_value": "2000",
                    "enabled": "Vaporisation_enable"
                }
            }
        }"""


    def execute(self, data):
        M_activate = self.getSettingValueByKey("M_start_extrusion")
        M_deactivate = self.getSettingValueByKey("M_stop_extrusion")
        Extrusion_stop_time = self.getSettingValueByKey("Extrusion_stop_time")
        Vaporisation_enable = self.getSettingValueByKey("Vaporisation_enable")
        M_vaporiation_start = self.getSettingValueByKey("M_vaporiation_start")
        M_vaporiation_stop = self.getSettingValueByKey("M_vaporiation_stop")
        Vaporisation_time = self.getSettingValueByKey("Vaporisation_time")
        Vaporisation_wait = self.getSettingValueByKey("Vaporisation_wait")
        Vaporisation_each = int(self.getSettingValueByKey("Vaporisation_each"))

        init_state = 0
        extruder_state = 0

        for layer_number,layer in enumerate(data):
            lines = layer.split("\n")
            null_lines = []
            for line_number, line in enumerate(lines):
                
                if 'G1' in line and 'Z' in line and init_state == 0:
                    lines[line_number] = ''
                    null_lines.append(line_number)
                elif 'G0' in line and 'X' in line and 'Y' in line and 'Z' in line and init_state == 0:
                    lines[line_number] = line.split('Z')[0] + "\nG0 Z" +  line.split('Z')[1]
                    init_state = 1
                elif  'G0' in line and extruder_state == 1: # Add the Stop extrusion and Dwell
                    lines[line_number] = M_deactivate + "\n" + "G4 P" + Extrusion_stop_time + "\n" + line.split('\n')[0]
                    extruder_state = 0
                elif 'G92' in line and 'E' in line or 'E-' in line: # Remove the absolute extrusion
                    lines[line_number] = ''
                    null_lines.append(line_number)
                elif 'G1' in line and ('X' in line or 'Y' in line) and 'E' in line and extruder_state == 0: # Add the start extrusion
                    lines[line_number] = M_activate + "\n" + line.split('E')[0] + ";=== Start of extrusion ==="
                    extruder_state = 1
                elif 'G1' in line and 'E' in line:
                    lines[line_number] = line.split('E')[0] + ";=== Extrusion ==="
                elif 'G1' in line and not 'E' in line and extruder_state == 1:
                    lines[line_number] = M_deactivate + "\n" + "G4 P" + Extrusion_stop_time + "\n" + line.split('E')[0] + ";=== Stop of extrusion ==="
                    extruder_state = 0   
                elif 'M104' in line or 'M105' in line or 'M106' in line or 'M107' in line or 'M109' in line or 'M82' in line or 'M83' in line:
                    lines[line_number] = ''
                    null_lines.append(line_number)
                else:
                    lines[line_number] = line

                if ('T0' in line or 'T1' in line) and init_state == 1:
                    if extruder_state == 1:
                        lines[line_number] =  M_deactivate + "\n" + "G4 P" + Extrusion_stop_time + "\n" + line
                        extruder_state = 0
                    else: lines[line_number] = line

                if Vaporisation_enable and 'LAYER:' in line:
                    if (int(line.split('LAYER:')[1]) % Vaporisation_each) == 0:
                        lines[line_number] = M_vaporiation_start + "\n" + "G4 P" + Vaporisation_time + "\n" + M_vaporiation_stop + "\n"
                        if int(Vaporisation_wait) > 0:
                            lines[line_number] += "G4 P" + Vaporisation_wait + "\n" +  line.split('\n')[0]
                        else:
                            lines[line_number] += line.split('\n')[0]
                    else:
                        lines[line_number] = line.split('\n')[0]
            
            for i in sorted(null_lines, reverse=True): 
                lines.pop(i)
            new_layer = "\n".join(lines)
            data[layer_number] = new_layer
        return data
