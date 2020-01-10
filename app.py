from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics.context_instructions import Color
from kivy.graphics.instructions import CanvasBase
from kivy.uix.behaviors import ButtonBehavior, ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

from classes import Board
from database import Database
from hotkeys import HotKeyboard
from __init__ import *
import re
import threading

DARK_HIGHLIGHT = (0.1568627450980392, 0.16862745098039217, 0.18823529411764706, 1)  # Darkest Gray
BACKGROUND_COLOR = (0.18823529411764706, 0.19215686274509805, 0.21176470588235294, 1)  # Dark gray
ELEMENT_COLOR = (0.21176470588235294, 0.2235294117647059, 0.25882352941176473, 1)  # Medium Gray
LIGHT_HIGHLIGHT = (0.39215686274509803, 0.396078431372549, 0.41568627450980394, 1)  # Lighter Gray
TEXT_COLOR = (0.6705882352941176, 0.6705882352941176, 0.6705882352941176, 1)  # Lightest Gray
APP_COLORS = [DARK_HIGHLIGHT, BACKGROUND_COLOR, ELEMENT_COLOR, LIGHT_HIGHLIGHT, TEXT_COLOR]

ITEM_ROW_HEIGHT = 72
TEXT_BASE_SIZE = 30

Window.size = (round(1440 * 1.618) / 2, 1440 / 2)

Window.borderless = True


class TaskButton(ButtonBehavior, Image):
    """Callback based buttons for logical execution"""

    buttons = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_once(self.register_callbacks)  # ensure app is running before trying to resolve references

    def register_callbacks(self, _):
        """Assign callbacks to buttons *after* app has been built"""
        app = App.get_running_app()
        self.buttons['Solve'] = app.root.start_second_thread
        self.buttons['Reset'] = app.reset
        self.buttons['Open Puzzle'] = app.root.puzzle_picker
        self.buttons['Random'] = PuzzlePicker.random
        self.buttons['Easy'] = PuzzlePicker.easy
        self.buttons['Intermediate'] = PuzzlePicker.med
        self.buttons['Expert'] = PuzzlePicker.hard
        self.buttons['Hint'] = app.find_hint
        self.buttons['Show Hotkeys'] = HotkeysDisplay.show

    def task_button_callback(self, button_text):
        try:
            callback = self.buttons[button_text]
            callback()
        except AttributeError:
            print(f'No callback present for <{button_text}>.')
        except KeyError:
            print(f'No key present for <{button_text}>.')


class TaskButtonLayout(FloatLayout):
    """Layout for single buttons and names"""

    button_text = StringProperty()
    image_path = StringProperty()


class ToggleLayout(FloatLayout):
    """Layout that holds pairs of toggle buttons"""

    pair_name = StringProperty()
    toggle_on_cb = ObjectProperty()
    toggle_off_cb = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.guides_on = NineBy.instance.guides_on
        self.guides_off = NineBy.instance.guides_off

    @staticmethod
    def inspections_on():
        app = App.get_running_app()
        setattr(app, 'inspections', True)
        conflicts = set()
        for tile in app.board.tiles.values():
            _conflicts = app.board.validate(tile)
            conflicts = conflicts | _conflicts

        if None in conflicts:
            conflicts.remove(None)

        for pos in conflicts:
            tile = Tile.tiles[pos]
            tile.locked = False if tile.locked == 'soft' else 'hard'
            tile.label.color = (.6, .1, .1, 1)
        Tile.conflicts = conflicts

    @staticmethod
    def inspections_off():
        app = App.get_running_app()
        setattr(app, 'inspections', False)
        if Tile.conflicts:
            for pos in Tile.conflicts:
                tile = Tile.tiles[pos]
                tile.label.color = app.text_color
        Tile.conflicts = None


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
    """Background for entry and value label"""


class GuideLabel(Label):
    """Acts as guide/hightlight around tile"""

    def __init__(self, pos, **kwargs):
        super().__init__(**kwargs)
        self.grid_position = pos


