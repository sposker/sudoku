from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text.markup import MarkupLabel
from kivy.factory import Factory
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

import classes
from __init__ import *
import re

DARK_HIGHLIGHT = (0.1568627450980392, 0.16862745098039217, 0.18823529411764706, 1)  # Darkest Gray
BACKGROUND_COLOR = (0.18823529411764706, 0.19215686274509805, 0.21176470588235294, 1)  # Dark gray
ELEMENT_COLOR = (0.21176470588235294, 0.2235294117647059, 0.25882352941176473, 1)  # Medium Gray
LIGHT_HIGHLIGHT = (0.39215686274509803, 0.396078431372549, 0.41568627450980394, 1)  # Lighter Gray
TEXT_COLOR = (0.6705882352941176, 0.6705882352941176, 0.6705882352941176, 1)  # Lightest Gray
APP_COLORS = [DARK_HIGHLIGHT, BACKGROUND_COLOR, ELEMENT_COLOR, LIGHT_HIGHLIGHT, TEXT_COLOR]

ITEM_ROW_HEIGHT = 72
TEXT_BASE_SIZE = 40

Window.size = (round(1440 * 1.618) / 2, 1440 / 2)

Window.borderless = True


class TaskButton(ButtonBehavior, Image):
    """Callback based buttons for logical execution"""

    buttons = {
        'Hint': None,
        'Show Hotkeys': None,
        'Open Puzzle': None,
        'Solve': None,
        'Reset': None,
        'Settings': None,
    }

    def task_button_callback(self, button_text):
        print(button_text)


class TaskButtonLayout(FloatLayout):
    """Layout for single buttons and names"""

    button_text = StringProperty()
    image_path = StringProperty()


class ToggleLayout(FloatLayout):
    """Layout that holds pairs of toggle buttons"""

    pair_name = StringProperty()


class PanelToggle(ToggleButton):
    """Toggles for PanelLayout"""

    def on_touch_down(self, touch):
        if self.state == 'down':
            pass
        else:
            super().on_touch_down(touch)


class Panel(FloatLayout):
    """Holds buttons on sidebar"""


class TileBackground(Label):
    """Background for number entry tiles"""


class Guesses(TextInput):
    """Notes for tiles"""


class TileInput(TextInput):
    """Widget that allows setting values"""

    pat = re.compile('[^1-9]')
    tile_inputs = {}
    num_codes = {
        (260, 'numpad4'): (-1, 0),
        (264, 'numpad8'): (0, 1),
        (262, 'numpad6'): (1, 0),
        (258, 'numpad2'): (0, -1),
    }
    codes = {
        (273, 'up'): (0, 1),
        (276, 'left'): (-1, 0),
        (274, 'down'): (0, -1),
        (275, 'right'): (1, 0),
    }

    def __init__(self, grid_pos, label, locked=False, **kwargs):
        self.grid_pos = grid_pos
        self.label = label
        self.locked = locked
        self.tile_inputs[self.grid_pos] = self
        super().__init__(**kwargs)

    def find_next_focus(self, movement: (int, int)):
        x, y = self.grid_pos
        dx, dy = movement

        new_x = new_y = None

        if x + dx == -1:
            new_x = 8
        elif x + dx == 9:
            new_x = 0
        elif new_x is None:
            new_x = x + dx

        if y + dy == -1:
            new_y = 8
        elif y + dy == 9:
            new_y = 0
        elif new_y is None:
            new_y = y + dy

        w = self.tile_inputs[(new_x, new_y)]
        if not w.locked:
            w.focus = True
        else:
            w.find_next_focus(movement)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):

        if 'numlock' not in modifiers and keycode in self.num_codes.keys():
            self.find_next_focus(self.num_codes[keycode])

        elif keycode in self.codes.keys():
            self.find_next_focus(self.codes[keycode])

        elif 'shift' in modifiers and keycode == (9, 'tab'):
            self.not_focus()

        super().keyboard_on_key_down(window, keycode, text, modifiers)

    def _on_focus(self, instance, value, *largs):
        super()._on_focus(instance, value, *largs)
        print(self.grid_pos)
        if self.locked:
            w = self.get_focus_next()
            w.focus = True

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if len(self.text):
            self.text = ''
        s = re.sub(pat, '', substring)
        return super(TileInput, self).insert_text(s, from_undo=from_undo)

    def focus_helper(self, sign, end):

        if self.grid_pos[0] == end:
            if self.grid_pos[1] == end - 8:
                return self.tile_inputs[0, 8]
            else:
                return self.tile_inputs[0, self.grid_pos[1] - sign]
        else:
            return self.tile_inputs[self.grid_pos[0] + sign, self.grid_pos[1]]  # TODO

    def get_focus_next(self):
        print('focus')
        return self.focus_helper(1, 8)

    def not_focus(self):
        print('not focus')
        return self.focus_helper(-1, 8)

    def on_text_validate(self):
        pass

    # def set_text(self):
    #     # if self.defaults_button:
    #         # hide_widget(self)
    #         # hide_widget(self.defaults_button, dohide=False)
    #         redraw_canvas(self.defaults_button, DARK_HIGHLIGHT)
    #         self.defaults_button.text = self.text
    #
    # def on_text_validate(self):
    #     redraw_canvas(self, DARK_HIGHLIGHT)
    #     self.set_text()
    #
    # def _unbind_keyboard(self):
    #     redraw_canvas(self, DARK_HIGHLIGHT)
    #     super()._unbind_keyboard()
    #     self.set_text()


