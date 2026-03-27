import wx
import os
import json
from datetime import datetime


class ComponentHistoryFrame(wx.Frame):

    def __init__(self, parent, ref, diary_folder):
        super().__init__(parent, title=f"{ref} — Value History", size=(500, 400))
        self.ref = ref
        self.diary_folder = diary_folder
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(panel, label=f"Complete Value History — {ref}")
        title_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        self.list_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, "Timestamp", width=160)
        self.list_ctrl.InsertColumn(1, "Event", width=300)
        sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        panel.SetSizer(sizer)
        self.load_history()
        self.Centre()
        self.Show()

    def load_history(self):
        self.list_ctrl.DeleteAllItems()
        if not os.path.exists(self.diary_folder):
            return
        snapshots = sorted([f for f in os.listdir(self.diary_folder) if f.endswith(".json") and not f.startswith("SCH_")])
        for snapshot_file in snapshots:
            path = os.path.join(self.diary_folder, snapshot_file)
            with open(path, "r") as f:
                data = json.load(f)
            timestamp = data.get("timestamp", "Unknown")
            changes = data.get("changes", [])
            for change in changes:
                import re
                if re.search(r"\b" + self.ref + r"\b", change):
                    index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), timestamp)
                    self.list_ctrl.SetItem(index, 1, change)