class Tile(RelativeLayout):
    """Tile holding various widgets for sudoku tile functionality"""

    tiles = {}
    conflicts = None

    def __init__(self, position, **kwargs):
        self.locked = False
        self.grid_position = position
        if position[0] in [0, 8] or position[1] in [0, 8]:
            self.on_border = True
        else:
            self.on_border = False
        super().__init__(**kwargs)

        Tile.tiles[self.grid_position] = self

        self.background = TileBackground(size_hint=(.95, .95))
        self.add_widget(self.background)

        self.input = TileInput(size_hint=(.95, .95),
                               pos_hint={'y': -0.1375}
                               )
        self.input.bind(focus=lambda x, y: self.input.on_focus)
        self.add_widget(self.input)

        self.label = TileLabel(size_hint=(.95, .95),
                               # pos_hint={'x': 0.025, 'y': 0},
                               )
        self.add_widget(self.label)

        self.guesses = TileGuesses(size_hint=(.95, .95),
                                   # pos_hint={'x': 0.025, 'y': 0.025},
                                   )
        self.add_widget(self.guesses)

    def __str__(self):
        return f'Tile object at position ({self.grid_position[0]}, {self.grid_position[1]}).'


class TileGuesses(GridLayout):
    """Holds guesses"""

    def __init__(self, **kwargs):
        self.labels = {}
        super().__init__(**kwargs)
        for i in [7, 8, 9, 4, 5, 6, 1, 2, 3]:
            _label = Label(text=str(i),
                           color=TEXT_COLOR,
                           opacity=0)
            self.add_widget(_label)
            self.labels[i+48] = _label  # +48 matches 1-9 keycodes
            self.labels[i+256] = _label  # +256 matches numpad keycodes•

    def toggle_opacity(self, val):
        label = self.labels[int(val)]
        if label.opacity < .5:
            label.opacity = 1.
        else:
            label.opacity = 0.


class TileInput(TextInput, HotKeyboard):
    """Widget that allows setting values"""

    pat = re.compile('[^1-9]')
    app = None

    def __init__(self, **kwargs):
        self.locked = False
        if not self.app:
            self.app = App.get_running_app()
        super().__init__(**kwargs)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):

        args = window, keycode, text, modifiers
        result = self.evaluate_input(keycode, modifiers)
        try:
            result.input.focus = True
        except AttributeError:  # We didn't return a tile; either input or unknown keypress
            return super().keyboard_on_key_down(*args)
        else:
            print(result)
            return True  # Keypress was consumed

    def on_focus(self, _, value):
        if value:
            self.opacity = 1
            self.parent.label.text = '__'
            self.parent.label.pos_hint = {'x': 0, 'y': -.2}
            self._trigger_guides()
        else:
            self.opacity = 0
            self.parent.label.pos_hint = {'x': 0, 'y': 0}

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if len(self.text):
            self.text = ''
        s = re.sub(pat, '', substring)
        return super(TileInput, self).insert_text(s, from_undo=from_undo)

    def set_text(self, text):
        setattr(self.parent.label, 'text', text)
        if text:
            for label in self.parent.guesses.labels.values():
                label.opacity = 0
            self.locked = self.parent.locked = 'soft'
        conflicts = self.app.update_board(self.parent.grid_position, self.text)
        if conflicts:
            Tile.conflicts = conflicts
            for pos in conflicts:
                tile = Tile.tiles[pos]
                tile.label.color = .6, .1, .1, 1

    def _unbind_keyboard(self):
        self.set_text(self.text)
        super()._unbind_keyboard()

        if Tile.conflicts:
            print(Tile.conflicts)
            to_remove = {self.app.resolve_conflicts(pos) for pos in Tile.conflicts}
            for elem in to_remove:
                if elem in Tile.conflicts:
                    Tile.conflicts.remove(elem)

    def _trigger_guides(self):
        NineBy.instance.trigger_guides(self.parent.grid_position)

    def get_focus_next(self):
        return self.hotkey_next_focus()

    def get_focus_previous(self):
        return self.hotkey_focus_previous()


class TileLabel(Label):
    """Label displaying tiles' value"""


class ThreeBy(RelativeLayout):
    """3x3 grid of tiles"""

    def __init__(self, grid_pos, **kwargs):
        self.grid_pos = grid_pos
        self._h_offset, self._v_offset = 3 * grid_pos[0], 3 * grid_pos[1]
        super().__init__(**kwargs)

    def make_tiles(self, **_):
        for vert in range(3):
            for horiz in range(3):
                coords = (self._h_offset + horiz, self._v_offset + vert)

                tile = Tile(coords,
                            size_hint=(.33, .33),
                            pos_hint={'x': horiz / 3, 'y': vert / 3},
                            )

                self.add_widget(tile)

    def populate_tiles(self):
        app = App.get_running_app()
        for tile in self.children:
            try:
                value = app.board[tile.grid_position]
            except KeyError:
                value = None

            if value:
                tile.label.text = str(value)
                tile.label.underline = True

                tile.input.locked = 'hard'
                tile.input.disabled = True
                tile.locked = 'hard'


