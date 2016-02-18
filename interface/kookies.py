import bisect
from math import pi
from itertools import chain

from style.styles import ISTYLES
from edit.paperairplanes import interpret_float, interpret_int, interpret_rgba, pack_binomial, read_binomial
from interface.base import Base_kookie, accent, xhover
from interface import menu

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

class Button(Base_kookie):
    def __init__(self, x, y, width, height, callback=None, string='', params=() ):
        Base_kookie.__init__(self, x, y, width, height, font=('strong',))
        
        self._callback = callback
        self._params = params
#        self._string = string
        
        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._add_static_text(x + width/2, self._y_bottom - self._height/2 + 5, string, align=0)
    
    def focus(self, x, y):
        self._active = 1
    
    def release(self, action=True):
        self._active = None
        if action:
            self._callback( * self._params)

    def hover(self, x, y):
        return 1

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        if self._active:
            cr.set_source_rgb( * accent)

            radius = 5
            y1, y2, x1, x2 = self._y, self._y_bottom, self._x, self._x_right
            cr.arc(x1 + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
            cr.arc(x2 - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
            cr.arc(x2 - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
            cr.arc(x1 + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
            cr.close_path()

            cr.fill()

            cr.set_source_rgb(1,1,1)
            
        elif hover[1]:
            cr.set_source_rgb( * accent)

        else:
            cr.set_source_rgb(0,0,0)
        cr.show_glyphs(self._texts[0])

class Checkbox(Base_kookie):
    def __init__(self, x, y, width, callback, params = (), value_acquire=None, before=lambda: None, after=lambda: None, name=''):
        Base_kookie.__init__(self, x, y, width, 20, font=('label',))

        self._BEFORE = before
        self._AFTER = after
        self._callback = callback
        self._params = params
        self._value_acquire = value_acquire
        self._ACQUIRE_REPRESENT()
        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT

        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._add_static_text(self._x + 20, self._y_bottom - 5, name, align=1)

    def _ACQUIRE_REPRESENT(self):
        self._STATE = self._value_acquire( * self._params)

    def focus(self, x, y):
        self._BEFORE()
        self._callback(not self._STATE, * self._params)
        self._ACQUIRE_REPRESENT()
        self._AFTER()

    def hover(self, x, y):
        return 1

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
            
        if hover[1]:
            cr.set_source_rgb(0,0,0)
            cr.show_glyphs(self._texts[0])

        else:
            cr.set_source_rgba(0,0,0, 0.6)
            cr.show_glyphs(self._texts[0])

        cr.arc(self._x + 6, self._y_bottom - 9, 6, 0, 2*pi)
        cr.fill()
        if not self._STATE:
            cr.set_source_rgb(1, 1, 1)
            cr.arc(self._x + 6, self._y_bottom - 9, 4.5, 0, 2*pi)
            cr.fill()


class Tabs(Base_kookie):
    def __init__(self, x, y, width, height, default=0, callback=None, signals=() ):
        Base_kookie.__init__(self, x, y, width, height, font=('strong',))
        self._signals, self._strings = zip( * signals )
        
        self._callback = callback
        
        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._active = default
        
        self._construct()
    
    def _construct(self):
        self._button_width = self._width/len(self._strings)
        self._x_left = []
        xo = self._x
        for string in self._strings:
            self._add_static_text(xo + self._button_width/2, self._y_bottom - self._height/2 + 5, string, align=0)
            self._x_left.append(int(round(xo)))
            xo += self._button_width

    def _target(self, x):
        return bisect.bisect(self._x_left, x) - 1

    def focus(self, x, y):
        self._active = self._target(x)
        self._callback(self._signals[self._active])

    def hover(self, x, y):
        return self._target(x)

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        for i, button in enumerate(self._x_left):
            if i == self._active:
                cr.set_source_rgb( * accent)

                radius = 5
                y1, y2, x1, x2 = self._y, self._y_bottom, button, button + int(round(self._button_width))
                cr.arc(x1 + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
                cr.arc(x2 - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
                cr.arc(x2 - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
                cr.arc(x1 + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
                cr.close_path()

                cr.fill()

                cr.set_source_rgb(1,1,1)
                
            elif i == hover[1]:
                cr.set_source_rgb( * accent)

            else:
                cr.set_source_rgb(0,0,0)
            cr.show_glyphs(self._texts[i])

class Heading(Base_kookie):
    def __init__(self, x, y, width, height, text, font=('title',), fontsize=None, upper=False):
        Base_kookie.__init__(self, x, y, width, height, font=font)
        
        if fontsize is None:
            fontsize = self.font['fontsize']
        
        self._add_static_text(self._x, self._y + fontsize, text, fontsize=fontsize, upper=upper)
    
    def is_over(self, x, y):
        return False
        
    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        cr.set_source_rgb(0,0,0)
        cr.rectangle(self._x, self._y_bottom - 2, self._width, 2)
        cr.fill()
        cr.show_glyphs(self._texts[0])


class Blank_space(Base_kookie):
    def __init__(self, x, y, width, callback, value_acquire, params = (), before=lambda: None, after=lambda: None, name=''):
        self._params = params
        self._BEFORE = before
        self._AFTER = after
        
        Base_kookie.__init__(self, x, y, width, 28)

        self._callback = callback
        self._value_acquire = value_acquire
        
        self._set_text_bounds()
        self._text_width = self._text_right - self._text_left
        
        self._SYNCHRONIZE()

        self._domain = lambda k: k
        self._name = name
        
        self.is_over_hover = self.is_over
        
        # cursors
        self._i = len(self._LIST) - 1
        self._j = self._i
        
        # build static texts
        self._add_static_text(self._x, self._y + 40, self._name, font=ISTYLES[('label',)] , upper=True)
        
        self._resting_bar_color = (0, 0, 0, 0.4)
        self._active_bar_color = (0, 0, 0, 0.8)
        self._resting_text_color = (0, 0, 0, 0.6)
        self._active_text_color = (0, 0, 0, 1)
        
        self._scroll = 0
    
    def _set_text_bounds(self):
        self._text_left = self._x
        self._text_right = self._x_right

    def _ACQUIRE_REPRESENT(self):
        self._VALUE = self._value_acquire( * self._params)
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

    def _SYNCHRONIZE(self):
        self._ACQUIRE_REPRESENT()
        self._PREV_VALUE = self._VALUE

    def _stamp_glyphs(self, glyphs):
        self._template = self._build_line(self._text_left, self._y + self.font['fontsize'] + 5, glyphs, self.font)
        
    def is_over(self, x, y):
        return self._y <= y <= self._y_bottom and self._x - 10 <= x <= self._x_right + 10

    def _entry(self):
        return ''.join(self._LIST[:-1])
    
    # scrolling function
    def _center_j(self):
        position = self._template[self._j][1] - self._text_left
        if position + self._scroll > self._text_width:
            self._scroll = -(position - self._text_width)
        elif position + self._scroll < 0:
            self._scroll = -(position)

    # typing
    def type_box(self, name, char):
        changed = False
        output = None
        
        if name in ['BackSpace', 'Delete']:
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                del self._LIST[self._i : self._j]
                changed = True
                self._j = self._i
                
            elif name == 'BackSpace':
                if self._i > 0:
                    del self._LIST[self._i - 1]
                    changed = True
                    self._i -= 1
                    self._j -= 1
            else:
                if self._i < len(self._LIST) - 2:
                    del self._LIST[self._i]
                    changed = True

        elif name == 'Left':
            if self._i > 0:
                self._i -= 1
                self._j = self._i
        elif name == 'Right':
            if self._i < len(self._LIST) - 1:
                self._i += 1
                self._j = self._i
        elif name == 'Home':
            self._i = 0
            self._j = 0
        elif name == 'End':
            self._i = len(self._LIST) - 1
            self._j = len(self._LIST) - 1

        elif name == 'All':
            self._i = 0
            self._j = len(self._LIST) - 1
        
        elif name == 'Paste':
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                del self._LIST[self._i : self._j]
                self._j = self._i
            # take note that char is a LIST now
            self._LIST[self._i:self._i] = char
            changed = True
            self._i += len(char)
            self._j = self._i
        
        elif name == 'Copy':
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                
                output = ''.join(self._LIST[self._i : self._j])
        
        elif name == 'Cut':
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                output = ''.join(self._LIST[self._i : self._j])
                del self._LIST[self._i : self._j]
                changed = True
                self._j = self._i

        elif char is not None:
            # delete selection
            if self._i != self._j:
                # sort
                if self._i > self._j:
                    self._i, self._j = self._j, self._i
                del self._LIST[self._i : self._j]
                self._j = self._i
            self._LIST[self._i:self._i] = [char]
            changed = True
            self._i += 1
            self._j += 1
        
        if changed:
            self._stamp_glyphs(self._LIST)
        
        self._center_j()
        
        return output

    # target glyph index
    def _target(self, x):
        x -= self._scroll
        
        i = bisect.bisect([g[1] for g in self._template[:-1]], x)
        if i > 0 and x - self._template[i - 1][1] < self._template[i][1] - x:
            i -= 1
        return i

    def focus(self, x, y):
        self._active = True
        
        # clip to edges of visible text
        if x < self._text_left:
            self._i = self._target(self._text_left)
            # inch left or right
            if self._template[self._i][1] > self._text_left:
                self._i -= 1
        elif x > self._text_right:
            self._i = self._target(self._text_right)
            if self._template[self._i][1] < self._text_right and self._i < len(self._template) - 1:
                self._i += 1
        else:
            self._i = self._target(x)
        self._j = self._i
        
        self._center_j()

    def focus_drag(self, x, y):
        j = self._target(x)
        
        # force redraw if cursor moves
        if self._j != j:
            self._j = j
            self._center_j()
            return True
        else:
            return False

    def defocus(self):
        self._active = None
        self._dropdown_active = False
        self._scroll = 0
        # dump entry
        self._VALUE = self._entry()
        if self._VALUE != self._PREV_VALUE:
            self._BEFORE()
            self._callback(self._domain(self._VALUE), * self._params)
            self._SYNCHRONIZE()
            self._AFTER()
        else:
            return False
        return True

    def hover(self, x, y):
        return 1
    # drawing
    def _sup_draw(self, cr, hover):
        pass
    
    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        self._sup_draw(cr, hover=hover)
        
        if hover[0] is not None:
            resting_bar_color = self._active_bar_color
        else:
            resting_bar_color = self._resting_bar_color
        active_bar_color = self._active_bar_color
        resting_text_color = self._resting_text_color
        active_text_color = self._active_text_color
            
        fontsize = round(self.font['fontsize'])
        
        cr.rectangle(self._text_left - 1, self._y, self._text_width + 2, self._height)
        cr.clip()
        
        if self._active:
            cr.set_source_rgba( * active_text_color)
        else:
            cr.set_source_rgba( * resting_text_color)
        
        cr.save()
        cr.translate(round(self._scroll), 0)
        
        # don't print the cap glyph
        cr.show_glyphs(self._template[:-1])
        
        if self._active:
            # print cursors
            cr.set_source_rgb( * accent)
            cr.rectangle(round(self._template[self._i][1] - 1), 
                        self._y + 5, 
                        2, 
                        fontsize)
            cr.rectangle(round(self._template[self._j][1] - 1), 
                        self._y + 5, 
                        2, 
                        fontsize)
            cr.fill()
            
            # print highlight
            if self._i != self._j:
                cr.set_source_rgba(0, 0, 0, 0.1)
                # find leftmost
                if self._i <= self._j:
                    root = self._template[self._i][1]
                else:
                    root = self._template[self._j][1]
                cr.rectangle(root, 
                        self._y + 5,
                        abs(self._template[self._i][1] - self._template[self._j][1]),
                        fontsize)
                cr.fill()
        
        cr.restore()
        cr.reset_clip()
                
        if self._name is not None:
            cr.move_to(self._x, self._y + self.font['fontsize'] + 5)
            cr.set_font_size(11)
            # print label
            for label in self._texts:
                cr.show_glyphs(label)
        
        if self._active:
            cr.set_source_rgba( * active_bar_color)
        else:
            cr.set_source_rgba( * resting_bar_color)
        cr.rectangle(self._text_left, self._y + fontsize + 10, self._text_width, 1)
        cr.fill()

#########

class Numeric_field(Blank_space):
    def __init__(self, x, y, width, callback, value_acquire, params=(), before=lambda: None, after=lambda: None, name=None):
        Blank_space.__init__(self, x, y, width, callback, value_acquire, params, before, after, name)
        self._domain = interpret_float

    def _stamp_glyphs(self, text):
        self._template = self._build_line(self._text_left, self._y + self.font['fontsize'] + 5, text, self.font, sub_minus=True)

    def _ACQUIRE_REPRESENT(self):
        self._VALUE = str(self._value_acquire( * self._params))
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

class Integer_field(Numeric_field):
    def __init__(self, x, y, width, callback, value_acquire, params=(), before=lambda: None, after=lambda: None, name=None):
        Numeric_field.__init__(self, x, y, width, callback, value_acquire, params, before, after, name)
        self._domain = interpret_int

class Enumerate_field(Numeric_field):
    def __init__(self, x, y, width, callback, value_acquire, params=(), before=lambda: None, after=lambda: None, name=None):
        Blank_space.__init__(self, x, y, width, callback, value_acquire, params, before, after, name)
        self._domain = lambda k: set([interpret_int(val) for val in k.split(',') if any(c in '0123456789' for c in val)])

    def _ACQUIRE_REPRESENT(self):
        self._VALUE = str(self._value_acquire( * self._params))[1:-1]
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

class RGBA_field(Blank_space):
    def __init__(self, x, y, width, callback, value_acquire, params=(), before=lambda: None, after=lambda: None, name=None):
        Blank_space.__init__(self, x, y, width, callback, value_acquire, params, before, after, name)
        self._domain = interpret_rgba

    def _ACQUIRE_REPRESENT(self):
        self._VALUE = str(self._value_acquire( * self._params))[1:-1]
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

class Binomial_field(Numeric_field):
    def __init__(self, x, y, width, callback, value_acquire, params, before=lambda: None, after=lambda: None, name=None, letter='X'):
        Blank_space.__init__(self, x, y, width, callback, value_acquire, params, before, after, name)
        letters = set('1234567890.-+' + letter)
        self._domain = lambda k: pack_binomial(''.join([c for c in k if c in letters]))

    def _ACQUIRE_REPRESENT(self):
        self._VALUE = read_binomial( * self._value_acquire( * self._params))
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

#############
class Selection_menu(Base_kookie):
    def __init__(self, x, y, width, height, menu_callback, options_acquire, value_acquire, params = (), before=lambda: None, after=lambda: None, source=0):
        Base_kookie.__init__(self, x, y, width, height, font=('strong',))
        
        self._get_value = value_acquire
        self._get_options = options_acquire
        self._params = params
        self._BEFORE = before
        self._AFTER = after

        self._menu_callback = menu_callback

        self._dropdown_active = False
        
        # set hover function equal to press function
        self.is_over_hover = self.is_over
        
        self._source = source
        
        self._SYNCHRONIZE()

    def _ACQUIRE_OPTIONS(self):
        self._menu_options = self._get_options()
        self._lookup_label = dict(self._menu_options)

    def _ACQUIRE_REPRESENT(self):
        label = self._lookup_label[self._get_value( * self._params)]
        self._texts = []
        self._add_static_text(self._x_right, self._y_bottom - self._height/2 + 5, label, align=-1)

    def _SYNCHRONIZE(self):
        self._ACQUIRE_OPTIONS()
        self._ACQUIRE_REPRESENT()
    
    def _MENU_PUSH(self, * args):
        self._menu_callback( * args)
        self._SYNCHRONIZE()
    
    def focus(self, x, y):
        menu.menu.create(self._x, self._y_bottom - 5, 200, self._menu_options, self._MENU_PUSH, self._params, before=self._BEFORE, after=self._AFTER, source=self._source )
        self._active = True
        self._dropdown_active = True
        print('DROPDOWN')

    def defocus(self):
        self._active = None
        self._dropdown_active = False

        return False

    def hover(self, x, y):
        return 1
    
    def draw(self, cr, hover=(None, None)):
        
        self._render_fonts(cr)
        
        if hover[1] == 1:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
            
        cr.show_glyphs(self._texts[0])

class New_object_menu(Base_kookie):
    hover = xhover
    def __init__(self, x, y, width, value_push, library, TYPE, before=lambda: None, after=lambda: None, name='', source=0):
        Base_kookie.__init__(self, x, y, width, 28, font=('strong',))
        self._BEFORE = before
        self._AFTER = after
        self._library = library
        self._value_push = value_push
        self._TYPE = TYPE

        self._dropdown_active = False
        self.is_over_hover = self.is_over
        
        self._source = source
        
        self._add_static_text(self._x + 40, self._y + self.font['fontsize'] + 5, 'NEW')
        
        self._SYNCHRONIZE()
        self._make_sd([(x + 30, 2)], 3)

    def _SYNCHRONIZE(self):
        # scan objects
        self._menu_options = tuple( (v, str(k)) for k, v in sorted(self._library.items()) )

    def focus(self, x, y):
        J = self.hover(x, y)

        if J == 3:
            FS = self._TYPE()
            self._library[FS.name] = FS
            self._value_push(self._library[FS.name])
        elif J == 2:
            menu.menu.create(self._x, self._y_bottom - 5, 200, self._menu_options, lambda *args: (self._BEFORE(), self._value_push(*args), self._AFTER()), (), source=self._source )
            self._active = True
            self._dropdown_active = True
            print('DROPDOWN')
        
        self._AFTER()
        
    def draw(self, cr, hover=(None, None)):
        cr.set_line_width(2)
        if self._dropdown_active:
            cr.set_source_rgb( * accent)
        elif hover[1] == 2:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        
        # v
        downchevron(cr, self._x + 3, self._y + 1)
        cr.stroke()

        # +
        if hover[1] == 3:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        plus_sign(cr, self._x_right - 26, self._y + 1)
        cr.fill()
        
        self._render_fonts(cr)
        cr.show_glyphs(self._texts[0])
        
class Object_menu(Blank_space):
    hover = xhover
    def __init__(self, x, y, width, value_acquire, value_push, library, before=lambda: None, after=lambda: None, name='', source=0):
        self._library = library
        self._value_push = value_push

        Blank_space.__init__(self, x, y, width, lambda O, N, *args: O.rename(N, *args), value_acquire, (), before, after, name)

        self._dropdown_active = False
        self._source = source
        
        self._make_sd([(x + 30, 2), (x + width - 50, 1), (x + width - 26, 3)], 4)

    def _set_text_bounds(self):
        self._text_left = self._x + 30
        self._text_right = self._x_right - 50

    def _ACQUIRE_REPRESENT(self):
        # scan objects
        self._menu_options = tuple( (v, k) for k, v in sorted(self._library.items()) )
        
        self._O = self._value_acquire()

        self._VALUE = self._O.name
        self._LIST = list(self._VALUE) + [None]
        self._stamp_glyphs(self._LIST)

    def focus(self, x, y):
        J = self.hover(x, y)
        if J == 1:
            self._active = True
            self._dropdown_active = False
            self._i = self._target(x)
            self._j = self._i
            
            self._center_j()
        else:
            self.defocus()
            if J == 3:
                self._value_push(self._O.clone())
            elif J == 2:
                menu.menu.create(self._x, self._y_bottom - 5, 200, self._menu_options, lambda *args: (self._BEFORE(), self._value_push(*args), self._AFTER()), (),  source=self._source )
                self._active = True
                self._dropdown_active = True
                print('DROPDOWN')
                return
            elif J == 4:
                # unlink
                self._value_push(None, * self._params)
            
            self._AFTER()
        
    def defocus(self):
        self._active = None
        self._dropdown_active = False
        self._scroll = 0
        # dump entry
        self._VALUE = self._entry()
        if self._VALUE != self._PREV_VALUE:
            self._BEFORE()
            self._callback(self._O, self._VALUE, * self._params)
            self._AFTER()

        else:
            return False
        return True
        
    def _sup_draw(self, cr, hover=(None, None)):
        cr.set_line_width(2)
        if self._dropdown_active:
            cr.set_source_rgb( * accent)
        elif hover[1] == 2:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        
        # v
        downchevron(cr, self._x + 3, self._y + 1)
        cr.stroke()

        # +
        if hover[1] == 3:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        plus_sign(cr, self._subdivisions[1], self._y + 1)
        cr.fill()

        # x
        if hover[1] == 4:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        cross(cr, self._subdivisions[2], self._y + 1)
        cr.stroke()

class _Enumerated(Base_kookie):
    def __init__(self, x, y, width, height, itemheight, library, before, after, refresh, lcap = 0):
        self._itemheight = itemheight
        self._BEFORE = before
        self._AFTER = after
        self._REFRESH = refresh
        
        self._LIBRARY = library
        self._LMAX = len(library) + lcap
        Base_kookie.__init__(self, x, y, width, height, font=('strong',))

    def hover(self, x, y):
        y -= self._y
        i = int(y // self._itemheight)
        if i > self._LMAX:
            i = self._LMAX

        j = self._sdkeys[bisect.bisect(self._subdivisions, x)]
        return i, j

class Subset_table(_Enumerated):
    def __init__(self, x, y, width, height, datablock, superset, before=lambda: None, after=lambda: None, refresh=lambda: None):

        _Enumerated.__init__(self, x, y, width, height, itemheight=26, library=superset, before=before, after=after, refresh=refresh, lcap = -1)

        self._DB = datablock

        # set hover function equal to press function
        self.is_over_hover = self.is_over

        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT
        self._SYNCHRONIZE()
        
        self._make_sd([(x + width - 25, 1)], 4)

    def _ACQUIRE_REPRESENT(self):
        self._map = list(self._LIBRARY.values())
        
        self._texts = []
        if self._map:
            self._map.sort(key=lambda k: k.name)
            for i, l in enumerate(self._map):
                self._add_static_text(self._x + 10, self._y + self._itemheight*i + 17, l.name, align=1)
    
    def focus(self, x, y):
        F, C = self.hover(x, y)

        key = self._map[F]
        if C == 1 and key in self._DB.elements:
            self._DB.active = self._DB.elements[key]
            self._AFTER()

        elif C == 4:
            self._BEFORE()
            if key in self._DB.elements:
                self._DB.delete_slot(key)
            else:
                self._DB.add_slot(key)
            self._SYNCHRONIZE()
            self._AFTER()
    
    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        cr.set_line_width(1.5)
        y1 = self._y
        
        for i, l in enumerate(self._texts):
            key = self._map[i]
            if key in self._DB.elements:
                if self._DB.elements[key] is self._DB.active:
                    cr.set_source_rgb( * accent)

                    radius = 5

                    y2 = y1 + self._itemheight
                    cr.arc(self._x + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
                    cr.arc(self._x_right - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
                    cr.arc(self._x_right - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
                    cr.arc(self._x + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
                    cr.close_path()

                    cr.fill()

                    if hover[1] == (i, 4):
                        cr.set_source_rgba(1, 1, 1, 0.9)
                    else:
                        cr.set_source_rgb(1, 1, 1)
                    cr.arc(self._x_right - 15, y1 + 13, 6, 0, 2*pi)
                    cr.fill()

                    cr.set_source_rgb(1, 1, 1)
                    
                elif hover[1] is not None and hover[1][0] == i:
                    if hover[1][1] == 4:
                        cr.set_source_rgb( * accent)
                    else:
                        cr.set_source_rgba(0, 0, 0, 0.7)

                    cr.arc(self._x_right - 15, y1 + 13, 6, 0, 2*pi)
                    cr.fill()
                    cr.set_source_rgb( * accent)

                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                    cr.arc(self._x_right - 15, y1 + 13, 6, 0, 2*pi)
                    cr.fill()
            else:
                if hover[1] is not None and hover[1][0] == i:
                    if hover[1][1] == 4:
                        cr.set_source_rgb( * accent)
                    else:
                        cr.set_source_rgba(0, 0, 0, 0.7)

                    cr.arc(self._x_right - 15, y1 + 13, 5.5, 0, 2*pi)
                    cr.stroke()
                    cr.set_source_rgba(0, 0, 0, 0.4)

                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                    cr.arc(self._x_right - 15, y1 + 13, 5.5, 0, 2*pi)
                    cr.stroke()
                    cr.set_source_rgba(0, 0, 0, 0.4)
                
            cr.show_glyphs(l)
            y1 += self._itemheight

class Unordered(_Enumerated):
    def __init__(self, x, y, width, height, library, display=lambda: None, before=lambda: None, after=lambda: None, refresh=lambda: None):
        self._display = display

        _Enumerated.__init__(self, x, y, width, height, itemheight=26, library=library, before=before, after=after, refresh=refresh)

        # set hover function equal to press function
        self.is_over_hover = self.is_over

        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT
        self._SYNCHRONIZE()

        self._make_sd([(x + width - 26, 1)], 4)

    def _ACQUIRE_REPRESENT(self):
        self._map = list(self._LIBRARY.items())
        
        self._texts = []
        if self._map:
            self._map.sort()
            for i, l in enumerate(self._map):
                self._add_static_text(self._x + 10, self._y + self._itemheight*i + 17, self._display(l[1]), align=1)

    def focus(self, x, y):
        F, C = self.hover(x, y)

        if F == len(self._LIBRARY):
            self._BEFORE()
            self._LIBRARY.add_slot()
            self._SYNCHRONIZE()
            self._AFTER()
        else:
            key, value = self._map[F]
            if C == 1:
                self._LIBRARY.active = value
                self._REFRESH()

            elif C == 4:
                self._BEFORE()
                self._LIBRARY.delete_slot(key)
                self._SYNCHRONIZE()
                self._AFTER()

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        cr.set_line_width(2)
        y1 = self._y
        
        for i, l in enumerate(self._texts):
            key, value = self._map[i]
            if value is self._LIBRARY.active:
                cr.set_source_rgb( * accent)

                radius = 5

                y2 = y1 + self._itemheight
                cr.arc(self._x + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
                cr.arc(self._x_right - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
                cr.arc(self._x_right - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
                cr.arc(self._x + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
                cr.close_path()

                cr.fill()
                
                cr.set_source_rgb(1, 1, 1)
                
                cross(cr, self._subdivisions[0], y1)
                cr.stroke()

            elif hover[1] is not None and hover[1][0] == i:
                if hover[1][1] == 4:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cross(cr, self._subdivisions[0], y1)
                cr.stroke()

                if hover[1][1] == 1:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)

            else:
                cr.set_source_rgba(0, 0, 0, 0.7)
            cr.show_glyphs(l)
            y1 += self._itemheight

        if hover[1] is not None and hover[1][0] == len(self._LIBRARY):
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        plus_sign(cr, self._x + 4, y1)
        cr.fill()

class Ordered(_Enumerated):
    def __init__(self, x, y, width, height, library, display=lambda: None, before=lambda: None, after=lambda: None, refresh=lambda: None):
        self._display = display
        _Enumerated.__init__(self, x, y, width, height, itemheight=26, library=library, before=before, after=after, refresh=refresh)

        # set hover function equal to press function
        self.is_over_hover = self.is_over

        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT
        self._SYNCHRONIZE()
        
        x2 = x + width
        self._make_sd([(x2 - 74, 1), (x2 - 50, 2), (x2 - 26, 3)], 4)

    def _ACQUIRE_REPRESENT(self):
        self._texts = []
        for i, l in enumerate(self._LIBRARY):
            self._add_static_text(self._x + 10, self._y + self._itemheight*i + 17, self._display(l), align=1)
    
    def _move(self, i, j):
        if 0 <= j < len(self._LIBRARY):
            self._LIBRARY.insert(j, self._LIBRARY.pop(i))
            self._LIBRARY.active = self._LIBRARY[j]
    
    def _add(self):
        if self._LIBRARY.active is not None:
            O = self._LIBRARY.active.copy()
        else:
            O = self._LIBRARY.template.copy()
        self._LIBRARY.append(O)
        self._LIBRARY.active = O
 
    def focus(self, x, y):
        F, C = self.hover(x, y)

        if F == len(self._LIBRARY):
            self._BEFORE()
            self._add()
            self._SYNCHRONIZE()
            self._AFTER()
        else:
            if C == 1:
                self._LIBRARY.active = self._LIBRARY[F]
                self._REFRESH()
                return

            elif C == 2:
                self._BEFORE()
                self._move(F, F - 1)
                self._SYNCHRONIZE()

            elif C == 3:
                self._BEFORE()
                self._move(F, F + 1)
                self._SYNCHRONIZE()

            elif C == 4:
                self._BEFORE()
                del self._LIBRARY[F]
                self._SYNCHRONIZE()
            
            self._AFTER()

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.set_line_width(2)
        
        y1 = self._y
        for i, value in enumerate(self._LIBRARY):
            l = self._texts[i]
            if value is self._LIBRARY.active:
                cr.set_source_rgb( * accent)

                radius = 5

                y2 = y1 + self._itemheight
                cr.arc(self._x + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
                cr.arc(self._x_right - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
                cr.arc(self._x_right - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
                cr.arc(self._x + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
                cr.close_path()

                cr.fill()
                
                cr.set_source_rgb(1, 1, 1)
                cr.show_glyphs(l)

                upchevron(cr, self._subdivisions[0], y1)
                cr.stroke()
                
                downchevron(cr, self._subdivisions[1], y1)
                cr.stroke()

                cross(cr, self._subdivisions[2], y1)
                cr.stroke()

                cr.set_source_rgba(0, 0, 0, 0.7)
            elif hover[1] is not None and hover[1][0] == i:
                if hover[1][1] == 1:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cr.show_glyphs(l)

                if hover[1][1] == 2:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                upchevron(cr, self._subdivisions[0], y1)
                cr.stroke()

                if hover[1][1] == 3:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                downchevron(cr, self._subdivisions[1], y1)
                cr.stroke()

                if hover[1][1] == 4:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cross(cr, self._subdivisions[2], y1)
                cr.stroke()
                
                cr.set_source_rgba(0, 0, 0, 0.7)
            else:
                cr.show_glyphs(l)

            y1 += self._itemheight
        
        if hover[1] is not None and hover[1][0] == len(self._LIBRARY):
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        plus_sign(cr, self._x + 4, y1)
        cr.fill()

class Para_control_panel(Ordered):
    def __init__(self, x, y, width, height, paragraph, library, display=lambda: None, before=lambda: None, after=lambda: None, refresh=lambda: None):
        self._display = display
        _Enumerated.__init__(self, x, y, width, height, itemheight=26, library=library, before=before, after=after, refresh=refresh, lcap=1)

        self._paragraph = paragraph

        # set hover function equal to press function
        self.is_over_hover = self.is_over

        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT
        self._SYNCHRONIZE()
        
        x2 = x + width
        self._make_sd([(x + 25, 5), (x + 50, 6), (x2 - 69, 1), (x2 - 47, 2), (x2 - 25, 3)], 4)
        
    def _ACQUIRE_REPRESENT(self):
        self._texts = []
        for i, l in enumerate(chain((self._display(L) for L in self._LIBRARY), ['ELEMENT'])):
            self._add_static_text(self._x + 55, self._y + self._itemheight*i + 17, l, align=1)

    def focus(self, x, y):
        F, C = self.hover(x, y)
        items = self._LIBRARY + [self._paragraph.EP]

        if F == len(items):
            self._BEFORE()
            self._add()
            self._SYNCHRONIZE()
            self._AFTER()

        else:
            PSTYLE = items[F]
            if C == 1:
                self._LIBRARY.active = PSTYLE
                self._REFRESH()
                return C
            
            elif F < len(items) - 1:
                if C == 2:
                    self._BEFORE()
                    self._move(F, F - 1)

                elif C == 3:
                    self._BEFORE()
                    self._move(F, F + 1)
                
                elif C == 4:
                    self._BEFORE()
                    del self._LIBRARY[F]
                
                if C == 5 or C == 6 and len(PSTYLE.tags) == 1:
                    tag, count = next(iter(PSTYLE.tags.items()))
                    self._BEFORE()
                    if C == 5:
                        self._paragraph.P[tag] -= 1
                    else:
                        self._paragraph.P[tag] += 1

            self._SYNCHRONIZE()
            self._AFTER()
            return C
    
    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        cr.set_line_width(2)
        y1 = self._y
        
        for i, PSTYLE in enumerate(chain(self._LIBRARY, [self._paragraph.EP])):

            if PSTYLE is self._LIBRARY.active:
                radius = 5

                y2 = y1 + self._itemheight
                cr.move_to(self._x, y1 + radius)
                cr.arc(self._x + radius, y1 + radius, radius, 2*(pi/2), 3*(pi/2))
                cr.arc(self._x_right - radius, y1 + radius, radius, 3*(pi/2), 4*(pi/2))
                cr.arc(self._x_right - radius, y2 - radius, radius, 0*(pi/2), 1*(pi/2))
                cr.arc(self._x + radius, y2 - radius, radius, 1*(pi/2), 2*(pi/2))
                cr.close_path()
                
                if PSTYLE.tags <= self._paragraph.P:
                    cr.set_source_rgb( * accent)
                    cr.fill()
                else:
                    cr.set_source_rgb(0.7, 0.7, 0.7)
                    cr.fill()

                cr.set_source_rgb(1, 1, 1)
                
                upchevron(cr, self._subdivisions[2], y1)
                cr.stroke()
                
                downchevron(cr, self._subdivisions[3], y1)
                cr.stroke()

                cross(cr, self._subdivisions[4], y1)
                cr.stroke()

                if len(PSTYLE.tags) == 1:
                    minus_sign(cr, self._x, y1)
                    plus_sign(cr, self._x + 25, y1)
                    k = next(iter(PSTYLE.tags.keys()))
                    cr.move_to(self._x + 22, y1 + 17)
                    cr.show_text(str(self._paragraph.P[k]))
                    cr.fill()

                cr.set_source_rgb(1, 1, 1)

            elif hover[1] is not None and hover[1][0] == i:
                if hover[1][1] == 2:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                upchevron(cr, self._subdivisions[2], y1)
                cr.stroke()

                if hover[1][1] == 3:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                downchevron(cr, self._subdivisions[3], y1)
                cr.stroke()

                if hover[1][1] == 4:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cross(cr, self._subdivisions[4], y1)
                cr.stroke()

                if len(PSTYLE.tags) == 1:
                    if hover[1] == (i, 5):
                        cr.set_source_rgb( * accent)
                    else:
                        cr.set_source_rgba(0, 0, 0, 0.7)
                    minus_sign(cr, self._x, y1)
                    cr.fill()

                    if hover[1] == (i, 6):
                        cr.set_source_rgb( * accent)
                    else:
                        cr.set_source_rgba(0, 0, 0, 0.7)
                    plus_sign(cr, self._x + 25, y1)
                    cr.fill()
                    k = next(iter(PSTYLE.tags.keys()))
                    cr.move_to(self._x + 22, y1 + 17)
                    cr.show_text(str(self._paragraph.P[k]))
                
                if PSTYLE.tags <= self._paragraph.P:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.4)

            elif PSTYLE.tags <= self._paragraph.P:
                cr.set_source_rgba(0, 0, 0, 0.7)
                
                if len(PSTYLE.tags) == 1:
                    k = next(iter(PSTYLE.tags.keys()))
                    cr.move_to(self._x + 22, y1 + 17)
                    cr.show_text(str(self._paragraph.P[k]))

            else:
                cr.set_source_rgba(0, 0, 0, 0.4)
                
            cr.show_glyphs(self._texts[i])
            y1 += self._itemheight

        if hover[1] is not None and hover[1][0] == len(self._LIBRARY) + 1:
            cr.set_source_rgb( * accent)
        else:
            cr.set_source_rgba(0, 0, 0, 0.7)
        plus_sign(cr, self._x + 50, y1)
        cr.fill()

class Z_indicator(Base_kookie):
    def __init__(self, x, y, width, height, get_projection, get_attributes, A, copy_value, library, before=lambda: None, after=lambda: None):
        self._BEFORE = before
        self._AFTER = after
        Base_kookie.__init__(self, x, y, width, height)

        # set hover function equal to press function
        self.is_over_hover = self.is_over

        self._get_projection = get_projection
        self._get_attributes = get_attributes
        self._LIBRARY = library
        self._attribute = A
        self._copy_value = copy_value
        
        self._state = 0
        
        self._colors = ((0.6, 0.6, 0.6), accent, accent, (0.7, 0.7, 0.7))
        self._hover_colors = ((0.4, 0.4, 0.4), tuple(v + 0.2 for v in accent), tuple(v + 0.2 for v in accent), (0.5, 0.5, 0.5))

        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT
        self._SYNCHRONIZE()

    def is_over(self, x, y):
        return True
        
    def hover(self, x, y):
        return 1
    
    def focus(self, x, y):
        self._BEFORE()
        if self._state == 3:
            self._copy_value(self._attribute)
        else:
            del self._get_attributes(self._LIBRARY)[self._attribute]
        self._AFTER()

    def _ACQUIRE_REPRESENT(self):
        L = self._get_projection()
        # test for definition
        if self._attribute in self._get_attributes(self._LIBRARY):
            # test for stack membership
            if self._LIBRARY.active in L.members:
                # test for stack visibility
                if self._LIBRARY.active is L.Z[self._attribute]:
                    self._state = 1 # defined, in effect
                else:
                    self._state = 2 # defined, but overriden
            else:   
                self._state = 0 # defined, but not applicable

        else:
            self._state = 3 # undefined, unapplicable

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        cr.rectangle(self._x, self._y, self._width, self._height)
        if hover[1]:
            colors = self._hover_colors
        else:
            colors = self._colors
        
        cr.set_source_rgb( * colors[self._state])
        if self._state == 2:
            cr.clip()
            cr.move_to(self._x, self._y)

            for i in range(6):
                
                cr.rel_line_to(self._width, -12)
                cr.rel_line_to(0, 3.8)
                cr.rel_line_to(-self._width, 12)
                cr.rel_move_to(0, 2.8)
            
            cr.fill()
            cr.reset_clip()
        if self._state == 3:
            cr.fill()
            cr.rectangle(self._x + 2, self._y + 2, self._width - 4, self._height - 4)
            cr.set_source_rgb(1, 1, 1)
            cr.fill()
        else:
            cr.fill()

class _Table(Base_kookie):
    def __init__(self, x, y, width, height, cellsize):
        self._cellwidth, self._cellheight = cellsize
        self._cellratio = self._cellwidth / self._cellheight
        Base_kookie.__init__(self, x, y, width, height, font=('strong',))
        self._per_row = ( self._width // self._cellwidth )
        # set hover function equal to press function
        self.is_over_hover = self.is_over

    def _construct_table(self, margin=0):
        self._texts = []
        self._cells = []
        x = self._x
        y = self._y
        mp = self._cellwidth/2
        for cell in self._table:
            if x + self._cellwidth > self._x_right:
                x = self._x
                y += self._cellheight
            
            self._add_static_text(x + mp, y + 18, cell[1], align=0)
            self._cells.append((x + margin, y + margin, self._cellwidth - 2*margin, self._cellheight - 2*margin))
            
            x += self._cellwidth
    
class Counter_editor(_Table):
    def __init__(self, x, y, width, height, cellsize, get_counter, superset, before=lambda: None, after=lambda: None):
        self._BEFORE = before
        self._AFTER = after
        self._get_counter = get_counter
        self._SUPERSET = superset

        _Table.__init__(self, x, y, width, height, cellsize)

        self._SYNCHRONIZE = self._ACQUIRE_REPRESENT
        self._SYNCHRONIZE()

    def _ACQUIRE_REPRESENT(self):
        self._COUNT = self._get_counter()
        self._table = [(self._COUNT[V], str(self._COUNT[V]) + ' ' + V.name, V) for V in sorted(self._SUPERSET.values(), key=lambda k: k.name)]
        self._construct_table(margin = 2)

    def hover(self, x, y):
        y -= self._y
        x -= self._x
        k = (y // self._cellheight)
        h = x // self._cellwidth
        if h >= self._per_row:
            h = self._per_row - 1

        i = int(k * self._per_row + h)
        if i >= len(self._table):
            i = None
            j = None
        else:
            a = x - h*self._cellwidth
            if a * 2 > self._cellwidth:
                j = 1
            else:
                j = -1
        return i, j

    def focus(self, x, y):
        i, j = self.hover(x, y)
        if i is not None:
            self._BEFORE()
            self._COUNT[self._table[i][2]] += j
            if not self._COUNT[self._table[i][2]]:
                del self._COUNT[self._table[i][2]]
            self._SYNCHRONIZE()
            self._AFTER()

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        
        for i, cell in enumerate(self._cells):
            if self._table[i][0]:
                if self._table[i][0] > 0:
                    R = range(self._table[i][0])
                    bg = accent
                else:
                    R = reversed(range(0, self._table[i][0], -1))
                    bg = (1, 0.3, 0.35)
                for c in R:
                    cr.set_source_rgba(1, 1, 1, 0.5)
                    cr.rectangle(cell[0] + 2*c - 1, cell[1] - 2*c + 1, cell[2], cell[3])
                    cr.fill()
                    cr.set_source_rgb( * bg)
                    cr.rectangle(cell[0] + 2*c, cell[1] - 2*c, cell[2], cell[3])
                    cr.fill()
                
                offset = (self._table[i][0] - 1) * 2
                if offset < 0:
                    offset = 0
                cr.set_source_rgb(1, 1, 1)
                cr.show_glyphs([(g[0], g[1] + offset, g[2] - offset) for g in self._texts[i]])
                plus_sign(cr, cell[0] + cell[2] - 24 + offset, cell[1] - 1 - offset)
                minus_sign(cr, cell[0] - 2 + offset, cell[1] - 1 - offset)
                
                cr.fill()
                
            elif hover[1] is not None and hover[1][0] == i:
                plus_sign(cr, cell[0] + cell[2] - 24, cell[1])
                if hover[1][1] == 1:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cr.fill()
                minus_sign(cr, cell[0] - 2, cell[1])
                if hover[1][1] == -1:
                    cr.set_source_rgb( * accent)
                else:
                    cr.set_source_rgba(0, 0, 0, 0.7)
                cr.fill()
                cr.set_source_rgb( * accent)
                cr.show_glyphs(self._texts[i])
            else:
                cr.set_source_rgba(0, 0, 0, 0.7)
                cr.show_glyphs(self._texts[i])
