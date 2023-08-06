# Copyright (C) 2023  Dimitios Mylonas

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# !/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GdkPixbuf

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from game_engine import Game

BUTTON_LABELS = ("Easy", "Medium", "Hard")
MENU_BACKGROUND_PATH = 'backgrounds/menu_background.png'
GAME_BACKGROUND_PATH = 'backgrounds/background{}.png'
MAP_PATH = 'map{}.json'
BOX_SPACING = 6


class TextdungeonActivity(activity.Activity):
    def __init__(self, handle):
        super().__init__(handle)
        self.max_participants = 1

        self.create_toolbar()
        self.create_menu()

    def create_toolbar(self):
        # Create a toolbar with an activity button and a stop button
        toolbar_box = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        self.show_all()

    def create_menu(self):
        menu_overlay = self.create_overlay_from_image(MENU_BACKGROUND_PATH)

        button_css = """
        button {
            background-color: #0B0B45;
            color: white;
            font: 20px Roboto, sans-serif;
            border-radius: 10px;
            padding: 5px 10px;
        }
        button:hover {
            background-color: #23395d;
        }
        """
        # Create a CssProvider
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(button_css.encode())

        # Create a button for each level difficulty and add it to the vbox
        for i, label in enumerate(BUTTON_LABELS, start=1):
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_button_clicked, i)
            self.vbox.pack_start(button, True, True, 0)

            # Add the CssProvider to the button's style context
            context = button.get_style_context()
            context.add_provider(
                css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # Set the canvas to the menu_overlay and display it
        self.set_canvas(menu_overlay)
        menu_overlay.show_all()

    def on_button_clicked(self, button, button_number):
        self.create_game_screen(button_number)
        self.start_game(button_number)

    def create_game_screen(self, level):
        overlay = self.create_overlay_from_image(
            GAME_BACKGROUND_PATH.format(level))

        self.create_text_view()
        self.create_entry_field()

        # Set the canvas to the overlay and display it,
        # then focus on the entry field
        self.set_canvas(overlay)
        overlay.show_all()
        self.entry.grab_focus()

    def clear_textview(self):
        buffer = self.textview.get_buffer()
        buffer.set_text("")

    def create_entry_field(self):
        self.entry = Gtk.Entry()
        self.vbox.pack_start(self.entry, False, True, 0)
        self.entry.connect("activate", self.on_activate)

    def start_game(self, level):
        self.game = Game(MAP_PATH.format(level), self)

    def on_activate(self, widget):
        command = widget.get_text()  # Retrieve command from entry field
        self.print_to_textview(command, True)
        widget.set_text("")  # Clear the entry field
        self.game.process_command(command)

    def print_to_textview(self, text, from_input=False):
        buffer = self.textview.get_buffer()
        # Insert the text to the buffer and scroll to bottom
        if not from_input:
            buffer.insert_with_tags_by_name(buffer.get_end_iter(), text + "\n")
        else:
            buffer.insert_with_tags_by_name(
                buffer.get_end_iter(), text + "\n", "custom")
        GLib.idle_add(self.scroll_to_bottom)

    def scroll_to_bottom(self):
        buffer = self.textview.get_buffer()
        mark = buffer.get_insert()
        GLib.idle_add(self.textview.scroll_to_mark, mark, 0.0, True, 0.0, 1.0)

    def create_overlay_from_image(self, image_path, is_menu=False):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=image_path,
            width=Gdk.Screen.width(),
            height=Gdk.Screen.height(),
            preserve_aspect_ratio=False)

        img = Gtk.Image.new_from_pixbuf(pixbuf)

        overlay = Gtk.Overlay()
        overlay.add(img)

        self.vbox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=BOX_SPACING)
        overlay.add_overlay(self.vbox)
        self.vbox.set_halign(Gtk.Align.CENTER)
        self.vbox.set_valign(Gtk.Align.CENTER)

        if is_menu:
            self.menu_vbox = self.vbox

        return overlay

    def create_text_view(self):
        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_editable(False)
        self.textview.set_left_margin(15)
        self.textview.set_right_margin(10)
        self.textview.set_top_margin(5)
        self.textview.set_bottom_margin(10)

        self.text_buffer = self.textview.get_buffer()
        self.custom_tag = self.text_buffer.create_tag(
            "custom", foreground="#424548")

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_size_request(500, 300)

        self.scrolled_window.add(self.textview)
        self.vbox.pack_start(self.scrolled_window, True, True, 0)