class NineBy(FloatLayout):
    """9x9 board containing 9 3x3 grids"""

    instance = None

    def __init__(self, **kw):
        super().__init__(**kw)
        NineBy.instance = self
        self.show_guides = False
        self._guides = set()
        self.hint_size = 1 / 3 - .01
        self.guide_tiles = {}
        self.rows = {}
        self.cols = {}
        self.boxes = {}

        self._draw_guides()
        self.construct()

    def construct(self):
        self._fill()
        for widget in self.children:
            try:
                widget.populate_tiles()
            except AttributeError:
                pass
        groups = self._create_guide_groups()
        self._set_guide_groups(*groups)

    @staticmethod
    def _create_guide_groups():

        c = [set() for _ in range(9)]  # We need to define this twice or we'll get the same values in both dicts
        r = [set() for _ in range(9)]  # Could also use deepcopy but this is simple

        rows = {k: v for k, v in zip(range(9), r)}
        cols = {k: v for k, v in zip(range(9), c)}
        boxes = {}

        for x in range(3):
            i, j, k = [x * 3 + _x for _x in range(3)]  # groups of 3 consecutive numbers
            for y in range(3):
                a, b, c = [y * 3 + _y for _y in range(3)]

                _boxes = set()

                for h in [i, j, k]:
                    for v in [a, b, c]:
                        _boxes.add((h, v))

                boxes[3 * x + y] = _boxes

        return rows, cols, boxes

    def _draw_guides(self):

        for i in range(9):
            for j in range(9):
                (qx, rx), (qy, ry) = divmod(i, 3), divmod(j, 3)
                w = GuideLabel((i, j),
                               size_hint=[(2 / 3 - self.hint_size) / 3 for _ in range(2)],
                               pos_hint={'x': ((i - (qx + rx) * .025) / 9), 'y': ((j - (qy + ry) * .025) / 9)},
                               opacity=0,
                               )
                self.guide_tiles[(i, j)] = w
                self.add_widget(w)

    def _fill(self):
        for vert in range(3):
            for horiz in range(3):
                w = ThreeBy((horiz, vert))
                self.add_widget(w)
                w.make_tiles()
                w.size_hint = [self.hint_size for _ in range(2)]

                w.pos_hint = {'x': self._find_offset(horiz), 'y': self._find_offset(vert)}

    def _find_offset(self, n: int) -> float:
        return ((n * 1.0025 + 2 * ((1 / 3 - self.hint_size) * 2 / 3)) + 0.01 * (1 - n)) / 3

    def _set_guide_groups(self, rows, cols, boxes):

        def linear(_dict, index):
            for k, v in _dict.items():
                for pos, tile in self.guide_tiles.items():
                    if pos[index] == k:
                        v.add(tile)
            return _dict

        self.rows = linear(rows, 1)
        self.cols = linear(cols, 0)

        for key, values in boxes.items():
            tiles = {self.guide_tiles[coord] for coord in values}
            for coord in values:
                self.boxes[coord] = tiles

    # noinspection PyMethodMayBeStatic
    def _recolor_tile(self, tile, value):
        tile.opacity = value

    def _trigger_guides(self, pos):

        highlights = self.cols[pos[0]] | self.rows[pos[1]] | self.boxes[pos]

        for guide in self._guides - highlights:
            self._recolor_tile(guide, 0)

        for guide in highlights - self._guides:
            self._recolor_tile(guide, 1)

        self._guides = highlights

    def guides_on(self):
        self.show_guides = True

    def guides_off(self):
        self.show_guides = False
        for tile in self._guides:
            self._recolor_tile(tile, 0)
        self._guides = set()

    def trigger_guides(self, pos: (int, int)):
        if self.show_guides:
            self._trigger_guides(pos)


