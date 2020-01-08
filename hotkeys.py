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

    def __call__(self, keycode: (int, str), modifiers: list):
        if modifiers is None:
            modifiers = []

        callback, code = self.resolve_modifiers(keycode[0], sorted(modifiers))
        # TODO: Call with some parameters
        # TODO: get from other module

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
            return self.jump, code
        if mods[0] == 'alt':
            return self.guesses, code
        if mods[0] == 'ctrl':
            return self.into_locks, code
        if code in self.entry:
            return self.enter, code
        if code in self.numpad:
            return self.move, code

    @staticmethod
    def enter(code):
        ...

    def jump(self):
        ...

    def guesses(self):
        ...

    def into_locks(self):
        ...

    def move(self):
        ...


print('_'.join(sorted(['numlock', 'shift', 'alt', 'ctrl', 'shift'])))
