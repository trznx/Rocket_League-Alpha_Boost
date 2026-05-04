"""
Alpha Boost Engine — Modern Interface
A professional, dark-mode GUI built with customtkinter.
"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import sys
import threading


# ─── THEME & COLOR PALETTE ────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

COLORS = {
    "bg_primary":      "#0D0F14",
    "bg_secondary":    "#121620",
    "bg_card":         "#13161E",
    "bg_card_hover":   "#181C26",
    "border":          "#222734",
    "border_accent":   "#3A4560",
    "text_primary":    "#E8ECF4",
    "text_secondary":  "#8892A6",
    "text_muted":      "#5A6478",
    "accent_blue":     "#4E8CFF",
    "accent_blue_dim": "#3A6BD4",
    "accent_cyan":     "#00D4AA",
    "accent_purple":   "#8B5CF6",
    "accent_orange":   "#F59E0B",
    "enabled_green":   "#22C55E",
    "enabled_bg":      "#132A1C",
    "disabled_red":    "#EF4444",
    "disabled_bg":     "#2A1318",
    "warning_yellow":  "#FBBF24",
    "slider_track":    "#222734",
    "divider":         "#1A1E28",
}


# ─── ICON HELPER ──────────────────────────────────────────────────────────────

def _get_base_path():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def load_icon(name, size=(18, 18)):
    base = _get_base_path()
    path = os.path.join(base, "interface_icons", name)
    if os.path.exists(path):
        try:
            img = Image.open(path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception:
            pass
    return None


# ─── CUSTOM WIDGETS ───────────────────────────────────────────────────────────

class StatusBadge(ctk.CTkFrame):
    def __init__(self, master, enabled=True, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(corner_radius=5, height=22,
                       fg_color=COLORS["enabled_bg"] if enabled else COLORS["disabled_bg"])
        self._label = ctk.CTkLabel(
            self, text="ENABLED" if enabled else "DISABLED",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLORS["enabled_green"] if enabled else COLORS["disabled_red"],
            height=22)
        self._label.pack(padx=8, pady=0)

    def set_state(self, enabled: bool):
        self.configure(fg_color=COLORS["enabled_bg"] if enabled else COLORS["disabled_bg"])
        self._label.configure(
            text="ENABLED" if enabled else "DISABLED",
            text_color=COLORS["enabled_green"] if enabled else COLORS["disabled_red"])


class ToggleRow(ctk.CTkFrame):
    def __init__(self, master, label_text, shortcut_text="", initial=True,
                 icon_name=None, command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._enabled = initial
        self._command = command

        icon = load_icon(icon_name, size=(16, 16)) if icon_name else None

        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)
        if icon:
            ctk.CTkLabel(left, text="", image=icon, width=16).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(left, text=label_text,
                     font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(side="left")
        if shortcut_text:
            ctk.CTkLabel(left, text=shortcut_text,
                         font=ctk.CTkFont(family="Segoe UI", size=10),
                         text_color=COLORS["text_muted"], anchor="w").pack(side="left", padx=(5, 0))

        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right")
        self._badge = StatusBadge(right, enabled=initial)
        self._badge.pack(side="left", padx=(0, 8))
        self._switch = ctk.CTkSwitch(
            right, text="", width=40, height=20, switch_width=36, switch_height=18,
            fg_color=COLORS["slider_track"], progress_color=COLORS["enabled_green"],
            button_color=COLORS["text_primary"], button_hover_color="#FFFFFF",
            command=self._on_toggle)
        if initial:
            self._switch.select()
        else:
            self._switch.deselect()
        self._switch.pack(side="left")

    def _on_toggle(self):
        self._enabled = self._switch.get() == 1
        self._badge.set_state(self._enabled)
        if self._command:
            self._command()

    @property
    def enabled(self):
        return self._enabled

    def set_state(self, enabled: bool):
        self._enabled = enabled
        if enabled:
            self._switch.select()
        else:
            self._switch.deselect()
        self._badge.set_state(enabled)


class SectionHeader(ctk.CTkFrame):
    def __init__(self, master, title, icon_name=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        icon = load_icon(icon_name, size=(14, 14)) if icon_name else None
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(0, 6))
        if icon:
            ctk.CTkLabel(row, text="", image=icon, width=14).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(row, text=title.upper(),
                     font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(side="left")
        ctk.CTkFrame(row, height=1, fg_color=COLORS["border"], corner_radius=0
                     ).pack(side="left", fill="x", expand=True, padx=(10, 0), pady=1)


class Card(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_card"])
        kwargs.setdefault("corner_radius", 10)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", COLORS["border"])
        super().__init__(master, **kwargs)


class SliderWithLabel(ctk.CTkFrame):
    def __init__(self, master, label, from_, to, value, unit="%",
                 icon_name=None, command=None, value_format=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._command = command
        self._unit = unit
        self._value_format = value_format or (lambda v: f"{int(v)}")

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 4))
        icon = load_icon(icon_name, size=(14, 14)) if icon_name else None
        if icon:
            ctk.CTkLabel(header, text="", image=icon, width=14).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(header, text=label,
                     font=ctk.CTkFont(family="Segoe UI", size=11),
                     text_color=COLORS["text_primary"], anchor="w").pack(side="left")
        self._value_label = ctk.CTkLabel(
            header, text=f"{self._value_format(value)}{unit}",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS["accent_cyan"], anchor="e")
        self._value_label.pack(side="right")

        self._slider = ctk.CTkSlider(
            self, from_=from_, to=to,
            number_of_steps=int(to - from_) if (to - from_) <= 100 else 100,
            fg_color=COLORS["slider_track"], progress_color=COLORS["accent_blue"],
            button_color=COLORS["text_primary"], button_hover_color="#FFFFFF",
            height=14, command=self._on_change)
        self._slider.set(value)
        self._slider.pack(fill="x")

    def _on_change(self, val):
        self._value_label.configure(text=f"{self._value_format(val)}{self._unit}")
        if self._command:
            self._command(val)

    def set(self, val):
        self._slider.set(val)
        self._value_label.configure(text=f"{self._value_format(val)}{self._unit}")


class CollapsibleSection(ctk.CTkFrame):
    """A section with a hint text and toggle button that expands/collapses a panel."""
    def __init__(self, master, hint_text, btn_show="Show", btn_hide="Hide",
                 icon_name=None, start_expanded=False, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._expanded = False

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x")

        icon = load_icon(icon_name, size=(13, 13)) if icon_name else None
        if icon:
            ctk.CTkLabel(row, text="", image=icon, width=13).pack(side="left", padx=(0, 5))

        ctk.CTkLabel(row, text=hint_text,
                     font=ctk.CTkFont(family="Segoe UI", size=10),
                     text_color=COLORS["text_muted"], anchor="w"
                     ).pack(side="left", fill="x", expand=True)

        self._btn_show = btn_show
        self._btn_hide = btn_hide
        self._toggle_btn = ctk.CTkButton(
            row, text=btn_show,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="transparent", hover_color=COLORS["bg_card_hover"],
            text_color=COLORS["accent_blue"], width=50, height=24, corner_radius=5,
            command=self._toggle)
        self._toggle_btn.pack(side="right")

        self._panel = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                   corner_radius=8, border_width=1,
                                   border_color=COLORS["border"])
        self.panel_inner = ctk.CTkFrame(self._panel, fg_color="transparent")
        self.panel_inner.pack(fill="x", padx=12, pady=10)

        if start_expanded:
            self._panel.pack(fill="x", pady=(6, 0))
            self._toggle_btn.configure(text=btn_hide)
            self._expanded = True

    def _toggle(self):
        # Freeze the window to prevent flicker during layout changes
        root = self.winfo_toplevel()
        root.update_idletasks()
        if self._expanded:
            self._panel.pack_forget()
            self._toggle_btn.configure(text=self._btn_show)
        else:
            self._panel.pack(fill="x", pady=(6, 0))
            self._toggle_btn.configure(text=self._btn_hide)
        self._expanded = not self._expanded
        root.update_idletasks()


# ─── MAIN APPLICATION WINDOW ─────────────────────────────────────────────────

class AlphaBoostApp(ctk.CTk):
    def __init__(self, engine_callbacks: dict):
        super().__init__()
        self.cb = engine_callbacks

        self.title("Alpha Boost Engine")
        self.geometry("440x680")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_primary"])
        self.attributes("-topmost", True)

        try:
            icon_path = (os.path.join(sys._MEIPASS, "icon", "app_icon.ico")
                         if hasattr(sys, "_MEIPASS")
                         else os.path.join("icon", "app_icon.ico"))
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("trznx.alphaboost.engine.2.0")
        except Exception:
            pass

        container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["border_accent"])
        container.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=14)

        # Build order: Header → Calibration → Controls → General Settings → Tips → Footer
        self._build_header(inner)
        self._build_calibration(inner)
        self._build_controls_card(inner)
        self._build_general_settings(inner)
        self._build_tips(inner)
        self._build_footer(inner)

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        logo_row = ctk.CTkFrame(header, fg_color="transparent")
        logo_row.pack(fill="x")

        logo_icon = load_icon("logo.png", size=(30, 30))
        if logo_icon:
            ctk.CTkLabel(logo_row, text="", image=logo_icon, width=30).pack(side="left", padx=(0, 10))

        title_block = ctk.CTkFrame(logo_row, fg_color="transparent")
        title_block.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(title_block, text="ALPHA BOOST ENGINE",
                     font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                     text_color=COLORS["text_primary"], anchor="center").pack(anchor="center")


    # ── Calibration (collapsible, at top) ─────────────────────────────────────

    def _build_calibration(self, parent):
        self._calib = CollapsibleSection(
            parent,
            hint_text="First time? Run calibration to set up boost tracking.",
            btn_show="Setup", btn_hide="Hide",
            icon_name="ic_calibration.png", start_expanded=False)
        self._calib.pack(fill="x", pady=(0, 10))

        p = self._calib.panel_inner

        self.btn_calibrate = ctk.CTkButton(
            p, text="Run Calibration",
            image=load_icon("ic_calibrate_btn.png", size=(14, 14)),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=COLORS["accent_blue"], hover_color=COLORS["accent_blue_dim"],
            text_color="#FFFFFF", height=32, corner_radius=7,
            command=self._on_calibrate)
        self.btn_calibrate.pack(fill="x")

        self.lbl_status = ctk.CTkLabel(
            p, text="Make sure you're in Freeplay with 0 boost.",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_muted"], anchor="w", wraplength=360, justify="left")
        self.lbl_status.pack(fill="x", pady=(6, 0))

    def _on_calibrate(self):
        res = messagebox.askyesno(
            "Calibration",
            "Are you sure you want to recalibrate?\n\n"
            "Make sure you are in Freeplay, your boost is at 0, "
            "and the game is Borderless/Windowed.", parent=self)
        if not res:
            return
        self.lbl_status.configure(text="Calibration starting...", text_color=COLORS["warning_yellow"])
        self.cb["start_calibration"](self._calibration_status_update)

    def _calibration_status_update(self, msg):
        self.after(0, lambda: self.lbl_status.configure(
            text=msg,
            text_color=COLORS["accent_cyan"] if "SUCCESS" in msg.upper()
            else COLORS["disabled_red"] if "ERROR" in msg.upper()
            else COLORS["warning_yellow"]))

    # ── Engine Controls ───────────────────────────────────────────────────────

    def _build_controls_card(self, parent):
        SectionHeader(parent, "Engine Controls", icon_name="ic_controls.png").pack(fill="x", pady=(0, 3))

        card = Card(parent)
        card.pack(fill="x", pady=(0, 10))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=12)

        self.toggle_active = ToggleRow(
            inner, label_text="Alpha Boost", shortcut_text="F5",
            initial=self.cb["get_active"](), icon_name="ic_boost.png",
            command=self._on_toggle_active)
        self.toggle_active.pack(fill="x", pady=(0, 5))

        ctk.CTkFrame(inner, height=1, fg_color=COLORS["divider"]).pack(fill="x", pady=5)

        self.toggle_freeplay = ToggleRow(
            inner, label_text="Freeplay Mode", shortcut_text="F4",
            initial=self.cb["get_freeplay"](), icon_name="ic_freeplay.png",
            command=self._on_toggle_freeplay)
        self.toggle_freeplay.pack(fill="x", pady=5)

        ctk.CTkFrame(inner, height=1, fg_color=COLORS["divider"]).pack(fill="x", pady=5)

        self.toggle_shortcuts = ToggleRow(
            inner, label_text="Keyboard Shortcuts", shortcut_text="",
            initial=self.cb["get_shortcuts"](), icon_name="ic_keyboard.png",
            command=self._on_toggle_shortcuts)
        self.toggle_shortcuts.pack(fill="x", pady=(5, 0))

    def _on_toggle_active(self):
        self.cb["toggle_active"]()

    def _on_toggle_freeplay(self):
        self.cb["toggle_freeplay"]()

    def _on_toggle_shortcuts(self):
        self.cb["toggle_shortcuts"]()

    # ── General Settings (merged profile + audio) ─────────────────────────────

    def _build_general_settings(self, parent):
        SectionHeader(parent, "General Settings", icon_name="ic_general_settings.png").pack(fill="x", pady=(0, 3))

        card = Card(parent)
        card.pack(fill="x", pady=(0, 10))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=12)

        # ── Sub-header: Sound Profile ──
        sp_header = ctk.CTkFrame(inner, fg_color="transparent")
        sp_header.pack(fill="x", pady=(0, 5))
        sp_icon = load_icon("ic_sound.png", size=(14, 14))
        if sp_icon:
            ctk.CTkLabel(sp_header, text="", image=sp_icon, width=14).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(sp_header, text="Sound Profile",
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(side="left")

        profiles = {
            "Alpha Boost (Test)": "alpha_test",
            "Classic Original Sound": "classic",
            "Quiet Loop Sound (Recommended)": "quiet_loop",
            "Quiet Loop 2 (Physics Based)": "quiet_loop_2",
            "Low-RPM Start Sound": "low_rpm",
        }
        self._profile_map = profiles
        self._profile_reverse = {v: k for k, v in profiles.items()}

        current_code = self.cb["get_profile"]()
        current_display = self._profile_reverse.get(current_code, "Quiet Loop Sound (Recommended)")

        self.combo_profile = ctk.CTkComboBox(
            inner, values=list(profiles.keys()), state="readonly",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=COLORS["bg_secondary"], border_color=COLORS["border_accent"],
            button_color=COLORS["accent_blue_dim"], button_hover_color=COLORS["accent_blue"],
            dropdown_fg_color=COLORS["bg_card"], dropdown_hover_color=COLORS["bg_card_hover"],
            dropdown_text_color=COLORS["text_primary"], text_color=COLORS["text_primary"],
            height=32, corner_radius=7, command=self._on_profile_change)
        self.combo_profile.set(current_display)
        self.combo_profile.pack(fill="x")

        # ── Sub-header: Audio Settings ──
        as_header = ctk.CTkFrame(inner, fg_color="transparent")
        as_header.pack(fill="x", pady=(25, 5))
        as_icon = load_icon("ic_audio.png", size=(14, 14))
        if as_icon:
            ctk.CTkLabel(as_header, text="", image=as_icon, width=14).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(as_header, text="Audio Settings",
                     font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                     text_color=COLORS["text_primary"], anchor="w").pack(side="left")

        self.slider_volume = SliderWithLabel(
            inner, label="Volume", from_=0, to=100,
            value=int(self.cb["get_volume"]() * 100), unit="%",
            icon_name="ic_volume.png", command=self._on_volume_change,
            value_format=lambda v: f"{int(v)}")
        self.slider_volume.pack(fill="x", pady=(0, 10))

        self.slider_delay = SliderWithLabel(
            inner, label="Audio Start Delay", from_=0, to=50,
            value=self.cb["get_delay"](), unit=" ms",
            icon_name="ic_delay.png", command=self._on_delay_change,
            value_format=lambda v: f"{int(v)}")
        self.slider_delay.pack(fill="x")

    def _on_profile_change(self, choice):
        code = self._profile_map.get(choice, "quiet_loop")
        self.cb["set_profile"](code)

    def _on_volume_change(self, val):
        self.cb["set_volume"](float(val) / 100.0)

    def _on_delay_change(self, val):
        self.cb["set_delay"](int(float(val)))

    # ── Tips & Info (collapsible) ─────────────────────────────────────────────

    def _build_tips(self, parent):
        self._tips_section = CollapsibleSection(
            parent, hint_text="Usage tips & important info",
            btn_show="Show", btn_hide="Hide",
            icon_name="ic_info.png", start_expanded=False)
        self._tips_section.pack(fill="x", pady=(0, 8))

        p = self._tips_section.panel_inner
        tips = [
            ("Freeplay Mode", "Enable only when using Unlimited Boost in Freeplay.", COLORS["accent_orange"]),
            ("Goal Replays", "Short sounds during replays or countdowns are normal.", COLORS["accent_purple"]),
            ("Calibration", "Ensure game is Borderless or Windowed Fullscreen.", COLORS["accent_cyan"]),
        ]
        for i, (title, desc, color) in enumerate(tips):
            tip_row = ctk.CTkFrame(p, fg_color="transparent")
            tip_row.pack(fill="x", pady=(0, 7 if i < len(tips) - 1 else 0))

            dot = ctk.CTkFrame(tip_row, width=6, height=6, corner_radius=3, fg_color=color)
            dot.pack(side="left", padx=(2, 10), anchor="n", pady=5)

            text_block = ctk.CTkFrame(tip_row, fg_color="transparent")
            text_block.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(text_block, text=title,
                         font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                         text_color=color, anchor="w").pack(anchor="w")
            ctk.CTkLabel(text_block, text=desc,
                         font=ctk.CTkFont(family="Segoe UI", size=10),
                         text_color=COLORS["text_secondary"], anchor="w",
                         wraplength=320, justify="left").pack(anchor="w")

    # ── Footer ────────────────────────────────────────────────────────────────

    def _build_footer(self, parent):
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", pady=(2, 0))
        ctk.CTkLabel(footer, text="Alpha Boost Engine v1.1.0  •  by trznx",
                     font=ctk.CTkFont(family="Segoe UI", size=9),
                     text_color=COLORS["text_muted"]).pack()

    # ── PUBLIC API ────────────────────────────────────────────────────────────

    def update_active_state(self, enabled: bool):
        self.toggle_active.set_state(enabled)

    def update_freeplay_state(self, enabled: bool):
        self.toggle_freeplay.set_state(enabled)

    def update_shortcuts_state(self, enabled: bool):
        self.toggle_shortcuts.set_state(enabled)

    def set_profile_display(self, profile_code: str):
        display = self._profile_reverse.get(profile_code, "Quiet Loop Sound (Recommended)")
        self.combo_profile.set(display)
