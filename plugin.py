import pcbnew
import os
import json
from datetime import datetime


class DesignDiaryPlugin(pcbnew.ActionPlugin):

    def defaults(self):
        self.name = "KiCad Design Diary"
        self.category = "Design History"
        self.description = "Automatically tracks every change to your design in plain English"
        self.show_toolbar_button = True

    def Run(self):
        board = pcbnew.GetBoard()
        board_path = board.GetFileName()

        if not board_path:
            print("Design Diary: Please save your project first.")
            return

        project_folder = os.path.dirname(board_path)
        diary_folder = os.path.join(project_folder, ".design_diary")
        os.makedirs(diary_folder, exist_ok=True)

        # Read current components
        current_components = {}
        for fp in board.GetFootprints():
            current_components[fp.GetReference()] = {
                "value": fp.GetValue(),
                "footprint": fp.GetFPIDAsString()
            }

        # Load previous snapshot if it exists
        previous_components = {}
        snapshots = sorted([f for f in os.listdir(diary_folder) if f.endswith(".json")])
        if snapshots:
            last_snapshot_path = os.path.join(diary_folder, snapshots[-1])
            with open(last_snapshot_path, "r") as f:
                last_snapshot = json.load(f)
                previous_components = last_snapshot.get("components", {})

        # Run diff engine
        changes = []
        for ref in current_components:
            if ref not in previous_components:
                changes.append(f"Added component {ref} with value {current_components[ref]['value']}")
            elif current_components[ref]['value'] != previous_components[ref]['value']:
                changes.append(f"Changed value of {ref} from {previous_components[ref]['value']} to {current_components[ref]['value']}")
        for ref in previous_components:
            if ref not in current_components:
                changes.append(f"Deleted component {ref}")

        # Save new snapshot
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

        # Print result
        if changes:
            msg = f"Design Diary: {len(changes)} change(s) detected — {changes[0]}"
        else:
            msg = "Design Diary: No changes detected since last snapshot."

        print(msg)