class DiaryPanel(wx.Frame):

    def __init__(self, parent, diary_folder):
        super().__init__(parent, title="KiCad Design Diary", size=(700, 550))
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
        hint = wx.StaticText(panel, label="Tip: Double-click any row to see component value history")
        hint.SetForegroundColour(wx.Colour(100, 100, 100))
        main_sizer.Add(hint, 0, wx.LEFT | wx.BOTTOM, 10)
        self.list_ctrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, "Timestamp", width=160)
        self.list_ctrl.InsertColumn(1, "Changes", width=500)
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_double_click)
        main_sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        refresh_btn = wx.Button(panel, label="Refresh")
        refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        btn_sizer.Add(refresh_btn, 0, wx.ALL, 5)
        export_btn = wx.Button(panel, label="Export Report")
        export_btn.Bind(wx.EVT_BUTTON, self.on_export)
        btn_sizer.Add(export_btn, 0, wx.ALL, 5)
        history_btn = wx.Button(panel, label="Component History")
        history_btn.Bind(wx.EVT_BUTTON, self.on_component_history)
        btn_sizer.Add(history_btn, 0, wx.ALL, 5)
        sim_btn = wx.Button(panel, label="Mark Simulation Checkpoint")
        sim_btn.Bind(wx.EVT_BUTTON, self.on_simulation_checkpoint)
        btn_sizer.Add(sim_btn, 0, wx.ALL, 5)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        panel.SetSizer(main_sizer)

    def load_entries(self):
        self.list_ctrl.DeleteAllItems()
        if not os.path.exists(self.diary_folder):
            return
        snapshots = sorted([f for f in os.listdir(self.diary_folder) if f.endswith(".json") and not f.startswith("SCH_")])
        for snapshot_file in reversed(snapshots):
            path = os.path.join(self.diary_folder, snapshot_file)
            with open(path, "r") as f:
                data = json.load(f)
            timestamp = data.get("timestamp", "Unknown")
            changes = data.get("changes", [])
            if not changes:
                continue
            changes_text = " | ".join(changes) if changes else "No changes detected"
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), timestamp)
            self.list_ctrl.SetItem(index, 1, changes_text)

    def on_item_double_click(self, event):
        index = event.GetIndex()
        changes_text = self.list_ctrl.GetItemText(index, 1)
        import re
        refs = re.findall(r'\b([A-Z]+[0-9]+)\b', changes_text)
        if refs:
            ref = refs[0]
            ComponentHistoryFrame(self, ref, self.diary_folder)
        else:
            wx.MessageBox("No component reference found in this entry.", "KiCad Design Diary", wx.OK)

    def on_component_history(self, event):
        refs = self.get_all_refs()
        if not refs:
            wx.MessageBox("No components tracked yet.", "KiCad Design Diary", wx.OK)
            return
        dlg = wx.SingleChoiceDialog(self, "Select a component to view its history:", "Component History", refs)
        if dlg.ShowModal() == wx.ID_OK:
            ref = dlg.GetStringSelection()
            ComponentHistoryFrame(self, ref, self.diary_folder)
        dlg.Destroy()

    def get_all_refs(self):
        import re
        refs = set()
        snapshots = sorted([f for f in os.listdir(self.diary_folder) if f.endswith(".json") and not f.startswith("SCH_")])
        for snapshot_file in snapshots:
            path = os.path.join(self.diary_folder, snapshot_file)
            with open(path, "r") as f:
                data = json.load(f)
            for change in data.get("changes", []):
                found = re.findall(r'\b([A-Z]+[0-9]+)\b', change)
                refs.update(found)
        return sorted(list(refs))

    def on_simulation_checkpoint(self, event):
        import json
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = "SIM_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
        checkpoint = {
            "timestamp": timestamp,
            "type": "simulation_checkpoint",
            "changes": ["SIMULATION CHECKPOINT — Design state saved before eSim simulation"]
        }
        path = os.path.join(self.diary_folder, filename)
        with open(path, "w") as f:
            json.dump(checkpoint, f, indent=2)
        self.load_entries()
        wx.MessageBox(f"Simulation checkpoint saved at {timestamp}", "KiCad Design Diary", wx.OK | wx.ICON_INFORMATION)

    def on_refresh(self, event):
        self.load_entries()

    def on_export(self, event):
        with wx.FileDialog(self, "Save Report", wildcard="HTML files (*.html)|*.html",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            export_path = dlg.GetPath()

        snapshots = sorted([f for f in os.listdir(self.diary_folder) if f.endswith(".json") and not f.startswith("SCH_")])
        entries = []
        for snapshot_file in reversed(snapshots):
            path = os.path.join(self.diary_folder, snapshot_file)
            with open(path, "r") as f:
                data = json.load(f)
            if data.get("changes"):
                entries.append(data)

        total_changes = sum(len(e.get("changes", [])) for e in entries)
        total_sessions = len(entries)
        board_file = entries[0].get("board_file", "Unknown") if entries else "Unknown"
        board_name = os.path.basename(board_file) if board_file != "Unknown" else "Unknown"

        component_freq = {}
        for entry in entries:
            for change in entry.get("changes", []):
                import re
                parts = re.findall(r'\b([A-Z]+[0-9]+)\b', change)
                for part in parts:
                    component_freq[part] = component_freq.get(part, 0) + 1

        top_components = sorted(component_freq.items(), key=lambda x: x[1], reverse=True)[:6]

        bar_html = ""
        if top_components:
            max_val = max(v for _, v in top_components)
            for comp, count in top_components:
                width = int((count / max_val) * 100)
                bar_html += f"""
    <div class="bar-row">
      <div class="bar-label">{comp}</div>
      <div class="bar-track"><div class="bar-fill" style="width:{width}%"></div></div>
      <div class="bar-count">{count}</div>
    </div>"""
        else:
            bar_html = '<div class="empty-note">No component modifications recorded yet</div>'

        timeline_html = ""
        for entry in entries:
            timestamp = entry.get("timestamp", "Unknown")
            changes = entry.get("changes", [])
            has_changes = len(changes) > 0
            entry_class = "entry has-changes" if has_changes else "entry"
            tag_class = "entry-tag active" if has_changes else "entry-tag"
            tag_text = f"{len(changes)} change{'s' if len(changes) != 1 else ''}"

            change_rows = ""
            for change in changes:
                if "PCB:" in change:
                    pill = '<div class="pill pill-pcb">PCB</div>'
                elif "Schematic:" in change:
                    pill = '<div class="pill pill-sch">SCH</div>'
                elif "Added" in change:
                    pill = '<div class="pill pill-add">Added</div>'
                elif "Deleted" in change:
                    pill = '<div class="pill pill-del">Deleted</div>'
                else:
                    pill = '<div class="pill pill-mod">Modified</div>'
                change_rows += f"""
        <div class="change-row">
          {pill}
          <div class="change-desc">{change}</div>
        </div>"""

            timeline_html += f"""
    <div class="{entry_class}">
      <div class="entry-head">
        <div class="entry-ts">{timestamp}</div>
        <div class="{tag_class}">{tag_text}</div>
      </div>
      <div class="entry-body">{change_rows}
      </div>
    </div>"""

        generated = datetime.now().strftime("%B %d, %Y at %H:%M:%S")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>KiCad Design Diary</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #1a1410;
    --ink-2: #3d342a;
    --ink-3: #7a6e65;
    --ink-4: #b5aca4;
    --paper: #faf8f5;
    --paper-2: #f2ede8;
    --paper-3: #e8e0d8;
    --accent: #b85c2c;
    --green: #2d6a4f;
    --green-bg: #f0f7f4;
    --red: #9b2226;
    --red-bg: #fdf0f0;
    --blue: #1d4e89;
    --blue-bg: #f0f4fb;
    --purple: #5b2d8e;
    --purple-bg: #f5f0fb;
    --rule: #ddd5cc;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'DM Sans', sans-serif; background: var(--paper); color: var(--ink); min-height: 100vh; }}
  .page-rule {{ height: 4px; background: var(--ink); }}
  .masthead {{ padding: 48px 64px 40px; border-bottom: 1px solid var(--rule); display: grid; grid-template-columns: 1fr auto; align-items: end; gap: 24px; }}
  .masthead-title {{ font-family: 'DM Serif Display', serif; font-size: 36px; color: var(--ink); letter-spacing: -0.5px; line-height: 1; }}
  .masthead-title span {{ color: var(--accent); }}
  .masthead-sub {{ font-size: 12px; color: var(--ink-3); margin-top: 6px; font-weight: 300; }}
  .masthead-date {{ font-family: 'DM Mono', monospace; font-size: 11px; color: var(--ink-3); line-height: 1.8; text-align: right; }}
  .main {{ max-width: 860px; margin: 0 auto; padding: 48px 64px 80px; }}
  .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid var(--rule); border-radius: 2px; margin-bottom: 48px; overflow: hidden; }}
  .metric {{ padding: 28px 32px; border-right: 1px solid var(--rule); }}
  .metric:last-child {{ border-right: none; }}
  .metric-num {{ font-family: 'DM Serif Display', serif; font-size: 44px; color: var(--ink); line-height: 1; letter-spacing: -2px; }}
  .metric-num span {{ font-family: 'DM Sans', sans-serif; font-size: 13px; font-weight: 500; color: var(--accent); letter-spacing: 0; vertical-align: super; margin-left: 2px; }}
  .metric-label {{ font-size: 10px; font-weight: 500; color: var(--ink-3); text-transform: uppercase; letter-spacing: 1.2px; margin-top: 8px; }}
  .section-head {{ display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }}
  .section-label {{ font-size: 10px; font-weight: 500; color: var(--ink-3); text-transform: uppercase; letter-spacing: 1.5px; white-space: nowrap; }}
  .section-rule {{ flex: 1; height: 1px; background: var(--rule); }}
  .chart-block {{ margin-bottom: 48px; background: var(--paper-2); border: 1px solid var(--rule); border-radius: 2px; padding: 28px 32px; }}
  .bar-row {{ display: grid; grid-template-columns: 52px 1fr 28px; align-items: center; gap: 14px; margin-bottom: 12px; }}
  .bar-row:last-child {{ margin-bottom: 0; }}
  .bar-label {{ font-family: 'DM Mono', monospace; font-size: 12px; font-weight: 500; color: var(--ink-2); text-align: right; }}
  .bar-track {{ height: 6px; background: var(--paper-3); border-radius: 1px; overflow: hidden; }}
  .bar-fill {{ height: 100%; background: var(--accent); border-radius: 1px; }}
  .bar-count {{ font-family: 'DM Mono', monospace; font-size: 11px; color: var(--ink-4); }}
  .empty-note {{ font-size: 13px; color: var(--ink-4); font-style: italic; }}
  .entry {{ border: 1px solid var(--rule); border-radius: 2px; margin-bottom: 10px; background: #ffffff; overflow: hidden; }}
  .entry.has-changes {{ border-left: 3px solid var(--accent); }}
  .entry-head {{ padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; background: var(--paper-2); border-bottom: 1px solid var(--rule); }}
  .entry-ts {{ font-family: 'DM Mono', monospace; font-size: 11px; color: var(--ink-3); }}
  .entry-tag {{ font-size: 9px; font-weight: 500; letter-spacing: 0.8px; text-transform: uppercase; color: var(--ink-4); }}
  .entry-tag.active {{ color: var(--accent); }}
  .entry-body {{ padding: 14px 20px; }}
  .change-row {{ display: flex; align-items: baseline; gap: 12px; padding: 5px 0; border-bottom: 1px solid var(--paper-2); }}
  .change-row:last-child {{ border-bottom: none; }}
  .pill {{ font-size: 9px; font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase; padding: 2px 8px; border-radius: 2px; white-space: nowrap; flex-shrink: 0; }}
  .pill-add {{ background: var(--green-bg); color: var(--green); }}
  .pill-del {{ background: var(--red-bg); color: var(--red); }}
  .pill-mod {{ background: var(--blue-bg); color: var(--blue); }}
  .pill-pcb {{ background: var(--blue-bg); color: var(--blue); }}
  .pill-sch {{ background: var(--purple-bg); color: var(--purple); }}
  .change-desc {{ font-size: 13px; color: var(--ink-2); line-height: 1.5; font-weight: 300; }}
  .colophon {{ margin-top: 64px; padding-top: 20px; border-top: 1px solid var(--rule); font-size: 10px; color: var(--ink-4); display: flex; justify-content: space-between; font-family: 'DM Mono', monospace; }}
</style>
</head>
<body>
<div class="page-rule"></div>
<div class="masthead">
  <div>
    <div class="masthead-title">KiCad Design<span> Diary</span></div>
    <div class="masthead-sub">Automatic PCB & Schematic Change History Report</div>
  </div>
  <div>
    <div class="masthead-date">Generated: {generated}</div>
    <div class="masthead-date">Board: {board_name}</div>
  </div>
</div>
<div class="main">
  <div class="metrics">
    <div class="metric">
      <div class="metric-num">{total_sessions}<span>sessions</span></div>
      <div class="metric-label">Total Sessions</div>
    </div>
    <div class="metric">
      <div class="metric-num">{total_changes}<span>events</span></div>
      <div class="metric-label">Total Changes</div>
    </div>
    <div class="metric">
      <div class="metric-num">{len(component_freq)}<span>refs</span></div>
      <div class="metric-label">Components Tracked</div>
    </div>
  </div>
  <div class="section-head">
    <div class="section-label">Modification Frequency</div>
    <div class="section-rule"></div>
  </div>
  <div class="chart-block">{bar_html}
  </div>
  <div class="section-head">
    <div class="section-label">Change Timeline</div>
    <div class="section-rule"></div>
  </div>
  <div class="timeline">{timeline_html}
  </div>
  <div class="colophon">
    <span>KiCad Design Diary &mdash; PCB & Schematic Change Tracking</span>
    <span>v2.0.0</span>
  </div>
</div>
</body>
</html>"""

        with open(export_path, "w", encoding="utf-8") as f:
            f.write(html)

        wx.MessageBox("Report saved successfully.", "KiCad Design Diary", wx.OK | wx.ICON_INFORMATION)
