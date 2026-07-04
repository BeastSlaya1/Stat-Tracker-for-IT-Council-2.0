import flet as ft
from datetime import datetime
import os

class StatTrackerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Match Stat Tracker"
        self.page.padding = ft.Padding.all(20)
        self.page.scroll = ft.ScrollMode.AUTO

        # --- Data State ---
        self.TEAM_LISTS = []
        self.ALL_TEAM_STATS = {}
        self.Game = ""
        self.TrackerMode = "Attack"
        self.last_action_label = ""
        self.s = self.get_default_stats()

        # --- System Short-code Log Glossary (matches v1.0) ---
        # p should be the lowercase 'p' (pass). It was incorrectly set to 'I'.
        self.p = "p"; self.c = "c"; self.A = "A"; self.shot = "s"; self.G = "G"
        self.p0 = "!"; self.c0 = "!"; self.s0 = "!"; self.Con = "^"; self.H = "H"; self.inter = "!"
        self.dd = "d"; self.dfw = "F+"
        self.dt = "T"; self.di = "I"; self.db = "B"; self.df = "F-"; self.do = "O"; self.dc = "C"; self.dv = "V"
        self.yc = "Y"; self.rc = "R"

        # --- ipywidgets button_style color equivalents (v1.0 look) ---
        self.STYLE_INFO = ft.Colors.BLUE_400        # info
        self.STYLE_SUCCESS = ft.Colors.GREEN_400    # success
        self.STYLE_WARNING = ft.Colors.ORANGE_400   # warning
        self.STYLE_DANGER = ft.Colors.RED_400       # danger
        self.STYLE_PRIMARY = ft.Colors.BLUE_600     # primary

        # --- UI Element Handlers ---
        self.stats_text = ft.Text("No game selected.", font_family="Courier", size=14)
        self.log_text = ft.Text("", font_family="Courier", color=ft.Colors.GREY, size=13)
        self.team_btns_row = ft.Row(wrap=True, spacing=10)
        self.action_panel = ft.Column(spacing=10)
        self.status_text = ft.Text("", color=ft.Colors.GREEN_700, size=13)

        self.action_buttons = {}

        self.setup_ui()

    def get_default_stats(self):
        return {
            'Passes': 0, 'Crosses': 0, 'Shots': 0, 'Assists': 0, 'Conversions': 0, 'Goals': 0,
            'Dribbles': 0, 'FoulsWon': 0, 'Passes0': 0, 'Crosses0': 0, 'Shots0': 0,
            'Tackles': 0, 'Interceptions': 0, 'Blocks': 0, 'Fouls': 0, 'Offsides': 0,
            'Clears': 0, 'Saves': 0, 'Tackles0': 0, 'Interceptions0': 0, 'Blocks0': 0, 'Saves0': 0,
            'YellowCard': 0, 'RedCard': 0,
            'Half': 0, 'Listofinputs': '', 'AttackSequence': '', 'DefenceSequence': '', 'CardsSequence': '',
            'TrackerMode': 'Attack'
        }

    # ------------------------------------------------------------------
    # UI SETUP
    # ------------------------------------------------------------------

    def setup_ui(self):
        self.new_team_input = ft.TextField(label="New Game:", width=320, hint_text="e.g. Team A vs Team B")
        add_btn = ft.Button(content="Add Game", on_click=self.on_add_new_team, bgcolor=self.STYLE_SUCCESS, color=ft.Colors.WHITE)

        self.import_path_input = ft.TextField(label="Import from file:", width=320, hint_text="Full path to a _full_report.txt file")
        import_btn = ft.Button(content="Import Team", on_click=self.on_import_clicked, bgcolor=self.STYLE_PRIMARY, color=ft.Colors.WHITE)

        self.mode_radio = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="Attack", label="Attack"),
                ft.Radio(value="Defence", label="Defence"),
                ft.Radio(value="Cards", label="Cards")
            ], spacing=20),
            value="Attack",
            on_change=self.on_mode_change,
            disabled=True
        )

        self.page.add(
            ft.SafeArea(
                content=ft.Column([
                    ft.Text("--- SET UP ---", weight=ft.FontWeight.BOLD, size=14),
                    ft.Row([self.new_team_input, add_btn], spacing=10),
                    ft.Row([self.import_path_input, import_btn], spacing=10),
                    ft.Text("--- SELECT MATCH ---", weight=ft.FontWeight.BOLD, size=14),
                    self.team_btns_row,
                    ft.Row([ft.Text("Mode:", size=14), self.mode_radio], spacing=10),
                    ft.Divider(thickness=1),
                    self.stats_text,
                    ft.Divider(thickness=1),
                    ft.Text("--- ACTION PANEL ---", weight=ft.FontWeight.BOLD, size=14),
                    self.action_panel,
                    ft.Divider(thickness=1),
                    self.log_text,
                    self.status_text,
                ], spacing=8)
            )
        )
        self.update_ui()

    def create_action_button(self, label, bg_color, action_key, disabled=False):
        btn = ft.Button(
            content=label,
            bgcolor=bg_color,
            color=ft.Colors.WHITE,
            disabled=disabled,
            on_click=lambda _, a=action_key: self.on_action(a)
        )
        self.action_buttons[action_key] = btn
        return btn

    def build_action_rows(self):
        """Builds rows of buttons exactly mirroring v1.0's HBox groupings per mode."""
        self.action_buttons.clear()
        rows = []

        if self.TrackerMode == "Attack":
            row1 = [
                self.create_action_button("Pass (p)", self.STYLE_INFO, "pass"),
                self.create_action_button("Cross (c)", self.STYLE_INFO, "cross"),
                self.create_action_button("Shot (s)", self.STYLE_INFO, "shot"),
                self.create_action_button("Dribble (d)", self.STYLE_INFO, "dribble"),
                self.create_action_button("Foul Won (F+)", self.STYLE_INFO, "foulwon"),
            ]
            row2 = [
                self.create_action_button("Pass!", self.STYLE_WARNING, "pass0", disabled=True),
                self.create_action_button("Cross!", self.STYLE_WARNING, "cross0", disabled=True),
                self.create_action_button("Shot!", self.STYLE_WARNING, "shot0", disabled=True),
            ]
            row3 = [
                self.create_action_button("Goal (G)", self.STYLE_SUCCESS, "goal"),
                self.create_action_button("Assist (A)", self.STYLE_SUCCESS, "assist"),
                self.create_action_button("Conversion (^)", self.STYLE_SUCCESS, "conversion", disabled=True),
            ]
            row4 = [self.create_action_button("Half-time", self.STYLE_PRIMARY, "halftime")]
            row5 = [self.create_action_button("Export to Text", self.STYLE_PRIMARY, "export")]
            row6 = [self.create_action_button("Undo Last Action", self.STYLE_DANGER, "undo")]
            rows = [row1, row2, row3, row4, row5, row6]

        elif self.TrackerMode == "Defence":
            row1 = [
                self.create_action_button("Tackle (T)", self.STYLE_INFO, "tackle"),
                self.create_action_button("Interception (I)", self.STYLE_INFO, "interception"),
                self.create_action_button("Block (B)", self.STYLE_INFO, "block"),
                self.create_action_button("Save (V)", self.STYLE_INFO, "save"),
            ]
            row2 = [
                self.create_action_button("Tackle!", self.STYLE_WARNING, "tackle0", disabled=True),
                self.create_action_button("Interception!", self.STYLE_WARNING, "interception0", disabled=True),
                self.create_action_button("Block!", self.STYLE_WARNING, "block0", disabled=True),
                self.create_action_button("Save!", self.STYLE_WARNING, "save0", disabled=True),
            ]
            row3 = [
                self.create_action_button("Foul Given (F-)", self.STYLE_WARNING, "foulgiven"),
                self.create_action_button("Offside (O)", self.STYLE_WARNING, "offside"),
                self.create_action_button("Clear (C)", self.STYLE_SUCCESS, "clear"),
            ]
            row4 = [self.create_action_button("Half-time", self.STYLE_PRIMARY, "halftime")]
            row5 = [self.create_action_button("Export to Text", self.STYLE_PRIMARY, "export")]
            row6 = [self.create_action_button("Undo Last Action", self.STYLE_DANGER, "undo")]
            rows = [row1, row2, row3, row4, row5, row6]

        elif self.TrackerMode == "Cards":
            row1 = [
                self.create_action_button("Yellow Card (Y)", self.STYLE_WARNING, "yellow"),
                self.create_action_button("Red Card (R)", self.STYLE_DANGER, "red"),
            ]
            row2 = [self.create_action_button("Half-time", self.STYLE_PRIMARY, "halftime")]
            row3 = [self.create_action_button("Export to Text", self.STYLE_PRIMARY, "export")]
            row4 = [self.create_action_button("Undo Last Action", self.STYLE_DANGER, "undo")]
            rows = [row1, row2, row3, row4]

        return rows

    def update_action_buttons(self):
        self.action_panel.controls.clear()

        if not self.Game:
            self.action_panel.controls.append(ft.Text("Add or select a match above.", color=ft.Colors.GREY))
            return

        for row in self.build_action_rows():
            self.action_panel.controls.append(ft.Row(row, wrap=True, spacing=8, run_spacing=8))

        self.refresh_incomplete_button_states()

    def reset_incomplete_buttons(self):
        """Disables all incomplete-toggle and Conversion buttons (matches v1.0's reset_incomplete_buttons)."""
        for key in ['pass0', 'cross0', 'shot0', 'tackle0', 'interception0', 'block0', 'save0', 'conversion']:
            if key in self.action_buttons:
                self.action_buttons[key].disabled = True

    def refresh_incomplete_button_states(self):
        """Re-applies disabled=True to all incomplete/Conversion buttons whenever the panel is rebuilt
        (mirrors v1.0 always starting fresh after a mode switch / game load)."""
        self.reset_incomplete_buttons()

    # ------------------------------------------------------------------
    # GAME / MODE MANAGEMENT
    # ------------------------------------------------------------------

    def on_add_new_team(self, e):
        import re
        game_name = self.new_team_input.value.strip()
        if not re.search(r".+\s+vs\s+.+", game_name, re.IGNORECASE):
            self.status_text.value = "[Error] Invalid format! Please use: 'Team Name vs Team Name'"
            self.status_text.color = ft.Colors.RED_700
            self.page.update()
            return

        if game_name and game_name not in self.ALL_TEAM_STATS:
            self.TEAM_LISTS.append(game_name)
            self.ALL_TEAM_STATS[game_name] = self.get_default_stats()
            self.team_btns_row.controls.append(
                ft.Button(
                    content=game_name,
                    bgcolor=self.STYLE_PRIMARY,
                    color=ft.Colors.WHITE,
                    on_click=lambda _, g=game_name: self.load_game(g)
                )
            )

        self.new_team_input.value = ""
        self.status_text.value = ""
        self.load_game(game_name)

    def load_game(self, game_name):
        self.save_current_game_stats()
        self.Game = game_name
        self.s = self.ALL_TEAM_STATS[game_name]
        self.TrackerMode = self.s['TrackerMode']
        self.mode_radio.value = self.TrackerMode
        self.mode_radio.disabled = False
        self.last_action_label = ""
        self.update_action_buttons()
        self.update_ui()

    def save_current_game_stats(self):
        if self.Game and self.Game in self.ALL_TEAM_STATS:
            self.s['TrackerMode'] = self.TrackerMode
            self.ALL_TEAM_STATS[self.Game] = self.s

    def on_mode_change(self, e):
        if not self.Game:
            return
        self.TrackerMode = e.control.value
        self.last_action_label = ""
        self.update_action_buttons()
        self.update_ui()

    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------

    def process_char(self, char):
        s = self.s
        s['Listofinputs'] += char
        if self.TrackerMode == "Attack":
            s['AttackSequence'] += char
        elif self.TrackerMode == "Defence":
            s['DefenceSequence'] += char
        else:
            s['CardsSequence'] += char

    def on_action(self, action_key):
        if not self.Game:
            return
        if action_key == "export":
            self.on_export_clicked()
            return
        if action_key == "undo":
            self.on_undo()
            return

        s = self.s
        char_to_add = ""

        # --- Attack actions ---
        if action_key == "pass":
            char_to_add = self.p; s['Passes'] += 1
            self.reset_incomplete_buttons()
            self._enable('pass0'); self._enable('conversion')
        elif action_key == "cross":
            char_to_add = self.c; s['Crosses'] += 1
            self.reset_incomplete_buttons()
            self._enable('cross0'); self._enable('conversion')
        elif action_key == "shot":
            char_to_add = self.shot; s['Shots'] += 1
            self.reset_incomplete_buttons()
            self._enable('shot0'); self._enable('conversion')
        elif action_key == "dribble":
            char_to_add = self.dd; s['Dribbles'] += 1
            self.reset_incomplete_buttons()
        elif action_key == "foulwon":
            char_to_add = self.dfw; s['FoulsWon'] += 1
            self.reset_incomplete_buttons()
        elif action_key == "pass0":
            char_to_add = self.inter; s['Passes0'] += 1; s['Passes'] -= 1
            self.reset_incomplete_buttons()
        elif action_key == "cross0":
            char_to_add = self.inter; s['Crosses0'] += 1; s['Crosses'] -= 1
            self.reset_incomplete_buttons()
        elif action_key == "shot0":
            char_to_add = self.inter; s['Shots0'] += 1; s['Shots'] -= 1
            self.reset_incomplete_buttons()
        elif action_key == "goal":
            char_to_add = self.G; s['Goals'] += 1
            self.reset_incomplete_buttons()
        elif action_key == "assist":
            char_to_add = self.A; s['Assists'] += 1
            self.reset_incomplete_buttons()
        elif action_key == "conversion":
            self.process_char(self.Con); s['Conversions'] += 1
            self.process_char(self.A); s['Assists'] += 1
            self.process_char(self.G); s['Goals'] += 1
            char_to_add = ""
            self.reset_incomplete_buttons()

        # --- Defence actions ---
        elif action_key == "tackle":
            char_to_add = self.dt; s['Tackles'] += 1
            self.reset_incomplete_buttons(); self._enable('tackle0')
        elif action_key == "interception":
            char_to_add = self.di; s['Interceptions'] += 1
            self.reset_incomplete_buttons(); self._enable('interception0')
        elif action_key == "block":
            char_to_add = self.db; s['Blocks'] += 1
            self.reset_incomplete_buttons(); self._enable('block0')
        elif action_key == "save":
            char_to_add = self.dv; s['Saves'] += 1
            self.reset_incomplete_buttons(); self._enable('save0')
        elif action_key == "tackle0":
            char_to_add = self.inter; s['Tackles0'] += 1; s['Tackles'] -= 1
            self.reset_incomplete_buttons()
        elif action_key == "interception0":
            char_to_add = self.inter; s['Interceptions0'] += 1; s['Interceptions'] -= 1
            self.reset_incomplete_buttons()
        elif action_key == "block0":
            char_to_add = self.inter; s['Blocks0'] += 1; s['Blocks'] -= 1
            self.reset_incomplete_buttons()
        elif action_key == "save0":
            char_to_add = self.inter; s['Saves0'] += 1; s['Saves'] -= 1
            self.reset_incomplete_buttons()
        elif action_key == "foulgiven":
            char_to_add = self.df; s['Fouls'] += 1
            self.reset_incomplete_buttons()
        elif action_key == "offside":
            char_to_add = self.do; s['Offsides'] += 1
            self.reset_incomplete_buttons()
        elif action_key == "clear":
            char_to_add = self.dc; s['Clears'] += 1
            self.reset_incomplete_buttons()

        # --- Cards actions ---
        elif action_key == "yellow":
            char_to_add = self.yc; s['YellowCard'] += 1
            self.reset_incomplete_buttons()
        elif action_key == "red":
            char_to_add = self.rc; s['RedCard'] += 1
            self.reset_incomplete_buttons()

        # --- Shared ---
        elif action_key == "halftime":
            char_to_add = self.H; s['Half'] += 1
            self.reset_incomplete_buttons()

        if char_to_add:
            self.process_char(char_to_add)

        self.last_action_label = action_key
        self.save_current_game_stats()
        self.update_ui()

    def _enable(self, key):
        if key in self.action_buttons:
            self.action_buttons[key].disabled = False

    def on_undo(self):
        s = self.s
        if not s['Listofinputs']:
            return

        last = s['Listofinputs'][-1]
        s['Listofinputs'] = s['Listofinputs'][:-1]

        if self.TrackerMode == "Attack" and s['AttackSequence'] and s['AttackSequence'][-1] == last:
            s['AttackSequence'] = s['AttackSequence'][:-1]
        elif self.TrackerMode == "Defence" and s['DefenceSequence'] and s['DefenceSequence'][-1] == last:
            s['DefenceSequence'] = s['DefenceSequence'][:-1]
        elif self.TrackerMode == "Cards" and s['CardsSequence'] and s['CardsSequence'][-1] == last:
            s['CardsSequence'] = s['CardsSequence'][:-1]

        if last == self.p:
            s['Passes'] -= 1
        elif last == self.c:
            s['Crosses'] -= 1
        elif last == self.shot:
            s['Shots'] -= 1
        elif last == self.dd:
            s['Dribbles'] -= 1
        elif last == self.dfw:
            s['FoulsWon'] -= 1
        elif last == self.G:
            s['Goals'] -= 1
        elif last == self.A:
            s['Assists'] -= 1
        elif last == self.Con:
            s['Conversions'] -= 1
        elif last == self.dt:
            s['Tackles'] -= 1
        elif last == self.di:
            s['Interceptions'] -= 1
        elif last == self.db:
            s['Blocks'] -= 1
        elif last == self.dv:
            s['Saves'] -= 1
        elif last == self.df:
            s['Fouls'] -= 1
        elif last == self.do:
            s['Offsides'] -= 1
        elif last == self.dc:
            s['Clears'] -= 1
        elif last == self.yc:
            s['YellowCard'] -= 1
        elif last == self.rc:
            s['RedCard'] -= 1
        elif last == self.inter:
            if self.last_action_label == 'pass0':
                s['Passes0'] -= 1; s['Passes'] += 1; self._enable('pass0')
            elif self.last_action_label == 'cross0':
                s['Crosses0'] -= 1; s['Crosses'] += 1; self._enable('cross0')
            elif self.last_action_label == 'shot0':
                s['Shots0'] -= 1; s['Shots'] += 1; self._enable('shot0')
            elif self.last_action_label == 'tackle0':
                s['Tackles0'] -= 1; s['Tackles'] += 1; self._enable('tackle0')
            elif self.last_action_label == 'interception0':
                s['Interceptions0'] -= 1; s['Interceptions'] += 1; self._enable('interception0')
            elif self.last_action_label == 'block0':
                s['Blocks0'] -= 1; s['Blocks'] += 1; self._enable('block0')
            elif self.last_action_label == 'save0':
                s['Saves0'] -= 1; s['Saves'] += 1; self._enable('save0')
        elif last == self.H:
            s['Half'] -= 1

        self.save_current_game_stats()
        self.update_ui()

    # ------------------------------------------------------------------
    # IMPORT
    # ------------------------------------------------------------------

    def parse_report_text(self, text):
        """Parses the plain-text report format produced by on_export_clicked
        back into a stats dict. Returns (game_name, stats_dict) or raises ValueError."""
        import re

        header_match = re.search(r"=== FULL GAME REPORT:\s*(.+?)\s*===", text)
        if not header_match:
            raise ValueError("Could not find a game report header in this file.")
        game_name = header_match.group(1).strip()

        def grab_int(label, default=0):
            m = re.search(rf"^{re.escape(label)}:\s*(-?\d+)\s*$", text, re.MULTILINE)
            return int(m.group(1)) if m else default

        def grab_line(label, default=""):
            m = re.search(rf"^{re.escape(label)}:\s*(.*)$", text, re.MULTILINE)
            return m.group(1).strip() if m else default

        def grab_slash_ints(label, count, defaults=None):
            m = re.search(rf"^{re.escape(label)}:\s*([\d/\-]+)\s*$", text, re.MULTILINE)
            if not m:
                return defaults if defaults else [0] * count
            parts = m.group(1).split("/")
            try:
                return [int(p) for p in parts]
            except ValueError:
                return defaults if defaults else [0] * count

        stats = self.get_default_stats()

        stats['Half'] = grab_int("Final Half-time Count", stats['Half'])

        stats['Passes'] = grab_int("Passes", stats['Passes'])
        stats['Crosses'] = grab_int("Crosses", stats['Crosses'])
        stats['Shots'] = grab_int("Shots", stats['Shots'])
        stats['Goals'] = grab_int("Goals", stats['Goals'])
        stats['Assists'] = grab_int("Assists", stats['Assists'])
        stats['Conversions'] = grab_int("Conversions", stats['Conversions'])
        stats['Dribbles'] = grab_int("Dribbles", stats['Dribbles'])
        stats['FoulsWon'] = grab_int("Fouls Won", stats['FoulsWon'])
        p0, c0, s0 = grab_slash_ints("Incomplete (P!/C!/S!)", 3, [stats['Passes0'], stats['Crosses0'], stats['Shots0']])
        stats['Passes0'], stats['Crosses0'], stats['Shots0'] = p0, c0, s0
        stats['AttackSequence'] = grab_line("Attack Sequence", stats['AttackSequence'])

        stats['Tackles'] = grab_int("Tackles", stats['Tackles'])
        stats['Interceptions'] = grab_int("Interceptions", stats['Interceptions'])
        stats['Blocks'] = grab_int("Blocks", stats['Blocks'])
        stats['Saves'] = grab_int("Saves", stats['Saves'])
        stats['Fouls'] = grab_int("Fouls Given", stats['Fouls'])
        stats['Offsides'] = grab_int("Offsides", stats['Offsides'])
        stats['Clears'] = grab_int("Clears", stats['Clears'])
        t0, i0, b0, v0 = grab_slash_ints(
            "Incomplete (T!/I!/B!/V!)", 4,
            [stats['Tackles0'], stats['Interceptions0'], stats['Blocks0'], stats['Saves0']]
        )
        stats['Tackles0'], stats['Interceptions0'], stats['Blocks0'], stats['Saves0'] = t0, i0, b0, v0
        stats['DefenceSequence'] = grab_line("Defence Sequence", stats['DefenceSequence'])

        stats['YellowCard'] = grab_int("Yellow Cards", stats['YellowCard'])
        stats['RedCard'] = grab_int("Red Cards", stats['RedCard'])
        stats['CardsSequence'] = grab_line("Cards Sequence", stats['CardsSequence'])

        stats['Listofinputs'] = stats['AttackSequence'] + stats['DefenceSequence'] + stats['CardsSequence']
        stats['TrackerMode'] = 'Attack'

        return game_name, stats

    def on_import_clicked(self, e):
        path = self.import_path_input.value.strip() if self.import_path_input.value else ""
        if not path:
            self.status_text.value = "[Error] Enter the full path to a report .txt file to import."
            self.status_text.color = ft.Colors.RED_700
            self.page.update()
            return

        if not os.path.isfile(path):
            self.status_text.value = f"[Error] File not found: {path}"
            self.status_text.color = ft.Colors.RED_700
            self.page.update()
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            game_name, stats = self.parse_report_text(text)
        except Exception as ex:
            self.status_text.value = f"[Error] Import failed: {ex}"
            self.status_text.color = ft.Colors.RED_700
            self.page.update()
            return

        is_new = game_name not in self.ALL_TEAM_STATS
        self.ALL_TEAM_STATS[game_name] = stats
        if game_name not in self.TEAM_LISTS:
            self.TEAM_LISTS.append(game_name)
            self.team_btns_row.controls.append(
                ft.Button(
                    content=game_name,
                    bgcolor=self.STYLE_PRIMARY,
                    color=ft.Colors.WHITE,
                    on_click=lambda _, g=game_name: self.load_game(g)
                )
            )

        self.import_path_input.value = ""
        self.status_text.value = f"[Success] Imported '{game_name}'{' (new game)' if is_new else ' (overwritten)'}"
        self.status_text.color = ft.Colors.GREEN_700
        self.load_game(game_name)

    # ------------------------------------------------------------------
    # EXPORT
    # ------------------------------------------------------------------

    def get_writable_dir(self):
        """Finds a directory the app is actually allowed to write to.
        Tries several common candidates in order and returns the first one
        that accepts a real write (cwd is often read-only on Android/sandboxed apps)."""
        candidates = []

        # App-specific storage env vars some platforms/launchers set
        for env_var in ("FLET_APP_STORAGE_DATA", "FLET_APP_STORAGE_TEMP", "XDG_DATA_HOME"):
            val = os.environ.get(env_var)
            if val:
                candidates.append(val)

        candidates.append(os.path.expanduser("~"))   # home directory
        candidates.append(os.getcwd())                # current working dir
        import tempfile
        candidates.append(tempfile.gettempdir())       # always-writable temp dir as last resort

        for directory in candidates:
            try:
                os.makedirs(directory, exist_ok=True)
                test_path = os.path.join(directory, ".write_test_tmp")
                with open(test_path, "w") as f:
                    f.write("")
                os.remove(test_path)
                return directory
            except Exception:
                continue

        return None

    def on_export_clicked(self):
        if not self.Game:
            self.status_text.value = "[Error] No game selected to export."
            self.status_text.color = ft.Colors.RED_700
            self.page.update()
            return

        s = self.s
        content = []
        content.append(f"=== FULL GAME REPORT: {self.Game} ===")
        content.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"Final Half-time Count: {s['Half']}")
        content.append("=" * 30)
        content.append("\n--- ATTACK STATISTICS ---")
        content.append(f"Passes: {s['Passes']}")
        content.append(f"Crosses: {s['Crosses']}")
        content.append(f"Shots: {s['Shots']}")
        content.append(f"Goals: {s['Goals']}")
        content.append(f"Assists: {s['Assists']}")
        content.append(f"Conversions: {s['Conversions']}")
        content.append(f"Dribbles: {s['Dribbles']}")
        content.append(f"Fouls Won: {s['FoulsWon']}")
        content.append(f"Incomplete (P!/C!/S!): {s['Passes0']}/{s['Crosses0']}/{s['Shots0']}")
        content.append(f"Attack Sequence: {s['AttackSequence']}")
        content.append("\n--- DEFENCE STATISTICS ---")
        content.append(f"Tackles: {s['Tackles']}")
        content.append(f"Interceptions: {s['Interceptions']}")
        content.append(f"Blocks: {s['Blocks']}")
        content.append(f"Saves: {s['Saves']}")
        content.append(f"Fouls Given: {s['Fouls']}")
        content.append(f"Offsides: {s['Offsides']}")
        content.append(f"Clears: {s['Clears']}")
        content.append(f"Incomplete (T!/I!/B!/V!): {s['Tackles0']}/{s['Interceptions0']}/{s['Blocks0']}/{s['Saves0']}")
        content.append(f"Defence Sequence: {s['DefenceSequence']}")
        content.append("\n--- CARDS ---")
        content.append(f"Yellow Cards: {s['YellowCard']}")
        content.append(f"Red Cards: {s['RedCard']}")
        content.append(f"Cards Sequence: {s['CardsSequence']}")

        report_text = "\n".join(content)
        filename = f"{self.Game.replace(' ', '_')}_full_report.txt"

        writable_dir = self.get_writable_dir()
        if writable_dir is None:
            self.status_text.value = "[Error] No writable location found on this device."
            self.status_text.color = ft.Colors.RED_700
            self.page.update()
            return

        full_path = os.path.join(writable_dir, filename)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            self.status_text.value = f"[Success] Report exported to {full_path}"
            self.status_text.color = ft.Colors.GREEN_700
        except Exception as ex:
            self.status_text.value = f"[Error] Export failed: {ex}"
            self.status_text.color = ft.Colors.RED_700

        self.page.update()

    # ------------------------------------------------------------------
    # DISPLAY
    # ------------------------------------------------------------------

    def build_stats_display(self):
        if not self.Game:
            return "No game selected."

        s = self.s
        lines = [f"=== STATISTICS: {self.Game} ({self.TrackerMode}) ==="]

        if self.TrackerMode == "Attack":
            lines.append(f"Passes: {s['Passes']} | Crosses: {s['Crosses']} | Shots: {s['Shots']}")
            lines.append(f"Assists: {s['Assists']} | Goals: {s['Goals']} | Conversions: {s['Conversions']}")
            lines.append(f"Dribbles: {s['Dribbles']} | Fouls Won: {s['FoulsWon']}")
            lines.append(f"Incomplete (P!/C!/S!): {s['Passes0']}/{s['Crosses0']}/{s['Shots0']}")
        elif self.TrackerMode == "Defence":
            lines.append(f"Tackles: {s['Tackles']} | Interceptions: {s['Interceptions']} | Blocks: {s['Blocks']} | Saves: {s['Saves']}")
            lines.append(f"Fouls Given: {s['Fouls']} | Offsides: {s['Offsides']} | Clears: {s['Clears']}")
            lines.append(f"Incomplete (T!/I!/B!/V!): {s['Tackles0']}/{s['Interceptions0']}/{s['Blocks0']}/{s['Saves0']}")
        elif self.TrackerMode == "Cards":
            lines.append(f"Yellow Cards: {s['YellowCard']} | Red Cards: {s['RedCard']}")

        lines.append(f"Half-time: {s['Half']}")
        return "\n".join(lines)

    def build_log_display(self):
        if not self.Game:
            return ""
        s = self.s
        return (
            f"=== EVENT SEQUENCES ===\n"
            f"Attack Mode Log:  {s['AttackSequence']}\n"
            f"Defence Mode Log: {s['DefenceSequence']}\n"
            f"Cards Mode Log:   {s['CardsSequence']}"
        )

    def update_ui(self):
        self.stats_text.value = self.build_stats_display()
        self.log_text.value = self.build_log_display()
        self.page.update()


def main(page: ft.Page):
    StatTrackerApp(page)

if __name__ == "__main__":
    ft.run(main)
