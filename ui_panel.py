import wx
import os
import json
from datetime import datetime


class DiaryPanel(wx.Frame):

    def __init__(self, parent, diary_folder):
        super().__init__(parent, title="KiCad Design Diary", size=(600, 500))
        self.diary_folder = diary_folder
        self.init_ui()
        self.load_entries()
        self.Centre()
        self.Show()

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(panel, label="KiCad Design Diary — Change Timeline")
        title_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        main_sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        self.list_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, "Timestamp", width=160)
        self.list_ctrl.InsertColumn(1, "Changes", width=400)
        main_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        refresh_btn = wx.Button(panel, label="Refresh")
        refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        btn_sizer.Add(refresh_btn, 0, wx.ALL, 5)
        export_btn = wx.Button(panel, label="Export Report")
        export_btn.Bind(wx.EVT_BUTTON, self.on_export)
        btn_sizer.Add(export_btn, 0, wx.ALL, 5)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        panel.SetSizer(main_sizer)

    def load_entries(self):
        self.list_ctrl.DeleteAllItems()
        if not os.path.exists(self.diary_folder):
            return
        snapshots = sorted([f for f in os.listdir(self.diary_folder) if f.endswith(".json")])
        for snapshot_file in reversed(snapshots):
            path = os.path.join(self.diary_folder, snapshot_file)
            with open(path, "r") as f:
                data = json.load(f)
            timestamp = data.get("timestamp", "Unknown")
            changes = data.get("changes", [])
            if changes:
                changes_text = " | ".join(changes)
            else:
                changes_text = "No changes detected"
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), timestamp)
            self.list_ctrl.SetItem(index, 1, changes_text)

    def on_refresh(self, event):
        self.load_entries()

    def on_export(self, event):
        # Ask user where to save
        with wx.FileDialog(self, "Save Report", wildcard="HTML files (*.html)|*.html",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            export_path = dlg.GetPath()

        # Load all snapshots
        snapshots = sorted([f for f in os.listdir(self.diary_folder) if f.endswith(".json")])
        entries = []
        for snapshot_file in reversed(snapshots):
            path = os.path.join(self.diary_folder, snapshot_file)
            with open(path, "r") as f:
                data = json.load(f)
            entries.append(data)

        # Generate HTML report
        html = """<!DOCTYPE html>
<html>
<head>
<title>KiCad Design Diary Report</title>
<style>
    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
    h1 { color: #1F3864; }
    h2 { color: #2E75B6; }
    .entry { background: white; border-left: 4px solid #2E75B6; margin: 15px 0; padding: 15px; border-radius: 4px; }
    .timestamp { color: #888; font-size: 0.9em; }
    .change { background: #EBF3FB; padding: 5px 10px; margin: 5px 0; border-radius: 3px; }
    .no-change { color: #aaa; font-style: italic; }
</style>
</head>
<body>
<h1>KiCad Design Diary</h1>
<h2>Complete Design Change History</h2>
<p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
<hr>
"""
        for entry in entries:
            timestamp = entry.get("timestamp", "Unknown")
            changes = entry.get("changes", [])
            html += f'<div class="entry">'
            html += f'<div class="timestamp">{timestamp}</div>'
            if changes:
                for change in changes:
                    html += f'<div class="change">• {change}</div>'
            else:
                html += '<div class="no-change">No changes detected</div>'
            html += '</div>'

        html += "</body></html>"

        with open(export_path, "w") as f:
            f.write(html)

        wx.MessageBox(f"Report saved to {export_path}", "Export Successful", wx.OK | wx.ICON_INFORMATION)
