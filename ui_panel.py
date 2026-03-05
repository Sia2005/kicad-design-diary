import wx
import os
import json


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
        wx.MessageBox("Export feature coming soon!", "KiCad Design Diary", wx.OK | wx.ICON_INFORMATION)
