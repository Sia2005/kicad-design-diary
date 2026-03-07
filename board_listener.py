import pcbnew
import os
import json
from datetime import datetime


class DesignDiaryListener(pcbnew.BOARD_LISTENER):

    def __init__(self, board, diary_folder):
        super().__init__()
        self.board = board
        self.diary_folder = diary_folder
        os.makedirs(self.diary_folder, exist_ok=True)

    def get_components(self):
        components = {}
        for fp in self.board.GetFootprints():
            components[fp.GetReference()] = {
                "value": fp.GetValue(),
                "footprint": fp.GetFPIDAsString()
            }
        return components

    def get_last_snapshot(self):
        snapshots = sorted([f for f in os.listdir(self.diary_folder) if f.endswith(".json")])
        if snapshots:
            path = os.path.join(self.diary_folder, snapshots[-1])
            with open(path, "r") as f:
                data = json.load(f)
                return data.get("components", {})
        return {}

    def save_snapshot(self, changes):
        current = self.get_components()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
        snapshot = {
            "timestamp": timestamp,
            "components": current,
            "changes": changes
        }
        path = os.path.join(self.diary_folder, filename)
        with open(path, "w") as f:
            json.dump(snapshot, f, indent=2)
        print(f"Design Diary: {len(changes)} change(s) saved")

    def OnBoardItemAdded(self, board, item):
        try:
            fp = pcbnew.Cast_to_FOOTPRINT(item)
            if fp:
                changes = [f"Added component {fp.GetReference()} with value {fp.GetValue()}"]
                self.save_snapshot(changes)
        except:
            pass

    def OnBoardItemRemoved(self, board, item):
        try:
            fp = pcbnew.Cast_to_FOOTPRINT(item)
            if fp:
                changes = [f"Deleted component {fp.GetReference()}"]
                self.save_snapshot(changes)
        except:
            pass

    def OnBoardItemChanged(self, board, item):
        try:
            fp = pcbnew.Cast_to_FOOTPRINT(item)
            if fp:
                previous = self.get_last_snapshot()
                ref = fp.GetReference()
                new_value = fp.GetValue()
                if ref in previous and previous[ref]["value"] != new_value:
                    changes = [f"Changed value of {ref} from {previous[ref]['value']} to {new_value}"]
                    self.save_snapshot(changes)
        except:
            pass
