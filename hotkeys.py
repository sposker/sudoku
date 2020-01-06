"""Dictates hotkey behavior.
It is strongly recommended to change your behaviors from CONFIG rather than directly editing this file.
"""


class HotKeyboard:
    """
    mods: numlock, ctrl, alt, shift (only for tab)

    keys: 1-9, numpad1-9, letters with ctrl


    """
    arrows = {n for n in range(273, 277)}
    entry = [n for n in range(49, 58)]
    entrypad = [n for n in range(257, 266)]
    pad_to_nums = {k: v for k, v in zip(entrypad, entry)}

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

    def __call__(self, keycode: (int, str), modifiers: list):
        if modifiers is None:
            modifiers = []

        self.resolve_modifiers(keycode[0], sorted(modifiers))

    def resolve_modifiers(self, code, mods):
        if 'numlock' in mods:
            mods.pop(mods.index('numlock'))
            code = self.pad_to_nums[code]
        if len(mods) != 1:
            return self.jump(code)
        if mods[0] == 'alt':
            return self.guesses(code)
        if mods[0] == 'ctrl':
            return self.move(code, locks=False)

    keystrokes = {
        'up',
        'down',
        'left',
        'right',
    }
    for num in range(1, 10):
        keystrokes.add(str(num))
        keystrokes.add(f'numpad{num}')


print('_'.join(sorted(['numlock', 'shift', 'alt', 'ctrl', 'shift'])))
