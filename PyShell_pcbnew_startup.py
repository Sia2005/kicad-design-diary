### DEFAULT STARTUP FILE FOR KiCad Python Shell
# Enter any Python code you would like to execute when the PCBNEW python shell first runs.

# For example, uncomment the following lines to import the current board

# import pcbnew
# import eeschema
# board = pcbnew.GetBoard()
# sch = eeschema.GetSchematic()

import sys, os
sys.path.insert(0, r'C:\Users\siaup\Documents\KiCad\9.0\scripting\plugins')
from kicad_design_diary.plugin import DesignDiaryPlugin
DesignDiaryPlugin().register()
print('Design Diary: Auto-loaded successfully')
