import sys, os, pcbnew

sys.path.insert(0, r'C:\Users\siaup\Documents\KiCad\9.0\scripting\plugins')

try:
    from kicad_design_diary.plugin import DesignDiaryPlugin
    _diary_plugin = DesignDiaryPlugin()
    _diary_plugin.register()
    print("Design Diary: Tracking silently. Call plugin.Run() to view history.")
except Exception as e:
    print(f"Design Diary: Failed to load — {e}")
