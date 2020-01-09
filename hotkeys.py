"""Dictates hotkey behavior.
It is strongly recommended to change your behaviors from CONFIG rather than directly editing this file.
"""


class HotKeyboard:
    """
    mods: numlock, ctrl, alt, shift

    keys: 1-9, numpad1-9, letters with ctrl, tab


    """
    arrows = [n for n in range(273, 277)]
    entry = [n for n in range(49, 58)]
    numpad = [n for n in range(257, 266)]
    pad_to_nums = {k: v for k, v in zip(numpad, entry)}
    special_keys = arrows + entry + numpad + [9]
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

        print(*keycode, *modifiers)

        callback, args = self.resolve_modifiers(keycode[0], sorted(modifiers))
        return callback(args)

    def resolve_modifiers(self, code, mods):
        mods = set(mods) & {'shift', 'numlock', 'ctrl', 'alt'}  # sanitize scroll lock, caps lock, etc.
        if 'numlock' in mods:
            try:
                code = self.pad_to_nums[code]
            except KeyError:
                pass

        if 'alt' in mods and code in self.entry:
            callback = self.guesses
        elif code in self.entry:
            callback = self.enter
        elif code in self.arrows or code in self.moves_table:
            if 'ctrl' in mods and 'shift' in mods:
                callback = self.jump
            elif 'ctrl' in mods:
                callback = self.into_locks
            else:
                callback = self.move
        elif code == 9:
            if 'shift' in mods:
                callback = self.hotkey_focus_previous
            else:
                callback = self.hotkey_next_focus
        else:
            print('Returning do_pass.')
            callback = self.do_pass

        return callback, code

        # try:
        #     mods.pop(mods.index('numlock'))
        #     code = self.pad_to_nums[code]
        # except ValueError:
        #     if not mods:
        #         if code in {261, 256}:
        #             return self.handle_special, [code]
        #         elif code in self.numpad or code in self.arrows:
        #             return self.move, [code]
        #         elif code == 9:
        #             return self.on_tab, [code]
        #         return self.enter, [code]
        # except KeyError:
        #     return self.move, [code]
        # else:
        #     if not mods:  # If numlock was popped as the only modifier
        #         return self.enter, [code]
        #
        # if mods[:2] == ['ctrl', 'shift']:
        #     return self.jump, [code]
        # if mods[0] == 'alt':
        #     return self.guesses, [code]
        # if mods[0] == 'ctrl':
        #     return self.into_locks, [code]
        # if code in self.entry:
        #     return self.enter, []
        # if code in self.numpad:
        #     return self.move, [code]
        # if code == 9:  # TAB
        #     print('code=9')
        #     try:
        #         return self.on_tab, [mods[0]]
        #     except IndexError:
        #         return self.on_tab, []
        # else:
        #     print('edge_case')
        #     return self.do_pass, [code]

    def enter(self, code):
        return code  # Handle this basic case in input class

    def jump(self, code):
        direction = self.moves_table[code]
        tile = self.parent
        tiles = tile.tiles
        _x, _y = tile.grid_position
        dx, dy = direction

        conditons = {'x': [0, 8],
                     'y': [0, 8]}

        if _x == 0 and dx == 0:
            conditons['x'] = [8]
        elif _x == 8 and dx == 0:
            conditons['x'] = [0]
        if _y == 0 and dy == 0:
            conditons['y'] = [8]
        elif _y == 8 and dy == 0:
            conditons['y'] = [0]

        while True:
            _x += dx
            _y += dy
            try:
                tile = tiles[(_x, _y)]
            except KeyError:
                return tile
            else:
                if _x in conditons['x'] or _y in conditons['y']:
                    return tile

    def guesses(self, code):
        tile = self.parent
        try:
            tile.guesses.toggle_opacity(code)
        except KeyError:
            return None
        return tile

    def into_locks(self, code):
        return self.move(code, condition=('soft', False,))

    def move(self, code, condition=(False,)):
        direction = self.moves_table[code]
        tile = self.parent
        tiles = tile.tiles

        _x, _y = tile.grid_position
        next_x, next_y = self._calculate_directional_focus(_x, _y, direction)
        _next = tiles[(next_x, next_y)]

        while _next.locked not in condition:

            next_x, next_y = self._calculate_directional_focus(next_x, next_y, direction)
            _next = tiles[(next_x, next_y)]

        return _next

    def hotkey_focus_previous(self, _):
        prev_x, prev_y = self._calculate_prev_focus(*self.parent.grid_position)
        _prev = self.parent.tiles[(prev_x, prev_y)]

        while _prev.locked:
            prev_x, prev_y = self._calculate_prev_focus(prev_x, prev_y)
            _prev = self.parent.tiles[(prev_x, prev_y)]

        return _prev

    def hotkey_next_focus(self, _):

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

    def do_pass(self, code):
        return code

    def handle_special(self, code):
        print(f'Special: {code}')