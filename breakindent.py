# -*- coding: utf-8 -*-
#
#  breakindent.py (v0.1)
#    ~
#
#  Copyright (C) 2016 - Sergej Chodarev
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330,
#  Boston, MA 02111-1307, USA.

from gi.repository import Gdk, Gedit, GObject, Gtk, Pango

class BreakIndent(GObject.Object, Gedit.ViewActivatable):
    __gtype_name__ = "BreakIndent"

    view = GObject.property(type=Gedit.View)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.buffer = self.view.get_buffer()
        self.char_width = self.get_char_width()
        self.tags = {}
        self.handlers = [self.buffer.connect("changed", self.on_changed)]
        self.add_margins()

    def do_deactivate(self):
        # Remove event handelers
        for handler in self.handlers:
            self.buffer.disconnect(handler)
        table = self.buffer.get_tag_table()
        for tag in self.tags.values():
            table.remove(tag)

    def do_update_state(self):
        pass

    def on_changed(self, buffer):
        """React to change of text."""
        self.add_margins()

    def add_margins(self):
        lines = self.buffer.get_line_count()
        for i in range(lines):
            itr = self.buffer.get_iter_at_line(i)
            start = itr.copy()
            while itr.get_char().isspace() and not itr.ends_line():
                itr.forward_char()
            position = itr.get_line_offset()
            # print(i, position, margin)
            tag = self.get_tag(position)
            itr.forward_line()
            self.apply_tag(tag, start, itr)

    def get_char_width(self):
        """Try to get current default font and calculate character width."""
        try:
            view = self.window.get_active_view()
            # Get font description (code from "text size" plugin)
            context = view.get_style_context()
            description = context.get_font(context.get_state()).copy()
            # Get font metrics
            pango_context = view.get_pango_context()
            lang = Pango.Language.get_default()
            metrics = pango_context.get_metrics(description, lang)
            # Calculate char width in pixels
            width = metrics.get_approximate_char_width() / Pango.SCALE
            return width
        except:
            return 8 # If it didn't work, just use some appropriate value

    def get_tag(self, position):
        if position not in self.tags:
            margin = position * self.char_width
            tag = self.buffer.create_tag(indent=-margin, indent_set=True)
            self.tags[position] = tag
        else:
            tag = self.tags[position]
        return tag
    
    def apply_tag(self, tag, start, end):
        self.buffer.apply_tag(tag, start, end)
        for t in self.tags.values():
            if t != tag:
                self.buffer.remove_tag(t, start, end)

