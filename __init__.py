from kivy.graphics.context_instructions import Color
from kivy.graphics.instructions import CanvasBase
from kivy.graphics.vertex_instructions import Rectangle


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
