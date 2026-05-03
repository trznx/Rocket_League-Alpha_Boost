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

# Premium color tokens
COLORS = {
    "bg_primary":      "#0D0F14",
    "bg_secondary":    "#141820",
    "bg_card":         "#1A1F2B",
    "bg_card_hover":   "#1E2433",
    "border":          "#2A3040",
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
    "slider_track":    "#2A3040",
    "slider_fill":     "#4E8CFF",
    "divider":         "#1E2433",
}


# ─── ICON HELPER ──────────────────────────────────────────────────────────────

def _get_base_path():
    """Returns base path for bundled or development mode."""
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def load_icon(name, size=(20, 20)):
    """Load a PNG icon from interface_icons directory. Returns CTkImage or None."""
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
    """A small colored badge that displays ENABLED / DISABLED."""

    def __init__(self, master, enabled=True, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            corner_radius=6,
            height=24,
            fg_color=COLORS["enabled_bg"] if enabled else COLORS["disabled_bg"],
        )
        self._label = ctk.CTkLabel(
            self, text="ENABLED" if enabled else "DISABLED",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS["enabled_green"] if enabled else COLORS["disabled_red"],
            height=24,
        )
        self._label.pack(padx=10, pady=0)

    def set_state(self, enabled: bool):
        self.configure(
            fg_color=COLORS["enabled_bg"] if enabled else COLORS["disabled_bg"]
        )
        self._label.configure(
            text="ENABLED" if enabled else "DISABLED",
            text_color=COLORS["enabled_green"] if enabled else COLORS["disabled_red"],
        )