class Main(FloatLayout):
    """Main screen"""

    stop = threading.Event()

    def start_second_thread(self):
        threading.Thread(target=self.second_thread).start()

    def second_thread(self):
        Clock.schedule_once(self.start_test, 0)
        App.get_running_app().slow_solve()
        self.stop_test()

    def start_test(self, *args):
        print('Starting slow solve')

    @mainthread
    def stop_test(self):
        print('Solved!')
        for tile in Tile.tiles.values():
            tile.label.color = (.1, .6, .1, 1)

    @mainthread
    def update_values(self):
        app = App.get_running_app()
        board = app.board
        for pos, _tile in board.tiles.items():
            tile = Tile.tiles[pos]
            tile.label.text = str(_tile.value) if _tile.value else ''

    @staticmethod
    def puzzle_picker():
        PuzzlePicker.instance = Factory.PuzzlePicker()
        PuzzlePicker.instance.open()


class PuzzleRandomLayout(FloatLayout):
    """Layout for random choice options"""


class PuzzlePicker(Popup):
    """Popup for choosing puzzles"""

    instance = None

    @staticmethod
    def random():
        return PuzzlePicker.instance.real_random()

    @staticmethod
    def easy():
        return PuzzlePicker.instance.real_random(difficulty='easy')

    @staticmethod
    def med():
        return PuzzlePicker.instance.real_random(difficulty='medium')

    @staticmethod
    def hard():
        return PuzzlePicker.real_random(difficulty='hard')

    @staticmethod
    def real_random(difficulty=None):
        app = App.get_running_app()
        puzzle = app.db.random_puzzle(difficulty)
        app.board = Board(puzzle=puzzle)
        NineBy.instance.children.clear()
        NineBy.instance.construct()
        PuzzlePicker.instance.dismiss()


class HotkeysDisplay(Popup):
    """Static widget displayinging availible hotkeys"""

    def show(self):
        Factory.HotkeysPopup().open()

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

    # End Color properties
    # Begin Misc

    trans = (1, 1, 1, 0)
    trans_string = '1, 1, 1, 0'
    trans_list = [1, 1, 1, 0]
    text_size = TEXT_BASE_SIZE

    hint_text_color = (0.6705882352941176, 0.6705882352941176, 0.6705882352941176, .1)
    board = {}
    tile_inputs = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inspections = False
        self.solve_iter_count = 0
        self.db = Database()
        self.board = Board(puzzle=self.db.blank_puzzle)

    def build(self):
        return Main()

    def _set_board_value(self, pos, value):
        tile = self.board.tiles[pos]
        try:
            tile.value = int(value)
        except ValueError:
            tile.value = None
        return tile

    def update_board(self, pos, value):
        tile = self._set_board_value(pos, value)

        if self.inspections:
            return self.board.validate(tile)

    def resolve_conflicts(self, pos):
        tile = self.board.tiles[pos]
        conflicts = self.board.validate(tile)
        if not conflicts:
            print('not conflicts')
            label = Tile.tiles[pos].label
            label.color = self.text_color
            return pos

    def solve(self):
        self.board.solve()
        for pos, tile in self.board.tiles.items():
            val = tile.value
            Tile.tiles[pos].label.text = str(val)
            Tile.tiles[pos].label.color = (.1, .6, .1, 1)
            Tile.tiles[pos].input.text = str(val)

    def slow_solve(self):

        tiles = self.board.reset()
        self.solve_iter_count = 0
        self._slow_solve(tiles)
        print(self.solve_iter_count)

    def find_hint(self):
        pos = self.board.generate_hint()
        tile = Tile.tiles[pos]
        tile.label.color = [(.6, .3, .3, 1)]

    def _slow_solve(self, tiles):

        tile = tiles.pop()
        label = Tile.tiles[tile.position].label
        label.color = (.1, .6, .1, 1)

        for i in range(1, 10):
            self.root.update_values()
            self.solve_iter_count += 1
            print(i)  # For whatever reason, printing gives the window time to update itself, so don't remove this

            tile.value = i

            if not self.board.validate(tile):
                label.color = self.text_color
                try:
                    x = self._slow_solve(tiles)
                except IndexError:  # Empty list
                    return True
                else:
                    if x:
                        return x
                    else:
                        label.color = (.1, .6, .1, 1)

        else:
            tile.value = None
            tiles.append(tile)

    def reset(self):
        self.board.reset()
        for pos, tile in self.board.tiles.items():
            val = tile.value
            Tile.tiles[pos].label.text = str(val) if val else ''
            Tile.tiles[pos].label.color = self.text_color
            Tile.tiles[pos].input.text = ''

    def on_stop(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        self.root.stop.set()


if __name__ == '__main__':
    # Factory.register('PuzzlePicker', cls=PuzzlePicker)
    SudokuSolverApp().run()
