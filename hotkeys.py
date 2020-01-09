"""Dictates hotkey behavior.
It is strongly recommended to change your behaviors from CONFIG rather than directly editing this file.
"""


class HotKeyboard:
    """
    mods: numlock, ctrl, alt, shift (only for tab)

    keys: 1-9, numpad1-9, letters with ctrl


    """
    arrows = [n for n in range(273, 277)]
    entry = [n for n in range(49, 58)]
    numpad = [n for n in range(257, 266)]
    pad_to_nums = {k: v for k, v in zip(numpad, entry)}
    special_keys = arrows + entry + numpad
    parent = None  # Only needed for subclass

    def __init__(self):
        self.master = {}
        with open('hotkeys.txt', encoding='utf-8') as f:
            for line in f:
                end = line.index(')')
                keycode = line[2:end]
                code, key = keycode.split(', ')
                key.strip("'")
                key.strip("'")

                self.master[int(code)] = key

                self.moves_table = {
                    # up, down, right, left
                    273: (0, 1),
                    274: (0, -1),
                    275: (1, 0),
                    276: (-1, 0),
                    # numpad 1, 2, 3, 4, 6, 7, 8, 9
                    257: (-1, -1),
                    258: (0, -1),
                    259: (1, -1),
                    260: (-1, 0),
                    262: (1, 0),
                    263: (-1, 1),
                    264: (0, 1),
                    265: (1, 1),
                }
                self.opposites = {  # reversing direction
                    273: 274,
                    274: 273,
                    275: 276,
                    276: 275,
                    257: 265,
                    258: 264,
                    259: 263,
                    260: 262,
                    262: 260,
                    263: 259,
                    264: 258,
                    265: 257,
                }

    def evaluate_input(self, keycode: (int, str), modifiers: list):
        if keycode[0] not in self.special_keys:  # not a hotkey or input
            return None

        if modifiers is None:
            modifiers = []

        callback, args = self.resolve_modifiers(keycode[0], sorted(modifiers))
        return callback(*args)

    def resolve_modifiers(self, code, mods):
        try:
            mods.pop(mods.index('numlock'))
        except ValueError:
            pass
        else:
            if not mods:  # If numlock was popped as the only modifier
                code = self.pad_to_nums[code]
                return self.enter, code

        if mods[:2] == ['alt', 'ctrl']:
            return self.jump, [code]
        if mods[0] == 'alt':
            return self.guesses, [code]
        if mods[0] == 'ctrl':
            return self.into_locks, [code]
        if code in self.entry:
            return self.enter, []
        if code in self.numpad:
            return self.move, [code]
        if code == 9:  # TAB
            try:
                return self.on_tab, [mods[0]]
            except IndexError:
                return self.on_tab, []

    def enter(self, code):
        return code  # Handle this basic case in input class

    def jump(self, code):
        direction = self.moves_table[code]
        tile = self.parent
        tiles = tile.tiles
        _x, _y = tile.grid_position
        dx, dy = direction

        while _x in range(1, 8) and _y in range(1, 8):
            _x += dx
            _y += dy

        edge_tile = tiles[(_x, _y)]
        if edge_tile.locked:
            reverse = self.opposites[code]
            return self.move(reverse)
        return edge_tile

    def guesses(self, code):
        tile = self.parent
        label = tile.guesses.labels[code]
        label.toggle_opacity()
        # TODO
        return tile

    def into_locks(self, code):
        return self.move(code, condition=(False,))

    def move(self, code, condition=('soft', False)):
        direction = self.moves_table[code]
        tile = self.parent
        tiles = tile.tiles

        _x, _y = tile.grid_position
        next_x, next_y = self._calculate_directional_focus(_x, _y, direction)
        _next = tiles[(next_x, next_y)]

        while _next.locked in condition:
            next_x, next_y = self._calculate_directional_focus(next_x, next_y, direction)
            _next = tiles[(next_x, next_y)]

        return _next

    def on_tab(self, *args):  # TODO: soft/hard locks?
        if args:
            return self.get_focus_previous()
        return self.get_focus_next()

    def get_focus_previous(self):
        prev_x, prev_y = self._calculate_prev_focus(*self.parent.grid_position)
        _prev = self.parent.tiles[(prev_x, prev_y)]

        while _prev.locked:
            prev_x, prev_y = self._calculate_prev_focus(prev_x, prev_y)
            _prev = self.parent.tiles[(prev_x, prev_y)]

        return _prev

    def get_focus_next(self):

        next_x, next_y = self._calculate_next_focus(*self.parent.grid_position)
        _next = self.parent.tiles[(next_x, next_y)]

        while _next.locked:
            next_x, next_y = self._calculate_next_focus(next_x, next_y)
            _next = self.parent.tiles[(next_x, next_y)]

        return _next

    @staticmethod
    def _calculate_directional_focus(x, y, delta: (int, int)):
        dx = x + delta[0]
        dy = y + delta[1]

        if dx == -1:
            dx = 8
        elif dx == 9:
            dx = 0
        if dy == -1:
            dy = 8
        elif dy == 9:
            dy = 0

        return dx, dy

    @staticmethod
    def _calculate_prev_focus(x, y):

        dx_prev = x - 1
        dy_prev = y

        if dx_prev == -1:
            dx_prev = 8
            dy_prev = y + 1

        if dy_prev == 9:
            dy_prev = 0

        return dx_prev, dy_prev

    @staticmethod
    def _calculate_next_focus(x, y):

        dx_next = x + 1
        dy_next = y

        if dx_next == 9:
            dx_next = 0
            dy_next = y - 1

        if dy_next == -1:
            dy_next = 8

        return dx_next, dy_next
