import tkinter as tk
from tkinter import messagebox

import GoatsandTigers as engine
from GoatsandTigers import ROTATION_ZONES

CANVAS_W = 640
CANVAS_H = 520
MARGIN   = 70
NODE_R   = 18

ZONE_HALO = {
    "4L":   "#ff9999",
    "4C":   "#ffcc66",
    "4R":   "#99ff99",
    "3TL":  "#66ccff",
    "3TLC": "#cc99ff",
    "3TRC": "#ff99cc",
    "3TR":  "#99ffcc",
    "3BL":  "#ffdd88",
    "3BLC": "#88ddff",
    "3BRC": "#bbff88",
    "3BR":  "#ff88bb",
}


class GameGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Goats and Tigers")
        self.root.resizable(False, False)
        self.selected_node = None
        self.rotation_zone = None
        self.rotation_mode = False
        self.game          = None
        self.engine        = None
        self.use_rotation  = False
        self._show_setup_screen()

    def _show_setup_screen(self):
        self.setup_frame = tk.Frame(self.root, bg="#2b2b2b", padx=50, pady=36)
        self.setup_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.setup_frame, text="🐯  Goats and Tigers  🐐",
                 font=("Helvetica", 20, "bold"),
                 fg="white", bg="#2b2b2b").pack(pady=(0, 6))

        tk.Label(self.setup_frame, text="Game Mode",
                 font=("Helvetica", 12, "bold"),
                 fg="#dddddd", bg="#2b2b2b").pack(anchor="w", pady=(8, 0))

        self.mode_var = tk.StringVar(value="normal")
        mf = tk.Frame(self.setup_frame, bg="#2b2b2b")
        mf.pack(fill=tk.X, pady=(4, 0))
        tk.Radiobutton(mf, text="Normal", variable=self.mode_var,
                       value="normal", bg="#2b2b2b", fg="white",
                       selectcolor="#555555", activebackground="#2b2b2b",
                       activeforeground="white",
                       font=("Helvetica", 11)).pack(side=tk.LEFT, padx=(0, 20))
        tk.Radiobutton(mf, text="Rotation Variation",
                       variable=self.mode_var, value="rotation",
                       bg="#2b2b2b", fg="#7ecfff",
                       selectcolor="#555555", activebackground="#2b2b2b",
                       activeforeground="#7ecfff",
                       font=("Helvetica", 11)).pack(side=tk.LEFT)

        tk.Label(self.setup_frame, text="Goat Player (goes first)",
                 font=("Helvetica", 12, "bold"),
                 fg="#5aab5a", bg="#2b2b2b").pack(anchor="w", pady=(16, 0))
        self.goat_var = tk.StringVar(value="Human")
        for opt in ["Human", "AI"]:
            tk.Radiobutton(self.setup_frame, text=opt,
                           variable=self.goat_var, value=opt,
                           bg="#2b2b2b", fg="white", selectcolor="#555555",
                           activebackground="#2b2b2b", activeforeground="white",
                           font=("Helvetica", 11)).pack(anchor="w", padx=20)

        tk.Label(self.setup_frame, text="Tiger Player",
                 font=("Helvetica", 12, "bold"),
                 fg="#e05252", bg="#2b2b2b").pack(anchor="w", pady=(14, 0))
        self.tiger_var = tk.StringVar(value="Human")
        for opt in ["Human", "AI"]:
            tk.Radiobutton(self.setup_frame, text=opt,
                           variable=self.tiger_var, value=opt,
                           bg="#2b2b2b", fg="white", selectcolor="#555555",
                           activebackground="#2b2b2b", activeforeground="white",
                           font=("Helvetica", 11)).pack(anchor="w", padx=20)

        tk.Button(self.setup_frame, text="Start Game",
                  font=("Helvetica", 13, "bold"),
                  bg="#5aab5a",
                  fg="black",
                  highlightbackground="#5aab5a",
                  activebackground="#3d8b3d",
                  activeforeground="black",
                  relief=tk.RAISED, bd=2,
                  padx=20, pady=10, cursor="hand2",
                  command=self._start_game).pack(pady=(26, 0))

    def _start_game(self):
        self.use_rotation = (self.mode_var.get() == "rotation")
        self.engine = engine
        depth = 3
        game_type = "rotation" if self.use_rotation else "original"
        self.game = engine.Game(game_type=game_type)
        PT = engine.PieceType

        def make(var, name, pt):
            if var.get() == "Human":
                return self.engine.HumanPlayer(name, pt)
            return self.engine.AIPlayer(f"{name} AI", pt, depth)

        self.game.players = [
            make(self.goat_var,  "Goat Player",  PT.GOAT),
            make(self.tiger_var, "Tiger Player", PT.TIGER),
        ]
        self.setup_frame.destroy()
        self._reset_interaction()
        self._build_ui()
        self._compute_pixel_positions()
        self.refresh()
        self._trigger_ai_if_needed()

    def _build_ui(self):
        top = tk.Frame(self.root, bg="#2b2b2b", pady=6)
        top.pack(fill=tk.X)
        self.turn_label = tk.Label(top, text="",
                                   font=("Helvetica", 13, "bold"),
                                   fg="white", bg="#2b2b2b")
        self.turn_label.pack(side=tk.LEFT, padx=16)
        if self.use_rotation:
            tk.Label(top, text="[Rotation Mode]",
                     font=("Helvetica", 10), fg="#7ecfff",
                     bg="#2b2b2b").pack(side=tk.LEFT)
        self.info_label = tk.Label(top, text="",
                                   font=("Helvetica", 11),
                                   fg="#aaaaaa", bg="#2b2b2b")
        self.info_label.pack(side=tk.RIGHT, padx=16)

        self.canvas = tk.Canvas(self.root,
                                width=CANVAS_W, height=CANVAS_H,
                                bg="#f5e6c8", highlightthickness=0)
        self.canvas.pack(padx=12, pady=(4, 0))
        self.canvas.bind("<Button-1>", self._on_click)

        self.hint_label = tk.Label(self.root, text="",
                                   font=("Helvetica", 10, "italic"),
                                   fg="#555555", bg="#f5e6c8", pady=4)
        self.hint_label.pack(fill=tk.X)

        if self.use_rotation:
            self._build_rotation_panel()

        bf = tk.Frame(self.root, bg="#f5e6c8")
        bf.pack(pady=(4, 8))
        for txt, cmd, bg in [
            ("New Game",    self._reset,       "#555555"),
            ("Change Mode", self._change_mode, "#3a6ea8"),
        ]:
            tk.Button(bf, text=txt, font=("Helvetica", 10),
                     command=cmd, relief=tk.RAISED, bd=2,
                     bg=bg,
                     fg="black",
                     highlightbackground=bg,
                     activebackground=bg,
                     activeforeground="black",
                      padx=12, pady=4,
                      cursor="hand2").pack(side=tk.LEFT, padx=4)

    def _build_rotation_panel(self):
        outer = tk.Frame(self.root, bg="#e8d8b0", pady=4)
        outer.pack(fill=tk.X, padx=12, pady=(2, 0))

        tk.Label(outer, text="Rotate zone:",
                 font=("Helvetica", 9, "bold"),
                 bg="#e8d8b0", fg="#333333").pack(anchor="w", padx=6)

        row4  = tk.Frame(outer, bg="#e8d8b0"); row4.pack(fill=tk.X, padx=4, pady=1)
        row3t = tk.Frame(outer, bg="#e8d8b0"); row3t.pack(fill=tk.X, padx=4, pady=1)
        row3b = tk.Frame(outer, bg="#e8d8b0"); row3b.pack(fill=tk.X, padx=4, pady=1)

        self._zone_btns = {}
        for key, info in ROTATION_ZONES.items():
            halo = ZONE_HALO.get(key, "#cccccc")
            parent = row4 if key.startswith("4") else (row3t if "T" in key else row3b)
            btn = tk.Button(
                parent, text=info["name"],
                font=("Helvetica", 8, "bold"),
                bg=halo,
                fg="black",
                highlightbackground=halo,
                relief=tk.RAISED, bd=2,
                padx=6, pady=2, cursor="hand2",
                command=lambda k=key: self._select_zone(k))
            btn.pack(side=tk.LEFT, padx=3)
            self._zone_btns[key] = btn

        dir_row = tk.Frame(outer, bg="#e8d8b0")
        dir_row.pack(fill=tk.X, padx=4, pady=(2, 4))
        self._dir_frame = dir_row

        def make_dir_btn(txt, cmd, bg):
            return tk.Button(dir_row, text=txt,
                             font=("Helvetica", 9, "bold"),
                             bg=bg,
                             fg="black",
                             highlightbackground=bg,
                             relief=tk.RAISED, bd=2,
                             padx=10, pady=3, cursor="hand2",
                             command=cmd)

        self._cw_btn     = make_dir_btn("↻  Clockwise",
                                         lambda: self._apply_rotation(True),  "#2e8b57")
        self._ccw_btn    = make_dir_btn("↺  Counter-Clockwise",
                                         lambda: self._apply_rotation(False), "#2e8b57")
        self._cancel_btn = make_dir_btn("✕  Cancel",
                                         self._cancel_rotation,               "#888888")
        self._hide_dir_buttons()

    def _compute_pixel_positions(self):
        pos  = self.game.board.positions
        xs   = [p[0] for p in pos.values()]
        ys   = [p[1] for p in pos.values()]
        mn_x, mx_x = min(xs), max(xs)
        mn_y, mx_y = min(ys), max(ys)
        uw = CANVAS_W - 2 * MARGIN
        uh = CANVAS_H - 2 * MARGIN
        self.pixel_pos = {}
        for nid, (gx, gy) in pos.items():
            px = MARGIN + (gx - mn_x) / (mx_x - mn_x) * uw
            py = CANVAS_H - MARGIN - (gy - mn_y) / (mx_y - mn_y) * uh
            self.pixel_pos[nid] = (px, py)

    def refresh(self):
        self.canvas.delete("all")
        if self.use_rotation and self.rotation_zone:
            self._draw_zone_highlight()
        self._draw_edges()
        self._draw_nodes()
        self._update_labels()
        if self.use_rotation:
            self._update_zone_btn_states()

    def _draw_zone_highlight(self):
        ring   = ROTATION_ZONES[self.rotation_zone]["perimeter"]
        colour = ZONE_HALO.get(self.rotation_zone, "#cccccc")
        r = NODE_R + 9
        for nid in ring:
            px, py = self.pixel_pos[nid]
            self.canvas.create_oval(px-r, py-r, px+r, py+r,
                                    fill=colour, outline="", stipple="gray50")

    def _draw_edges(self):
        for u, v in self.game.board.G.edges():
            x1, y1 = self.pixel_pos[u]
            x2, y2 = self.pixel_pos[v]
            self.canvas.create_line(x1, y1, x2, y2, fill="#888888", width=2)

    def _draw_nodes(self):
        for nid, (px, py) in self.pixel_pos.items():
            val = self.game.board.get_value(nid)
            if nid == self.selected_node:
                fill, outline, lw = "#ffdd44", "#cc9900", 3
            elif val == "T":
                fill, outline, lw = "#e05252", "#8b0000", 2
            elif val == "G":
                fill, outline, lw = "#5aab5a", "#1a6b1a", 2
            else:
                fill, outline, lw = "#d9c9a8", "#999999", 1
            self.canvas.create_oval(px-NODE_R, py-NODE_R,
                                    px+NODE_R, py+NODE_R,
                                    fill=fill, outline=outline, width=lw)
            self.canvas.create_text(px, py, text=str(nid),
                                    font=("Helvetica", 8),
                                    fill="white" if val in ("T","G") else "#444444")

    def _update_labels(self):
        player = self.game.get_current_player()
        piece  = player.piece_type
        PT     = self.engine.PieceType
        is_ai  = isinstance(player, self.engine.AIPlayer)
        self.turn_label.config(
            text=("🐯 Tiger" if piece == PT.TIGER else "🐐 Goat") +
                 ("  [AI thinking…]" if is_ai else "  [Your turn]"))
        self.info_label.config(
            text=f"To place: {self.game.goats_to_place}   "
                 f"Captured: {self.game.goats_captured}   "
                 f"Blocked: {self.game.tigers_blocked}")
        if is_ai:
            hint = "AI is thinking…"
        elif self.use_rotation and self.rotation_mode:
            hint = f"Zone {self.rotation_zone} — choose ↻ CW or ↺ CCW, or cancel."
        elif piece == PT.GOAT and self.game.goats_to_place > 0:
            hint = "Click an empty node to place a goat." + (
                "  Or pick a rotation zone below." if self.use_rotation else "")
        elif self.selected_node is None:
            hint = "Click your piece to select it." + (
                "  Or pick a rotation zone below." if self.use_rotation else "")
        else:
            hint = f"Node {self.selected_node} selected — click destination." + (
                "  Or pick a rotation zone below." if self.use_rotation else "")
        self.hint_label.config(text=hint, fg="#555555")

    def _update_zone_btn_states(self):
        player = self.game.get_current_player()
        is_ai  = isinstance(player, self.engine.AIPlayer)
        for key, btn in self._zone_btns.items():
            if is_ai or self.rotation_mode:
                btn.config(state=tk.DISABLED)
            elif key == self.game.last_rotated_zone:
                btn.config(state=tk.DISABLED)
            else:
                btn.config(state=tk.NORMAL)

    def _select_zone(self, key):
        if isinstance(self.game.get_current_player(), self.engine.AIPlayer):
            return
        self.rotation_zone = key
        self.rotation_mode = True
        self.selected_node = None
        self._show_dir_buttons()
        self.refresh()

    def _show_dir_buttons(self):
        self._cw_btn.pack(side=tk.LEFT, padx=3)
        self._ccw_btn.pack(side=tk.LEFT, padx=3)
        self._cancel_btn.pack(side=tk.LEFT, padx=8)

    def _hide_dir_buttons(self):
        self._cw_btn.pack_forget()
        self._ccw_btn.pack_forget()
        self._cancel_btn.pack_forget()

    def _cancel_rotation(self):
        self.rotation_zone = None
        self.rotation_mode = False
        self._hide_dir_buttons()
        self.refresh()

    def _apply_rotation(self, clockwise: bool):
        if not self.rotation_zone:
            return
        move = ("rotate", self.rotation_zone, clockwise)
        self.rotation_zone = None
        self.rotation_mode = False
        self._hide_dir_buttons()
        self._try_move(move)

    def _on_click(self, event):
        player = self.game.get_current_player()
        if isinstance(player, self.engine.AIPlayer):
            return
        if self.use_rotation and self.rotation_mode:
            return
        node = self._pixel_to_node(event.x, event.y)
        if node is None:
            return
        PT    = self.engine.PieceType
        piece = player.piece_type
        # Goat placement phase
        if piece == PT.GOAT and self.game.goats_to_place > 0:
            self._try_move(("place", node))
            return
        # Movement phase — select then destination
        if self.selected_node is None:
            if self.game.board.get_value(node) == piece.value:
                self.selected_node = node
                self.refresh()
            else:
                self._flash_hint("Select one of your own pieces first.")
        else:
            if node == self.selected_node:
                self.selected_node = None
                self.refresh()
            else:
                move = ("move", self.selected_node, node)
                self.selected_node = None
                self._try_move(move)

    def _try_move(self, move):
        player = self.game.get_current_player()
        if self.game.is_valid(move, player.piece_type):
            self.game.apply_move(move, player.piece_type)
            self.refresh()
            if self.game.is_game_over():
                self._check_game_over()
            else:
                self.game.switch_player()
                self.refresh()
                self._trigger_ai_if_needed()
        else:
            self._flash_hint("Invalid move — try again.")
            self.refresh()

    def _trigger_ai_if_needed(self):
        if isinstance(self.game.get_current_player(), self.engine.AIPlayer):
            self.canvas.unbind("<Button-1>")
            self.root.after(300, self._run_ai_move)

    def _run_ai_move(self):
        if self.game.is_game_over():
            return
        player = self.game.get_current_player()
        move = player.get_move(self.game, self.game.goats_to_place)
        if not move:
            return
        if self.use_rotation and move[0] == "rotate":
            self.rotation_zone = move[1]
            self.refresh()
            self.root.after(500, lambda: self._finish_ai_move(move, player))
        else:
            self._finish_ai_move(move, player)

    def _finish_ai_move(self, move, player):
        self.rotation_zone = None
        self.game.apply_move(move, player.piece_type)
        self.refresh()
        if self.game.is_game_over():
            self._check_game_over()
        else:
            self.game.switch_player()
            self.refresh()
            self.canvas.bind("<Button-1>", self._on_click)
            self._trigger_ai_if_needed()

    def _check_game_over(self):
        if self.game.goats_captured >= 5:
            msg = "🐯 Tigers win!\nThey captured 5 goats."
        elif self.game.is_draw():
            msg = "🤝 It's a draw!\nBoth players are stuck in a repeating cycle."
        else:
            msg = f"🐐 Goats win!\nAll {self.game.tigers_blocked} tigers are blocked."
        messagebox.showinfo("Game Over", msg)
        self._reset()

    def _pixel_to_node(self, px, py):
        for nid, (nx_, ny_) in self.pixel_pos.items():
            if (px-nx_)**2 + (py-ny_)**2 <= NODE_R**2:
                return nid
        return None

    def _flash_hint(self, msg: str):
        self.hint_label.config(text=f"⚠️  {msg}", fg="#cc3333")
        self.root.after(1800, lambda: self.hint_label.config(fg="#555555"))

    def _reset_interaction(self):
        self.selected_node = None
        self.rotation_zone = None
        self.rotation_mode = False

    def _reset(self):
        game_type = "rotation" if self.use_rotation else "original"
        self.game = engine.Game(game_type=game_type)
        self.game.players = [
            p.__class__(p.name, p.piece_type,
                        *([p.depth] if isinstance(p, self.engine.AIPlayer) else []))
            for p in self.game.players
        ]
        self._reset_interaction()
        if self.use_rotation:
            self._hide_dir_buttons()
        self.canvas.bind("<Button-1>", self._on_click)
        self.refresh()
        self._trigger_ai_if_needed()

    def _change_mode(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.game = None
        self.engine = None
        self._reset_interaction()
        self._show_setup_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app  = GameGUI(root)
    root.mainloop()