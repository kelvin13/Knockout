from math import floor
import bisect

from state import constants

from fonts.interfacefonts import ISTYLES

accent = (1, 0.22, 0.50)

def xhover(self, x, y):
    return self._sdkeys[bisect.bisect(self._subdivisions, x)]

# shapes
def plus_sign(cr, x, y):
    # w = 26
    cr.rectangle(x + 12, y + 8, 2, 10)
    cr.rectangle(x + 8, y + 12, 10, 2)

def minus_sign(cr, x, y):
    # w = 26
    cr.rectangle(x + 8, y + 12, 10, 2)

def downchevron(cr, x, y):
    # w = 24
    cr.move_to(x + 7, y + 10)
    cr.rel_line_to(5, 5)
    cr.rel_line_to(5, -5)

def upchevron(cr, x, y):
    # w = 24
    cr.move_to(x + 7, y + 15)
    cr.rel_line_to(5, -5)
    cr.rel_line_to(5, 5)

def cross(cr, x, y):
    # w = 24
    cr.move_to(x + 8, y + 9)
    cr.rel_line_to(8, 8)
    cr.rel_move_to(0, -8)
    cr.rel_line_to(-8, 8)

def text(x, y, text, font, fontsize=None, align=1, sub_minus=False, upper=False):
    if upper:
        text = text.upper()
    if fontsize is None:
        fontsize = font['fontsize']
    xo = x
    line = []
    for character in text:
        if sub_minus and character == '-':
            character = '–'
        try:
            line.append((font['fontmetrics'].character_index(character), x, y))
            x += (font['fontmetrics'].advance_pixel_width(character)*fontsize + font['tracking'])
        except TypeError:
            line.append((-1, x, y))

    if align == 0:
        dx = (xo - x)/2
        line = [(g[0], g[1] + dx, g[2]) for g in line]
    elif align == -1:
        dx = xo - x
        line = [(g[0], g[1] + dx, g[2]) for g in line]
    
    return font['font'], font['fontsize'], line

def set_fonts(cr, font, fontsize):
    cr.set_font_face(font)
    cr.set_font_size(fontsize)

def show_text(cr, textline):
    * F, T = textline
    set_fonts(cr, * F)
    cr.show_glyphs(T)

class Kookie(object):
    def __init__(self, x, y, width, height):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        
        self._active = None
        
        self._x_right = x + width
        self.y_bottom = y + height

    def _make_sd(self, subdivisions, cap):
        self._subdivisions, self._sdkeys = zip( * subdivisions)
        self._sdkeys += (cap,)
    
    def is_over(self, x, y):
        return self._y <= y <= self.y_bottom and self._x <= x <= self._x_right
    
    def is_over_hover(self, x, y):
        return False
    
    def focus(self, x, y):
        pass
    
    def dpress(self):
        pass
    
    def focus_drag(self, x, y):
        pass
    
    def release(self, action):
        pass
    
    def defocus(self):
        pass
    
    def hover(self, x, y):
        pass
    
    def type_box(self, name, char):
        pass
    
    def bounding_box(self):
        return self._x, self._x_right, self._y, self.y_bottom

class Base_kookie(object):
    def __init__(self, x, y, width, height, font=()):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        
        self._active = None
        
        self._texts = []
        
        if font is not None:
            self.font = ISTYLES[font]
        
        self._x_right = x + width
        self.y_bottom = y + height

    def _make_sd(self, subdivisions, cap):
        self._subdivisions, self._sdkeys = zip( * subdivisions)
        self._sdkeys += (cap,)
    
    def _add_static_text(self, x, y, text, font=None, fontsize=None, upper=False, align=1):
        if font is None:
            font = self.font
        if upper:
            text = text.upper()
        self._texts.append(self._build_line(x, y, text, font, fontsize=fontsize, align=align))

    def _build_line(self, x, y, text, font, fontsize=None, align=1, sub_minus=False):
        if fontsize is None:
            fontsize = font['fontsize']
        xo = x
        line = []
        for character in text:
            if sub_minus and character == '-':
                character = '–'
            try:
                line.append((font['fontmetrics'].character_index(character), x, y))
                x += (font['fontmetrics'].advance_pixel_width(character)*fontsize + font['tracking'])
            except TypeError:
                line.append((-1, x, y))

        if align == 0:
            dx = (xo - x)/2
            line = [(g[0], g[1] + dx, g[2]) for g in line]
        elif align == -1:
            dx = xo - x
            line = [(g[0], g[1] + dx, g[2]) for g in line]
        
        return line
            
    def is_over(self, x, y):
        return self._y <= y <= self.y_bottom and self._x <= x <= self._x_right
    
    def is_over_hover(self, x, y):
        return False


    def focus(self, x, y):
        pass
    def dpress(self):
        pass
    def focus_drag(self, x, y):
        pass
    def release(self, action):
        pass
    def defocus(self):
        pass
    def hover(self, x, y):
        pass

    
    def type_box(self, name, char):
        pass
    
    def _render_fonts(self, cr):
        cr.set_font_size(self.font['fontsize'])
        cr.set_font_face(self.font['font'])
    
    def bounding_box(self):
        return self._x, self._x_right, self._y, self.y_bottom


class Menu(Base_kookie):
    def __init__(self, x, y, width, item_height, signals=None):

        # 'centers' menu
        ht = item_height*len(signals)
        k = constants.window.get_k()
        if y > k/2:
            signals = tuple(reversed(signals))
            y -= ht
            
        if y < 0:
            y = 0
        elif y + ht > k:
            y = k - ht

        Base_kookie.__init__(self, x, y, width, ht)

        self._item_height = item_height
        self._signals = signals
        
        self._construct()
        
    def _construct(self):
        # build menu
        y = self._y
        for signal, text in self._signals:
            self._add_static_text(self._x + 10, y + self._item_height - 11, text )
            y += self._item_height

    def _target(self, y):
        y = (y - self._y)/self._item_height
        return int(floor(y))
            
    def press(self, y):
        i = self._target(y)
        return self._signals[i]

    def hover(self, y):
        return self._target(y)

    def draw(self, cr, hover=None):
        self._render_fonts(cr)
        
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.rectangle(self._x, self._y, self._width, self._height)
        cr.fill()
        cr.set_source_rgba(1, 1, 1, 1)
        cr.rectangle(self._x + 1, self._y + 1, self._width - 2, self._height - 2)
        cr.fill()
        
        for i, label in enumerate(self._texts):
            if i == hover:
                cr.set_source_rgb( * accent)
                cr.rectangle(self._x, self._y + i*self._item_height, self._width, self._item_height)
                cr.fill()
                cr.set_source_rgb(1, 1, 1)
            else:
                cr.set_source_rgb(0.1,0.1,0.1)
            cr.show_glyphs(label)

