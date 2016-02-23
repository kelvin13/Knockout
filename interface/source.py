from itertools import chain, accumulate
from bisect import bisect

from interface.base import Base_kookie, accent
from style.styles import ISTYLES
from IO.kevin import serialize, deserialize
from elements.elements import Mod_element
from edit import cursor

def _chunks(L, n):
    br = [i + 1 for i, v in enumerate(L) if v == '\n']
    for line in (L[i : j] for i, j in zip([0] + br, br + [len(L)])):
        linelen = len(line)
        for i in range(0, linelen, n):
            if i + n < linelen and line[i + n] == '\n':
                yield line[i:], not bool(i)
                break
            else:
                yield line[i : i + n], not bool(i)

def _paint_select(cl, sl, cx, sx, left, right):
    select = []
    if cl == sl:
                           # y, x1, x2
        select.append((cl, cx, sx))
    else:
        (cl, cx), (sl, sx) = sorted(((cl, cx), (sl, sx)))
        select.append((cl, cx, right))
        select.extend(((l, left, right) for l in range(cl + 1, sl)))
        select.append((sl, left, sx))
    return select

class Rose_garden(Base_kookie):
    def __init__(self, x, y, width, e_acquire, before=lambda: None, after=lambda: None):
        self._BEFORE = before
        self._AFTER = after
        self._e_acquire = e_acquire

        self.font = ISTYLES[('mono',)]
        fontsize = self.font['fontsize']
        self._K = self.font['fontmetrics'].advance_pixel_width(' ') * fontsize
        self._leading = int(fontsize * 1.3)
        
        self._charlength = int((width - 30) // self._K)
        width = int(self._charlength * self._K + 30)

        Base_kookie.__init__(self, x, y, width, 0, font=None)
        
        self._SYNCHRONIZE()
        
        self.is_over_hover = self.is_over
        
        # cursors
        self._i = 0
        self._j = 0
        
        self._active = False
        self._invalid = False

    def _ACQUIRE_REPRESENT(self):
        self._element = self._e_acquire()
        self._VALUE = serialize([self._element])
        self._CHARS = list(self._VALUE) + ['\n']
        self._grid_glyphs(self._CHARS)
        self._invalid = False

    def _SYNCHRONIZE(self):
        self._ACQUIRE_REPRESENT()
        self._PREV_VALUE = self._VALUE

    def _grid_glyphs(self, glyphs):
        x = self._x
        y = self._y
        
        K = self._K
        leading = self._leading
        FMX = self.font['fontmetrics'].character_index
        
        lines = list(_chunks(self._CHARS, self._charlength))
        self._IJ = [0] + list(accumulate(len(l) for l, br in lines))
        self.y_bottom = y + leading * len(lines)
        
        y += leading
        xd = x + 30
        self._LL = [[(FMX(character), xd + i*K, y + l*leading) for i, character in enumerate(line) if character != '\n'] for l, (line, br) in enumerate(lines)]
        N = zip(accumulate(br for line, br in lines), enumerate(lines))
        self._numbers = [[(FMX(character), x + i*K, y + l*leading) for i, character in enumerate(str(int(N)))] for N, (l, (line, br)) in N if br]
    
    def _target(self, x, y):
        y -= self._y
        x -= self._x + 30
        
        l = min(max(int(y // self._leading), 0), len(self._LL) - 1)
        di = int(round(x / self._K))
        i = self._IJ[l]
        j = self._IJ[l + 1]
        if x > self._width - 20:
            j += 1
        g = min(max(di + i, i), j - 1)
        return g
    
    def is_over(self, x, y):
        return self._y <= y <= self.y_bottom and self._x <= x <= self._x_right + 10

    def _entry(self):
        return ''.join(self._CHARS[:-1])
    
    # typing
    def type_box(self, name, char):
        changed = False
        output = None
        if name in ['BackSpace', 'Delete']:
            # delete selection
            if self._i != self._j:
                # sort
                self._i, self._j = sorted((self._j, self._i))
                del self._CHARS[self._i : self._j]
                changed = True
                self._j = self._i
                
            elif name == 'BackSpace':
                if self._i > 0:
                    del self._CHARS[self._i - 1]
                    changed = True
                    self._i -= 1
                    self._j -= 1
            else:
                if self._i < len(self._CHARS) - 2:
                    del self._CHARS[self._i]
                    changed = True

        elif name == 'Left':
            if self._i > 0:
                self._i -= 1
                self._j = self._i
        elif name == 'Right':
            if self._i < len(self._CHARS) - 1:
                self._i += 1
                self._j = self._i
        elif name == 'Up':
            l = self._index_to_line(self._i)
            u = max(0, l - 1)
            z = self._IJ[l]
            a = self._IJ[u]
            b = self._IJ[u + 1]
            self._i = min(a + self._i - z, b)
            self._j = self._i
        elif name == 'Down':
            l = self._index_to_line(self._i)
            u = min(len(self._LL) - 1, l + 1)
            z = self._IJ[l]
            a = self._IJ[u]
            b = self._IJ[u + 1]
            self._i = min(a + self._i - z, b, len(self._CHARS) - 1)
            self._j = self._i
            
        elif name == 'Home':
            l = self._index_to_line(self._i)
            z = self._IJ[l]
            self._i = z
            self._j = z
        elif name == 'End':
            l = self._index_to_line(self._i)
            z = self._IJ[l + 1] - 1
            self._i = z
            self._j = z

        elif name == 'All':
            self._i = 0
            self._j = len(self._CHARS) - 1
        
        elif name == 'Paste':
            # delete selection
            if self._i != self._j:
                # sort
                self._i, self._j = sorted((self._j, self._i))
                del self._CHARS[self._i : self._j]
                self._j = self._i
            # take note that char is a LIST now
            self._CHARS[self._i:self._i] = char
            changed = True
            self._i += len(char)
            self._j = self._i
        
        elif name == 'Copy':
            if self._i != self._j:
                # sort
                self._i, self._j = sorted((self._j, self._i))
                output = ''.join(self._CHARS[self._i : self._j])
        
        elif name == 'Cut':
            # delete selection
            if self._i != self._j:
                # sort
                self._i, self._j = sorted((self._j, self._i))
                output = ''.join(self._CHARS[self._i : self._j])
                del self._CHARS[self._i : self._j]
                changed = True
                self._j = self._i
        
        elif name == 'Tab':
            self._i, self._j = sorted((self._j, self._i))
            cl = self._index_to_line(self._i)
            sl = self._index_to_line(self._j)
            if cl == sl:
                a = self._IJ[cl]
                self.type_box('Paste', ' ' * (4 - (self._i - a) % 4))
            else:
                IJ = self._IJ
                CHARS = self._CHARS
                di = 0
                dj = 0
                for l in range(sl, cl - 1, -1):
                    a = IJ[l]
                    if CHARS[a - 1] == '\n':
                        CHARS[a : a] = ' ' * 4
                        dj += 4

                changed = True
                self._i += 4
                self._j += dj
        
        elif name in {'Ctrl Tab', 'ISO_Left_Tab'}:
            self._i, self._j = sorted((self._j, self._i))
            cl = self._index_to_line(self._i)
            sl = self._index_to_line(self._j)
            IJ = self._IJ
            CHARS = self._CHARS
            ifloor = None
            di = 0
            dj = 0
            for l in range(sl, cl - 1, -1):
                a = IJ[l]
                if CHARS[a - 1] == '\n':
                    b = IJ[l + 1] - 1
                    if b - a >= 4:
                        try:
                            d = next(i for i, v in enumerate(CHARS[a : a + 4]) if v != ' ')
                        except StopIteration:
                            d = 4
                        dj -= d
                        di = -d
                        ifloor = a
                        del CHARS[a : a + d]
            changed = True
            self._i = max(ifloor, self._i + di)
            self._j += dj

        elif char is not None:
            # delete selection
            if self._i != self._j:
                # sort
                self._i, self._j = sorted((self._j, self._i))
                del self._CHARS[self._i : self._j]
                self._j = self._i
            if char == '\r':
                char = '\n'
            self._CHARS[self._i:self._i] = [char]
            changed = True
            self._i += 1
            self._j += 1
        
        if changed:
            self._grid_glyphs(self._CHARS)
        
        return output

    def focus(self, x, y):
        self._i = self._target(x, y)
        self._j = self._i
        self._active = True

    def focus_drag(self, x, y):
        j = self._target(x, y)
        
        # force redraw if cursor moves
        if self._j != j:
            self._j = j
            return True
        else:
            return False

    def _commit(self, B):
        if isinstance(self._element, Mod_element):
            success = self._element.transfer(B)
            if not success:
                self._invalid = True
                return
        else:
            i = cursor.fcursor.i
            cursor.fcursor.FTX.text[i:i + 1] = deserialize(B, fragment=True)
        self._SYNCHRONIZE()
        self._AFTER()
        
    def defocus(self):
        self._active = False
        # dump entry
        self._VALUE = self._entry()
        if self._VALUE != self._PREV_VALUE:
            self._BEFORE()
            self._commit(self._VALUE)
            self._PREV_VALUE = self._VALUE
        else:
            return False
        return True

    def hover(self, x, y):
        return 1
    
    def _index_to_line(self, i):
        return bisect(self._IJ, i) - 1
    
    def _cursor_location(self, i):
        l = self._index_to_line(i)
        gx = (i - self._IJ[l]) * self._K
        return l, int(self._x + 30 + gx), self._y + self._leading * l

    def draw(self, cr, hover=(None, None)):
        self._render_fonts(cr)
        # line numbers
        cr.set_source_rgb(0.7, 0.7, 0.7)
        cr.show_glyphs(chain.from_iterable(self._numbers))
        cr.fill()
        
        # highlight
        if self._active:
            cr.set_source_rgba(0, 0, 0, 0.1)
            leading = self._leading
            cl, cx, cy = self._cursor_location(self._i)
            sl, sx, sy = self._cursor_location(self._j)

            for l, x1, x2 in _paint_select(cl, sl, cx, sx, self._x + 30, self._x_right):
                cr.rectangle(x1, self._y + l*leading, x2 - x1, leading)
            cr.fill()

        # text
            if self._invalid:
                cr.set_source_rgb(1, 0.2, 0.2)
            else:
                cr.set_source_rgb(0.2, 0.2, 0.2)
        else:
            if self._invalid:
                cr.set_source_rgb(1, 0.4, 0.4)
            else:
                cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.show_glyphs(chain.from_iterable(self._LL))
        cr.fill()

        # cursor
        if self._active:
            cr.set_source_rgb( * accent)
            cr.rectangle(cx - 1, cy, 2, leading)
            cr.rectangle(sx - 1, sy, 2, leading)
            cr.fill()