class TileLabel(Label):
    """Label for fixed values"""

    underline = True

    def __init__(self, value, grid_pos, **kwargs):
        super().__init__(**kwargs)
        self.grid_pos = grid_pos
        self.text = str(value) if value else ''


class ThreeBy(FloatLayout):
    """3x3 grid"""

    def __init__(self, grid_pos, **kwargs):
        self.grid_pos = grid_pos
        self._h_offset, self._v_offset = 3 * grid_pos[0], 3 * grid_pos[1]
        super().__init__(**kwargs)

    def populate_backgrounds(self, **_):

        for horiz in [0, 1, 2]:
            for vert in [0, 1, 2]:
                _h, _v = [i * 1 / 3 + .01 for i in [horiz, vert]]
                _w = TileBackground()
                self.add_widget(_w)
                _w.size_hint = (.315, .315)
                _w.pos_hint = {'x': _h, 'y': _v}

    def populate_tiles(self, **_):
        app = App.get_running_app()
        for horiz in [0, 1, 2]:
            for vert in [0, 1, 2]:
                _h_pos, _v_pos = [i * 1 / 3 + .01 for i in [horiz, vert]]
                coords = (self._h_offset + horiz, self._v_offset + vert)
                lock = True if horiz == vert else False

                try:
                    if horiz == vert:
                        value = 9
                    else:
                        value = app.board[coords]
                except KeyError:
                    tile_label = TileLabel(None, coords)
                    tile_input = TileInput(coords, tile_label, locked=lock)
                else:
                    tile_label = TileLabel(value, coords)
                    tile_input = TileInput(coords, tile_label, locked=lock)

                TileInput.tile_inputs[coords] = tile_input

                for widget in [tile_input, tile_label]:
                    if widget:
                        self.add_widget(widget)
                        widget.size_hint = (.315, .315)
                        y_offset = -.04 if isinstance(widget, TileInput) else 0
                        widget.pos_hint = {'x': _h_pos, 'y': _v_pos + y_offset}


class NineBy(FloatLayout):
    """9x9 board"""

    instance = None

    def __init__(self, **kw):
        super().__init__(**kw)
        thirds = [0, 1, 2]
        NineBy.instance = self

        for vert in thirds:
            for horiz in thirds:
                w = ThreeBy((horiz, vert))
                self.add_widget(w)
                w.populate_backgrounds()
                w.populate_tiles()
                w.size_hint = (.315, .315)
                _h, _v = [i * 1 / 3 + .01 for i in [horiz, vert]]
                w.pos_hint = {'x': _h, 'y': _v}


class Main(FloatLayout):
    """Main screen"""


class SudokuSolverApp(App):
    # Config Properties

    dh_color = DARK_HIGHLIGHT
    dh_color_string = as_string(dh_color)
    dh_color_list = as_list(dh_color)

    bg_color = BACKGROUND_COLOR
    bg_color_string = as_string(bg_color)
    bg_color_list = as_list(bg_color)

    elem_color = ELEMENT_COLOR
    elem_color_string = as_string(elem_color)
    elem_color_list = as_list(elem_color)

    lh_color = LIGHT_HIGHLIGHT
    lh_color_string = as_string(lh_color)
    lh_color_list = as_list(lh_color)

    text_color = TEXT_COLOR
    text_color_string = as_string(text_color)
    text_color_list = as_list(text_color)

    # End Config properties
    # Begin Misc

    trans = (1, 1, 1, 0)
    trans_string = '1, 1, 1, 0'
    trans_list = [1, 1, 1, 0]

    hint_text_color = (0.6705882352941176, 0.6705882352941176, 0.6705882352941176, .1)
    text_base_size = TEXT_BASE_SIZE
    item_row_height = ITEM_ROW_HEIGHT
    board = {}
    tile_inputs = {}

    def build(self):
        return Main()

    def set_board(self, board: classes.Board):
        ...


if __name__ == '__main__':
    SudokuSolverApp().run()
