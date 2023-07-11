#!/usr/bin/env python
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


class TextdungeonActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self.max_participants = 1

        self.build_toolbar()

        self.create_menu()

    def create_menu(self):
        # Loading menu background image and creating pixbuf
        menu_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename='backgrounds/menu_background.jpg',
            width=Gdk.Screen.width(),
            height=Gdk.Screen.height(),
            preserve_aspect_ratio=True)

        # Creating image and setting pixbuf
        menu_img = Gtk.Image.new_from_pixbuf(menu_pixbuf)

        # Creating overlay and packing image
        menu_overlay = Gtk.Overlay()
        menu_overlay.add(menu_img)

        # Create a vertical box to stack widgets
        self.menu_vbox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6)
        menu_overlay.add_overlay(self.menu_vbox)
        self.menu_vbox.set_halign(Gtk.Align.CENTER)
        self.menu_vbox.set_valign(Gtk.Align.CENTER)

        # Create three buttons
        for i in range(1, 4):
            button = Gtk.Button(label="Button " + str(i))
            button.connect("clicked", self.on_button_clicked, i)
            self.menu_vbox.pack_start(button, True, True, 0)

        # Add overlay as the canvas
        self.set_canvas(menu_overlay)
        menu_overlay.show_all()

    def on_button_clicked(self, button, button_number):
        self.create_game_screen(button_number)
        self.start_game(button_number)

    def create_game_screen(self, level):
        # Loading image and creating pixbuf
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=f'backgrounds/background{level}.jpg',
            width=Gdk.Screen.width(),
            height=Gdk.Screen.height(),
            preserve_aspect_ratio=True)

        # Creating image and setting pixbuf
        img = Gtk.Image.new_from_pixbuf(pixbuf)

        # Creating overlay and packing image
        overlay = Gtk.Overlay()
        overlay.add(img)

        # Create a vertical box to stack widgets
        self.vbox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6)
        overlay.add_overlay(self.vbox)
        self.vbox.set_halign(Gtk.Align.CENTER)
        self.vbox.set_valign(Gtk.Align.CENTER)

        # Create a textview to show the game output
        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_editable(False)
        self.textview.set_left_margin(10)
        self.textview.set_right_margin(10)
        self.textview.set_top_margin(5)
        self.textview.set_bottom_margin(10)

        # Initialize the text buffer and text tag
        # For changing the color of the outputing of the input text
        self.text_buffer = self.textview.get_buffer()
        self.custom_tag = self.text_buffer.create_tag(
            "custom", foreground="#424548")

        # Add TextView to a ScrolledWindow
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_size_request(300, 300)

        self.scrolled_window.add(self.textview)
        self.vbox.pack_start(self.scrolled_window, True, True, 0)

        # Create an entry for player's input
        self.entry = Gtk.Entry()
        self.vbox.pack_start(self.entry, False, True, 0)

        # When the enter key is pressed in the entry, call on_activate
        self.entry.connect("activate", self.on_activate)

        # Add overlay as the canvas
        self.set_canvas(overlay)
        overlay.show_all()
        self.entry.grab_focus()

    def start_game(self, level):
        # Create the game and set it in the game window
        self.game = Game(f'maps/map{level}.json', self)

    def clear_textview(self):
        buffer = self.textview.get_buffer()
        buffer.set_text("")

    def on_activate(self, widget):
        command = widget.get_text()
        self.print_to_textview(command, True)
        widget.set_text("")
        self.game.process_command(command)

    def append_text(self, text, from_input=False):
        buffer = self.textview.get_buffer()
        if not from_input:
            buffer.insert_with_tags_by_name(buffer.get_end_iter(), text + "\n")
        else:
            buffer.insert_with_tags_by_name(buffer.get_end_iter(), text + "\n", "custom")

    # This will be called instead of print
    def print_to_textview(self, text, from_input=False):
        self.append_text(text + '\n', from_input)
        GLib.idle_add(self.scroll_to_bottom)

    def scroll_to_bottom(self):
        buffer = self.textview.get_buffer()
        mark = buffer.get_insert()
        GLib.idle_add(self.textview.scroll_to_mark, mark, 0.0, True, 0.0, 1.0)

    def build_toolbar(self):
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