class ToggleRow(ctk.CTkFrame):
    """A row with icon, label, shortcut hint, toggle switch, and status badge."""

    def __init__(self, master, label_text, shortcut_text="", initial=True,
                 icon_name=None, command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._enabled = initial
        self._command = command

        # Icon
        icon = load_icon(icon_name) if icon_name else None

        # Left: icon + label
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        if icon:
            ctk.CTkLabel(left, text="", image=icon, width=20).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            left, text=label_text,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(side="left")

        if shortcut_text:
            ctk.CTkLabel(
                left, text=shortcut_text,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS["text_muted"],
                anchor="w",
            ).pack(side="left", padx=(6, 0))

        # Right: badge + switch
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right")

        self._badge = StatusBadge(right, enabled=initial)
        self._badge.pack(side="left", padx=(0, 10))

        self._switch = ctk.CTkSwitch(
            right, text="", width=44, height=22,
            switch_width=40, switch_height=20,
            fg_color=COLORS["slider_track"],
            progress_color=COLORS["enabled_green"],
            button_color=COLORS["text_primary"],
            button_hover_color="#FFFFFF",
            command=self._on_toggle,
        )
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
    """A styled section header with icon and divider."""

    def __init__(self, master, title, icon_name=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        icon = load_icon(icon_name, size=(16, 16)) if icon_name else None

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(0, 8))

        if icon:
            ctk.CTkLabel(row, text="", image=icon, width=16).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            row, text=title.upper(),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(side="left")

        # subtle divider line
        ctk.CTkFrame(
            row, height=1, fg_color=COLORS["border"], corner_radius=0
        ).pack(side="left", fill="x", expand=True, padx=(12, 0), pady=1)


class Card(ctk.CTkFrame):
    """A subtle card container with rounded corners and border."""

    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", COLORS["bg_card"])
        kwargs.setdefault("corner_radius", 12)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", COLORS["border"])
        super().__init__(master, **kwargs)


class SliderWithLabel(ctk.CTkFrame):
    """A labeled slider with live value readout."""

    def __init__(self, master, label, from_, to, value, unit="%",
                 icon_name=None, command=None, value_format=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._command = command
        self._unit = unit
        self._value_format = value_format or (lambda v: f"{int(v)}")

        # Header row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 6))

        icon = load_icon(icon_name, size=(16, 16)) if icon_name else None
        if icon:
            ctk.CTkLabel(header, text="", image=icon, width=16).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            header, text=label,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(side="left")

        self._value_label = ctk.CTkLabel(
            header,
            text=f"{self._value_format(value)}{unit}",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=12),
            text_color=COLORS["accent_cyan"],
            anchor="e",
        )
        self._value_label.pack(side="right")

        # Slider
        self._slider = ctk.CTkSlider(
            self, from_=from_, to=to,
            number_of_steps=int(to - from_) if (to - from_) <= 100 else 100,
            fg_color=COLORS["slider_track"],
            progress_color=COLORS["accent_blue"],
            button_color=COLORS["text_primary"],
            button_hover_color="#FFFFFF",
            height=16,
            command=self._on_change,
        )
        self._slider.set(value)
        self._slider.pack(fill="x")

    def _on_change(self, val):
        self._value_label.configure(text=f"{self._value_format(val)}{self._unit}")
        if self._command:
            self._command(val)

    def set(self, val):
        self._slider.set(val)
        self._value_label.configure(text=f"{self._value_format(val)}{self._unit}")


# ─── MAIN APPLICATION WINDOW ─────────────────────────────────────────────────

class AlphaBoostApp(ctk.CTk):
    """
    The main application window.
    Receives engine callback references so it can control the engine.
    """

    def __init__(self, engine_callbacks: dict):
        super().__init__()

        self.cb = engine_callbacks

        # ── Window Setup ──────────────────────────────────────────────────
        self.title("Alpha Boost Engine")
        self.geometry("480x720")
        self.minsize(460, 680)
        self.resizable(True, True)
        self.configure(fg_color=COLORS["bg_primary"])
        self.attributes("-topmost", True)

        # App icon
        try:
            icon_path = (
                os.path.join(sys._MEIPASS, "icon", "app_icon.ico")
                if hasattr(sys, "_MEIPASS")
                else os.path.join("icon", "app_icon.ico")
            )
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

        # App ID for taskbar grouping
        try:
            import ctypes
            myappid = "trznx.alphaboost.engine.2.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        # ── Scrollable Container ──────────────────────────────────────────
        container = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["border_accent"],
        )
        container.pack(fill="both", expand=True, padx=0, pady=0)

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        # ── HEADER ────────────────────────────────────────────────────────
        self._build_header(inner)

        # ── ENGINE CONTROLS CARD ──────────────────────────────────────────
        self._build_controls_card(inner)

        # ── SOUND PROFILE CARD ────────────────────────────────────────────
        self._build_profile_card(inner)

        # ── AUDIO SETTINGS CARD ───────────────────────────────────────────
        self._build_audio_card(inner)

        # ── CALIBRATION CARD ──────────────────────────────────────────────
        self._build_calibration_card(inner)

        # ── TIPS & INFO CARD ──────────────────────────────────────────────
        self._build_tips_card(inner)

        # ── FOOTER ────────────────────────────────────────────────────────
        self._build_footer(inner)

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        # Logo row
        logo_row = ctk.CTkFrame(header, fg_color="transparent")
        logo_row.pack(fill="x")

        logo_icon = load_icon("logo.png", size=(36, 36))
        if logo_icon:
            ctk.CTkLabel(logo_row, text="", image=logo_icon, width=36).pack(side="left", padx=(0, 12))

        title_block = ctk.CTkFrame(logo_row, fg_color="transparent")
        title_block.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            title_block, text="Alpha Boost Engine",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_block, text="Rocket League Audio Enhancer",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(anchor="w")

        # Accent line under header
        gradient_line = ctk.CTkFrame(header, height=2, fg_color=COLORS["accent_blue"], corner_radius=1)
        gradient_line.pack(fill="x", pady=(12, 0))

    # ── Engine Controls ───────────────────────────────────────────────────────

    def _build_controls_card(self, parent):
        SectionHeader(parent, "Engine Controls", icon_name="ic_controls.png").pack(fill="x", pady=(0, 4))

        card = Card(parent)
        card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)

        # Alpha Boost toggle
        self.toggle_active = ToggleRow(
            inner,
            label_text="Alpha Boost",
            shortcut_text="F5",
            initial=self.cb["get_active"](),
            icon_name="ic_boost.png",
            command=self._on_toggle_active,
        )
        self.toggle_active.pack(fill="x", pady=(0, 6))

        # Divider
        ctk.CTkFrame(inner, height=1, fg_color=COLORS["divider"]).pack(fill="x", pady=6)

        # Freeplay Mode toggle
        self.toggle_freeplay = ToggleRow(
            inner,
            label_text="Freeplay Mode",
            shortcut_text="F4",
            initial=self.cb["get_freeplay"](),
            icon_name="ic_freeplay.png",
            command=self._on_toggle_freeplay,
        )
        self.toggle_freeplay.pack(fill="x", pady=(6, 6))

        # Divider
        ctk.CTkFrame(inner, height=1, fg_color=COLORS["divider"]).pack(fill="x", pady=6)

        # Keyboard Shortcuts toggle
        self.toggle_shortcuts = ToggleRow(
            inner,
            label_text="Keyboard Shortcuts",
            shortcut_text="",
            initial=self.cb["get_shortcuts"](),
            icon_name="ic_keyboard.png",
            command=self._on_toggle_shortcuts,
        )
        self.toggle_shortcuts.pack(fill="x", pady=(6, 0))

    def _on_toggle_active(self):
        self.cb["toggle_active"]()

    def _on_toggle_freeplay(self):
        self.cb["toggle_freeplay"]()

    def _on_toggle_shortcuts(self):
        self.cb["toggle_shortcuts"]()

    # ── Sound Profile ─────────────────────────────────────────────────────────

    def _build_profile_card(self, parent):
        SectionHeader(parent, "Sound Profile", icon_name="ic_sound.png").pack(fill="x", pady=(0, 4))

        card = Card(parent)
        card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)

        profiles = {
            "Classic Original Sound": "classic",
            "Quiet Loop Sound (Recommended)": "quiet_loop",
            "Low-RPM Start Sound": "low_rpm",
        }
        self._profile_map = profiles
        self._profile_reverse = {v: k for k, v in profiles.items()}

        ctk.CTkLabel(
            inner, text="Active Profile",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
        ).pack(anchor="w", pady=(0, 6))

        current_code = self.cb["get_profile"]()
        current_display = self._profile_reverse.get(current_code, "Quiet Loop Sound (Recommended)")

        self.combo_profile = ctk.CTkComboBox(
            inner,
            values=list(profiles.keys()),
            state="readonly",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border_accent"],
            button_color=COLORS["accent_blue_dim"],
            button_hover_color=COLORS["accent_blue"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["bg_card_hover"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            height=36,
            corner_radius=8,
            command=self._on_profile_change,
        )
        self.combo_profile.set(current_display)
        self.combo_profile.pack(fill="x")

        # Shortcut hint — centered
        shortcuts_outer = ctk.CTkFrame(inner, fg_color="transparent")
        shortcuts_outer.pack(fill="x", pady=(8, 0))

        shortcuts_hint = ctk.CTkFrame(shortcuts_outer, fg_color="transparent")
        shortcuts_hint.pack(anchor="center")

        hint_items = [
            ("F1", "Classic"),
            ("F2", "Quiet Loop"),
            ("F3", "Low-RPM"),
        ]
        for key, label in hint_items:
            chip = ctk.CTkFrame(shortcuts_hint, fg_color=COLORS["bg_secondary"], corner_radius=6)
            chip.pack(side="left", padx=3)
            ctk.CTkLabel(
                chip,
                text=f" {key} ",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color=COLORS["accent_blue"],
            ).pack(side="left", padx=(6, 2), pady=3)
            ctk.CTkLabel(
                chip,
                text=label,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=COLORS["text_muted"],
            ).pack(side="left", padx=(0, 6), pady=3)

    def _on_profile_change(self, choice):
        code = self._profile_map.get(choice, "quiet_loop")
        self.cb["set_profile"](code)

    # ── Audio Settings ────────────────────────────────────────────────────────

    def _build_audio_card(self, parent):
        SectionHeader(parent, "Audio Settings", icon_name="ic_audio.png").pack(fill="x", pady=(0, 4))

        card = Card(parent)
        card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)

        # Volume slider
        self.slider_volume = SliderWithLabel(
            inner,
            label="Volume",
            from_=0, to=100,
            value=int(self.cb["get_volume"]() * 100),
            unit="%",
            icon_name="ic_volume.png",
            command=self._on_volume_change,
            value_format=lambda v: f"{int(v)}",
        )
        self.slider_volume.pack(fill="x", pady=(0, 14))

        # Divider
        ctk.CTkFrame(inner, height=1, fg_color=COLORS["divider"]).pack(fill="x", pady=4)

        # Delay slider
        self.slider_delay = SliderWithLabel(
            inner,
            label="Audio Start Delay",
            from_=0, to=50,
            value=self.cb["get_delay"](),
            unit=" ms",
            icon_name="ic_delay.png",
            command=self._on_delay_change,
            value_format=lambda v: f"{int(v)}",
        )
        self.slider_delay.pack(fill="x", pady=(14, 0))

    def _on_volume_change(self, val):
        self.cb["set_volume"](float(val) / 100.0)

    def _on_delay_change(self, val):
        self.cb["set_delay"](int(float(val)))

    # ── Calibration ───────────────────────────────────────────────────────────

    def _build_calibration_card(self, parent):
        """Subtle, collapsible calibration section — not prominent."""
        calib_frame = ctk.CTkFrame(parent, fg_color="transparent")
        calib_frame.pack(fill="x", pady=(0, 8))

        # Collapsed state: a small muted text link + status
        self._calib_expanded = False

        # Top row: muted hint text + expand button
        row = ctk.CTkFrame(calib_frame, fg_color="transparent")
        row.pack(fill="x")

        icon = load_icon("ic_calibration.png", size=(14, 14))
        if icon:
            ctk.CTkLabel(row, text="", image=icon, width=14).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            row, text="First time? Run calibration to set up boost tracking.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_muted"],
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        self._calib_toggle_btn = ctk.CTkButton(
            row, text="Setup",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color="transparent",
            hover_color=COLORS["bg_card_hover"],
            text_color=COLORS["accent_blue"],
            width=60, height=28,
            corner_radius=6,
            command=lambda: self._toggle_calib_panel(calib_frame),
        )
        self._calib_toggle_btn.pack(side="right")

        # Expandable panel (hidden by default)
        self._calib_panel = ctk.CTkFrame(calib_frame, fg_color=COLORS["bg_card"],
                                          corner_radius=10, border_width=1,
                                          border_color=COLORS["border"])
        # Don't pack yet — starts collapsed

        panel_inner = ctk.CTkFrame(self._calib_panel, fg_color="transparent")
        panel_inner.pack(fill="x", padx=14, pady=12)

        self.btn_calibrate = ctk.CTkButton(
            panel_inner,
            text="Run Calibration",
            image=load_icon("ic_calibrate_btn.png", size=(16, 16)),
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_blue_dim"],
            text_color="#FFFFFF",
            height=36,
            corner_radius=8,
            command=self._on_calibrate,
        )
        self.btn_calibrate.pack(fill="x")

        self.lbl_status = ctk.CTkLabel(
            panel_inner,
            text="Make sure you're in Freeplay with 0 boost.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["text_muted"],
            anchor="w",
            wraplength=380,
            justify="left",
        )
        self.lbl_status.pack(fill="x", pady=(8, 0))

    def _toggle_calib_panel(self, parent_frame):
        if self._calib_expanded:
            self._calib_panel.pack_forget()
            self._calib_toggle_btn.configure(text="Setup")
        else:
            self._calib_panel.pack(fill="x", pady=(8, 0))
            self._calib_toggle_btn.configure(text="Hide")
        self._calib_expanded = not self._calib_expanded

    def _on_calibrate(self):
        res = messagebox.askyesno(
            "Calibration",
            "Are you sure you want to recalibrate?\n\n"
            "Make sure you are in Freeplay, your boost is at 0, "
            "and the game is Borderless/Windowed.",
            parent=self,
        )
        if not res:
            return
        self.lbl_status.configure(text="Calibration starting...", text_color=COLORS["warning_yellow"])
        self.cb["start_calibration"](self._calibration_status_update)

    def _calibration_status_update(self, msg):
        """Called from calibration thread – must schedule on main thread."""
        self.after(0, lambda: self.lbl_status.configure(
            text=msg,
            text_color=COLORS["accent_cyan"] if "SUCCESS" in msg.upper()
            else COLORS["disabled_red"] if "ERROR" in msg.upper()
            else COLORS["warning_yellow"],
        ))

    # ── Tips & Info ───────────────────────────────────────────────────────────

    def _build_tips_card(self, parent):
        SectionHeader(parent, "Tips & Info", icon_name="ic_info.png").pack(fill="x", pady=(0, 4))

        card = Card(parent)
        card.pack(fill="x", pady=(0, 12))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)

        tips = [
            {
                "icon": "ic_tip_freeplay.png",
                "title": "Freeplay Mode",
                "desc": "Enable only when using Unlimited Boost in Freeplay.",
                "color": COLORS["accent_orange"],
            },
            {
                "icon": "ic_tip_replay.png",
                "title": "Goal Replays",
                "desc": "Short sounds during replays or countdowns are normal.",
                "color": COLORS["accent_purple"],
            },
            {
                "icon": "ic_tip_calibrate.png",
                "title": "Calibration",
                "desc": "Ensure game is Borderless or Windowed Fullscreen.",
                "color": COLORS["accent_cyan"],
            },
        ]

        for i, tip in enumerate(tips):
            tip_row = ctk.CTkFrame(inner, fg_color="transparent")
            tip_row.pack(fill="x", pady=(0, 10 if i < len(tips) - 1 else 0))

            icon = load_icon(tip["icon"], size=(16, 16))

            # Colored dot / icon
            if icon:
                ctk.CTkLabel(tip_row, text="", image=icon, width=16).pack(side="left", padx=(0, 10), anchor="n", pady=2)
            else:
                dot = ctk.CTkFrame(tip_row, width=8, height=8, corner_radius=4, fg_color=tip["color"])
                dot.pack(side="left", padx=(4, 14), anchor="n", pady=6)

            text_block = ctk.CTkFrame(tip_row, fg_color="transparent")
            text_block.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                text_block, text=tip["title"],
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=tip["color"],
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                text_block, text=tip["desc"],
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS["text_secondary"],
                anchor="w",
                wraplength=340,
                justify="left",
            ).pack(anchor="w")

    # ── Footer ────────────────────────────────────────────────────────────────

    def _build_footer(self, parent):
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", pady=(4, 0))

        ctk.CTkLabel(
            footer,
            text="Alpha Boost Engine v2.0  •  by trznx",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["text_muted"],
        ).pack()

    # ── PUBLIC API (called from main.py via keyboard shortcuts) ────────────

    def update_active_state(self, enabled: bool):
        self.toggle_active.set_state(enabled)

    def update_freeplay_state(self, enabled: bool):
        self.toggle_freeplay.set_state(enabled)

    def update_shortcuts_state(self, enabled: bool):
        self.toggle_shortcuts.set_state(enabled)

    def set_profile_display(self, profile_code: str):
        display = self._profile_reverse.get(profile_code, "Quiet Loop Sound (Recommended)")
        self.combo_profile.set(display)
