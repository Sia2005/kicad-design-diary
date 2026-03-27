import pcbnew
import os
import json
from datetime import datetime
import wx

_listener = None
_plugin_instance = None

class DesignDiaryPlugin(pcbnew.ActionPlugin):

    def defaults(self):
        self.name = "KiCad Design Diary"
        self.category = "Design History"
        self.description = "Automatically tracks every change to your design in plain English"
        self.show_toolbar_button = True

    def Run(self):
        global _listener, _plugin_instance
        _plugin_instance = self
        board = pcbnew.GetBoard()
        board_path = board.GetFileName()
        if not board_path:
            print("Design Diary: Please save your project first.")
            return
        project_folder = os.path.dirname(board_path)
        diary_folder = os.path.join(project_folder, ".design_diary")
        os.makedirs(diary_folder, exist_ok=True)
        if _listener is None:
            from kicad_design_diary.board_listener import DesignDiaryListener
            _listener = DesignDiaryListener(board, diary_folder)
            board.AddListener(_listener)
            print("Design Diary: Auto-tracking enabled.")
        current_components = {}
        for fp in board.GetFootprints():
            current_components[fp.GetReference()] = {
                "value": fp.GetValue(),
                "footprint": fp.GetFPIDAsString()
            }
        previous_components = {}
        snapshots = sorted([f for f in os.listdir(diary_folder) if f.endswith(".json") and not f.startswith("SCH_")])
        if snapshots:
            last_snapshot_path = os.path.join(diary_folder, snapshots[-1])
            with open(last_snapshot_path, "r") as f:
                last_snapshot = json.load(f)
                previous_components = last_snapshot.get("components", {})
        changes = []
        for ref in current_components:
            if ref not in previous_components:
                changes.append(f"Added component {ref} with value {current_components[ref]['value']}")
            elif current_components[ref]['value'] != previous_components[ref]['value']:
                changes.append(f"Changed value of {ref} from {previous_components[ref]['value']} to {current_components[ref]['value']}")
        for ref in previous_components:
            if ref not in current_components:
                changes.append(f"Deleted component {ref}")
        sch_files = [f for f in os.listdir(project_folder) if f.endswith(".kicad_sch")]
        if sch_files:
            sch_path = os.path.join(project_folder, sch_files[0])
            from kicad_design_diary.schematic_tracker import SchematicTracker
            sch_tracker = SchematicTracker(diary_folder)
            sch_changes = sch_tracker.take_snapshot(sch_path)
            changes.extend(sch_changes)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
        snapshot_path = os.path.join(diary_folder, filename)
        snapshot = {
            "timestamp": timestamp,
            "board_file": board_path,
            "components": current_components,
            "changes": changes
        }
        with open(snapshot_path, "w") as f:
            json.dump(snapshot, f, indent=2)
        from kicad_design_diary.ui_panel import DiaryPanel
        frame = DiaryPanel(None, diary_folder)
