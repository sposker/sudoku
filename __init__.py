from kivy.graphics.context_instructions import Color
from kivy.graphics.instructions import CanvasBase
from kivy.graphics.vertex_instructions import RoundedRectangle, Rectangle


def as_string(tup):
    """Convert constant color tuples to lists for kivy.properties.ListProperties"""
    try:
        r, g, b, a = tup
    except ValueError:
        a = 1
        r, g, b = tup
    return f'{r}, {g}, {b}, {a}'


def as_list(tup):
    """Convert constant color tuples to lists for kivy.properties.ListProperties"""
    try:
        r, g, b, a = tup
    except ValueError:
        a = 1
        r, g, b = tup
    return [r, g, b, a]


# noinspection PyUnboundLocalVariable
def redraw_canvas(widget, color, corners=False):
    try:
        _color = widget.color
    except AttributeError:
        _color_fg = widget.foreground_color
    dh0, dh1, dh2, _ = color
    if corners:
        radii = [widget.width / 2, widget.width / 2, 0, 0]
    else:
        radii = [widget.width / 2, widget.width / 2, widget.width / 2, widget.width / 2]
    with widget.canvas.before:
        CanvasBase.clear(widget.canvas.before)
        Color(dh0, dh1, dh2)
        widget.rect = Rectangle(size=widget.size,
                                pos=widget.pos,
                                radius=radii)
        try:
            Color(_color[0:2])
        except UnboundLocalError:
            Color(_color_fg[0:2])
    widget.canvas.ask_update()
    try:
        widget.color = _color
    except UnboundLocalError:
        widget.foreground_color = _color_fg


def hide_widget(wid, dohide=True):
    if isinstance(wid, list):
        for w in wid:
            hide_widget(w, dohide=dohide)
    else:
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True
