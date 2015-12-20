import bisect, itertools
from freetype import ft_errors
from copy import deepcopy

from state import constants
from state import noticeboard

from fonts import fonts
from fonts import fonttable

from interface import kookies, caramel, ui

from model import meredith, penclick
from model import un


class _Font_file_Field(kookies.Blank_space):
    def __init__(self, x, y, width, p, f, name=None):
        self.p = p
        self.f = f

        kookies.Blank_space.__init__(self, x, y, width, callback=self._push_fontname, value_acquire=self._value_acquire, name=name)

    def _value_acquire(self):
        self.broken = not fonttable.table.get_font(self.p, self.f)['path_valid']
        return fonttable.table.get_font(self.p, self.f)['path']

    def _push_fontname(self, path):

        fonttable.table.clear()
        
        fonts.f_set_attribute((False, path), 'path', self.p, self.f)
        
        meredith.mipsy.recalculate_all()
        klossy.synchronize()

def _p_push_value(value, attribute, p):
    fonts.p_set_attribute((False, value), attribute, p)

def create_p_field(TYPE, x, y, width, attribute, p, after, value_acquire=lambda A, p: str(fonttable.p_table.get_paragraph(p)[A]),  name=''):
    return TYPE(x, y, width,
            callback= _p_push_value, 
            value_acquire= value_acquire,
            params = (attribute, p), 
            before=un.history.save,
            after=after,
            name=name)

def _indent_acquire(A, p):
    C, SIGN, K = fonttable.p_table.get_paragraph(p)[A]

    if K:
        if abs(K) == 1:
            coefficient = ''
        else:
            coefficient = str(K)
        
        if SIGN == -1:
            SIGN = ' - '
        else:
            SIGN = ' + '
        
        if C:
            val = str(C) + SIGN + coefficient + 'K'
        else:
            if SIGN == ' + ':
                val = coefficient + 'K'
            else:
                val = SIGN[1] + coefficient + 'K'
    else:
        val = str(C)
    return val

def _push_indent(value, A, p):
    K = 0
    C = 0
    sgn = 1
    for k, g in ( (k, ''.join(g)) for k, g in itertools.groupby(value, key=lambda v: True if v in ('+', '-') else False) ):
        if k:
            if g.count('-') % 2:
                sgn = -1
            else:
                sgn = 1
        else:
            if 'K' in g:
                if g[0] == 'K':
                    coefficient = 1
                else:
                    coefficient = int(float(g[:g.find('K')]))
                K += coefficient*sgn
            else:
                if '.' in g:
                    if g.count('.') > 1:
                        dot = g.find('.')
                        g = ''.join(g[:dot + 1]) + ''.join([d for d in g[dot + 1:] if d != '.'])
                    constant = float(g)
                else:
                    constant = int(g)
                C += constant*sgn
    
    if K < 0:
        SIGN = -1
        K = abs(K)
    else:
        SIGN = 1
    
    value = (C, SIGN, K)
    
    fonts.p_set_attribute((False, value), A, p)

class _Paragraph_INDENT_EXP(kookies.Blank_space):
    def __init__(self, x, y, width, p, after, name=None):
        kookies.Blank_space.__init__(self, x, y, width,
                callback=_push_indent, 
                value_acquire=_indent_acquire,
                params = ('indent', p), 
                before=un.history.save,
                after=after,
                name=name)
        
        self._domain = lambda k: ''.join([c for c in k if c in '1234567890.-+K'])

    def _stamp_glyphs(self, text):
        self._template = self._build_line(self._x, self._y + self.font['fontsize'] + 5, text, self.font, sub_minus=True)


def _add_pclass():
    un.history.save()
    fonttable.p_table.clear()
    
    p, p_i = meredith.mipsy.glyph_at()[2]
    ns, p = p
    if len(p) > 3 and p[-4] == '.' and len([c for c in p[-3:] if c in '1234567890']) == 3:
        serialnumber = int(p[-3:])
        while True:
            serialnumber += 1
            name = p[:-3] + str(serialnumber).zfill(3)
            if (ns, name) not in fonts.paragraph_classes:
                break
    else:
        name = p + '.001'
    fonts.add_paragraph_class( (ns, name), (ns, p) )
    meredith.mipsy.change_paragraph_class( p_i, (ns, name) )

    klossy.refresh()

def _current_set_pclass(name):
    un.history.save()
    p = meredith.mipsy.glyph_at()[2]
    meredith.mipsy.change_paragraph_class(p[1], name)
    klossy.refresh()
    return False
    
class _Paragraph_style_menu(kookies.Object_menu):
    def __init__(self, x, y, width, p, name=None, source=0):
        entries = sorted(fonts.paragraph_classes.keys())
        entries = list(zip(entries, [v[0] + ' : ' + v[1] for v in entries]))
        
        self.p = p
        self._value_acquire = lambda: self.p[1]
        
        kookies.Object_menu.__init__(self, x, y, width, callback=self._push_pname, addition_callback=_add_pclass, menu_callback=_current_set_pclass, menu_options=entries, value_acquire=self._value_acquire, name=name, source=source)

    def _push_pname(self, name):
        un.history.save()
        fonttable.p_table.clear()
        
        new = (self.p[0], name)
        fonts.rename_p(self.p, new )
        meredith.mipsy.rename_paragraph_class(self.p, new )
        self.p = new

        meredith.mipsy.recalculate_all()
        klossy.refresh() # all the self.p’s have changed


def _P_options_acquire_filtered():
    PPP = ['—'] + sorted(list( key for key in fonts.paragraph_classes.keys() if not fonts.paragraph_classes[key]['fontclasses'][0] ))
    return list(zip(PPP, [v if v == '—' else v[0] + ' : ' + v[1] for v in PPP]))
    
def _F_options_acquire(P):
    if P != '—':
        return (('—', '—'), ) + tuple( sorted(((P, ff), '{ ' + ', '.join(ff) + ' }') for ff in fonts.paragraph_classes[P]['fontclasses'][1].keys()) )
    else:
        return (('—', '—'), )
    
class _Inheritance_selection_menu(kookies.Double_selection_menu):
    def __init__(self, x, y, width, p, f, attribute, source=0):
        self._p = p
        self._f = f
        self._attribute = attribute
        
        self._display = lambda k, v: k[0][1] + ' › ' + v if isinstance(k[0], tuple) else '—'
        
        kookies.Double_selection_menu.__init__(self, x, y, width=width, height=15, menu_callback=self._push_inherit, options_acquire=_P_options_acquire_filtered, options_acquire_l2=_F_options_acquire, value_acquire=self._value_acquire, source=source)

    def _value_acquire(self):
        if self._attribute == '_all':
            current = fonts.paragraph_classes[self._p]['fontclasses'][1][self._f]
        else:
            current = fonts.f_read_attribute(self._attribute, self._p, self._f)
        
        if current[0]:
            return (current[1][0], tuple(current[1]))
        else:
            return ('—', '—')
    
    def _push_inherit(self, value):
        fonttable.table.clear()
        if value == '—':
            if self._attribute == '_all':
                fonts.paragraph_classes[self._p]['fontclasses'][1][self._f] = deepcopy(fonts.f_get_f(self._p, self._f))
            else:
                fonts.f_set_attribute((False, fonttable.table.get_font(self._p, self._f)[self._attribute]), self._attribute, self._p, self._f)
        else:
            # save old value in case of a disaster
            if self._attribute == '_all':
                v = fonts.f_get_f(self._p, self._f)
            else:
                v = fonts.f_get_attribute(self._attribute, self._p, self._f)
            
            value = (True, value)
            fonts.f_set_attribute(value, self._attribute, self._p, self._f)

            try:
                fonttable.table.get_font(self._p, self._f)
            except RuntimeError:
                fonttable.table.clear()
                fonts.f_set_attribute(v, self._attribute, self._p, self._f)
                print('REFERENCE LOOP DETECTED')
        
        if self._attribute == 'path':
            meredith.mipsy.recalculate_all()
            klossy.synchronize()
        elif self._attribute == '_all':
            klossy.refresh()
        else:
            klossy.synchronize()

def _P_options_acquire():
    PPP = ['—'] + list(fonts.paragraph_classes.keys())
    return list(zip(PPP, [v if v == '—' else v[0] + ' : ' + v[1] for v in PPP]))
    
class _Paragraph_inheritance_menu(kookies.Selection_menu):
    def __init__(self, x, y, width, p, attribute, source=0):
        self._p = p
        self._attribute = attribute
        
        kookies.Selection_menu.__init__(self, x, y, width=width, height=15, menu_callback=self._push_inherit, options_acquire=_P_options_acquire, value_acquire=self._value_acquire, source=source)

    def _value_acquire(self):
        current = fonts.p_read_attribute(self._attribute, self._p)
        if current[0]:
            return current[1]
        else:
            return '—'
    
    def _push_inherit(self, value):
        un.history.save()
        fonttable.p_table.clear()
        if value == '—':
            fonts.p_set_attribute((False, fonttable.p_table.get_paragraph(self._p)[self._attribute]), self._attribute, self._p)
        else:
            # save old value in case of a disaster
            v = fonts.p_get_attribute(self._attribute, self._p)
            value = (True, value)
            fonts.p_set_attribute(value, self._attribute, self._p)

            try:
                fonttable.p_table.get_paragraph(self._p)
            except RuntimeError:
                fonttable.p_table.clear()
                fonts.p_set_attribute(v, self._attribute, self._p)
                print('REFERENCE LOOP DETECTED')
        
        klossy.refresh()
    

class _preview(kookies.Heading):
    def __init__(self, x, y, width, height, text, p, f):
        
        kookies.Heading.__init__(self, x, y, width, height, text, font=fonttable.table.get_font(p[0], f), fontsize = 15)
        
        self.p = p
        self.f = f

    def draw(self, cr, hover=(None, None)):
        cr.set_source_rgb(0,0,0)
        
        cr.set_font_size(15)
        cr.set_font_face(self.font['font'])
        cr.show_glyphs(self._texts[0])


class _TWO_COLUMN(object):
    def __init__(self, left, right):
        lbb = left.bounding_box()
        rbb = right.bounding_box()
        self.partition = (lbb[1] + rbb[0]) // 2
        self.y = max((lbb[3], rbb[3]))
        
        self.draw = lambda cr: None
        self._SYNCHRONIZE = lambda: None

# do not instantiate directly, requires a _reconstruct
class _Properties_panel(ui.Cell):
    def __init__(self, tabs = (), default=0, partition=1 ):
        
        self._partition = partition

        width = 140
        self._tabstrip = kookies.Tabs( (constants.window.get_h() - constants.UI[partition] - width)//2 , 50, width, 30, default=default, callback=self._tab_switch, signals=tabs)
        self._tab = tabs[default][0]
        
        self._reconstruct()

    def _tab_switch(self, name):
        if self._tab != name:
            self._tab = name
            self._reconstruct()
        
    def _stack(self):
        self._rows = [item.y for item in self._items]

    def _stack_bisect(self, x, y):
        i = bisect.bisect(self._rows, y)
        try:
            item = self._items[i]
        except IndexError:
            i -= 1
            item = self._items[i]
        
        if isinstance(item, _TWO_COLUMN):
            if x < item.partition:
                i += 1
            else:
                i += 2
        return i

    def refresh(self):
        meredith.mipsy.recalculate_all() # must come before because it rewrites all the paragraph styles
        self._reconstruct()
    
    def synchronize(self):
        for item in self._items:
            item._SYNCHRONIZE()

    def _TURNOVER_WITH_RERENDER_P(self):
        fonttable.p_table.clear()
        meredith.mipsy.recalculate_all()
        self.synchronize()

    def _TURNOVER_WITH_RERENDER_F(self):
        fonttable.table.clear()
        meredith.mipsy.recalculate_all()
        self.synchronize()

    def render(self, cr, h, k):
        
        # DRAW BACKGROUND
        cr.rectangle(0, 0, 
                h - constants.UI[self._partition], 
                k)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        
        # check if entries need restacking
        if noticeboard.refresh_properties_stack.should_refresh():
            mode = noticeboard.refresh_properties_type.should_refresh()
            if mode[0]:
                self._swap_reconstruct(mode[1])
            else:
                self._reconstruct()
        
        for i, entry in enumerate(self._items):
            if i == self._hover_box_ij[0]:
                entry.draw(cr, hover=self._hover_box_ij)
            else:
                entry.draw(cr)
        
        # DRAW SEPARATOR
        cr.rectangle(0, 0, 
                2, 
                k)
        cr.set_source_rgb(0.9, 0.9, 0.9)
        cr.fill()
    
    def key_input(self, name, char):
        if self._active_box_i is not None:
            if name == 'Return':
                self._items[self._active_box_i].defocus()
                self._active_box_i = None
            else:
                return self._items[self._active_box_i].type_box(name, char)
    
    def press(self, x, y, char):

        b = None
        bb = self._stack_bisect(x, y)

        if self._items[bb].is_over(x, y):
            self._items[bb].focus(x, y)
            b = bb

        # defocus the other box, if applicable
        if b is None or b != self._active_box_i:
            if self._active_box_i is not None:
                self._items[self._active_box_i].defocus()
            self._active_box_i = b
            
    def press_motion(self, x, y):
        if self._active_box_i is not None and self._items[self._active_box_i].focus_drag(x):
            noticeboard.redraw_klossy.push_change()
    
    def hover(self, x, y, hovered=[None]):
    
        self._hover_box_ij = (None, None)
        
        bb = self._stack_bisect(x, y)

        if self._items[bb].is_over_hover(x, y):
            self._hover_box_ij = (bb, self._items[bb].hover(x, y))

        if hovered[0] != self._hover_box_ij:
            hovered[0] = self._hover_box_ij
            noticeboard.redraw_klossy.push_change()


class Properties(_Properties_panel):
    def __init__(self, tabs = (), default=0, partition=1 ):
        self._reconstruct = self._reconstruct_text_properties
        
        _Properties_panel.__init__(self, tabs = tabs, default=default, partition=partition) 

    def _reconstruct_text_properties(self):
        # ALWAYS REQUIRES CALL TO _stack()
        print('reconstruct')

        p = meredith.mipsy.glyph_at()[2]
        
        self._items = [self._tabstrip]
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        y = 145
        
        self._items.append(kookies.Heading( 15, 90, 250, 30, p[0][0] + ':' + p[0][1], upper=True))
        
        if self._tab == 'font':
            self._items.append(kookies.Unordered( 15, y, 250, 200,
                        dict_acquire=lambda: fonts.p_get_attribute('fontclasses', p[0])[1], 
                        protect = set(((),)),
                        new = lambda L: (('{new}',), None),
                        display = lambda l: ', '.join(l) if l else '{none}',
                        before=un.history.save, after=self.synchronize, after_delete=self._TURNOVER_WITH_RERENDER_F))
            """      
            for key, item in sorted(fonts.get_fontclasses(p[0]).items()):
                if key:
                    classname = 'Class: ' + ', '.join(key)
                else:
                    classname = 'Class: none'
                
                self._items.append(_preview( 16, y, 250, 0, classname, p, key ))
                
                if fonts.f_read_f(p[0], key)[0]:
                    self._items.append(_Inheritance_selection_menu( 15, y + 20, width=250, p=p[0], f=key, attribute='_all', source=self._partition))
                    y += 50
                else:
                    self._items.append(_Inheritance_selection_menu( 15, y + 3, width=250, p=p[0], f=key, attribute='_all', source=self._partition))
                    y += 30
                    
                    self._items.append(_Font_file_Field( 15, y, 250, p[0], key, name='FONT FILE' ))
                    y += 30
                    self._items.append(_Inheritance_selection_menu( 15, y, width=250, p=p[0], f=key, attribute='path', source=self._partition))
                    y += 15
                    
                    self._items.append(_Font_numeric_Field( 15, y, 250, p[0], key, attribute='fontsize', name='FONT SIZE' ))
                    y += 30
                    self._items.append(_Inheritance_selection_menu( 15, y, width=250, p=p[0], f=key, attribute='fontsize', source=self._partition))
                    y += 15
                    
                    self._items.append(_Font_numeric_Field( 15, y, 250, p[0], key, attribute='tracking', name='TRACKING' ))
                    y += 30
                    self._items.append(_Inheritance_selection_menu( 15, y, width=250, p=p[0], f=key, attribute='tracking', source=self._partition))
                    y += 30

            """
                 
        elif self._tab == 'paragraph':
            self._items.append(_Paragraph_style_menu( 15, y, 250, p[0], name='RENAME CLASS', source=self._partition))
            y += 45

            self._items.append(create_p_field(kookies.Numeric_field, 15, y, 250, 'leading', p[0], after=self._TURNOVER_WITH_RERENDER_P, name='LEADING') )
            y += 30
            self._items.append(_Paragraph_inheritance_menu( 15, y, width=250, p=p[0], attribute='leading', source=self._partition))

            y += 15
            _tc_ = [_Paragraph_INDENT_EXP( 15, y, 175, p[0], after=self._TURNOVER_WITH_RERENDER_P, name='INDENT' ), 
                    create_p_field(kookies.Enumerate_field, 200, y, 65, 'indent_range', p[0], after=self._TURNOVER_WITH_RERENDER_P, 
                            value_acquire = lambda A, p: str(sorted(fonttable.p_table.get_paragraph(p)[A]))[1:-1], 
                            name='FOR LINES') ]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_

            y += 45
            _tc_ = [_Paragraph_inheritance_menu( 15, y, width=175, p=p[0], attribute='indent', source=self._partition), 
                    _Paragraph_inheritance_menu( 200, y, width=65, p=p[0], attribute='indent_range', source=self._partition) ]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_

            y += 15
            _tc_ = [create_p_field(kookies.Numeric_field, 15, y, 120, 'margin_left', p[0], after=self._TURNOVER_WITH_RERENDER_P, name='LEFT MARGIN'),
                    create_p_field(kookies.Numeric_field, 145, y, 120, 'margin_right', p[0], after=self._TURNOVER_WITH_RERENDER_P, name='RIGHT MARGIN')]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_
            y += 45
            _tc_ = [_Paragraph_inheritance_menu( 15, y, width=120, p=p[0], attribute='margin_left', source=self._partition), 
                    _Paragraph_inheritance_menu( 145, y, width=120, p=p[0], attribute='margin_right', source=self._partition) ]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_

            y += 15
            _tc_ = [create_p_field(kookies.Numeric_field, 15, y, 120, 'margin_top', p[0], after=self._TURNOVER_WITH_RERENDER_P, name='TOP MARGIN'),
                    create_p_field(kookies.Numeric_field, 145, y, 120, 'margin_bottom', p[0], after=self._TURNOVER_WITH_RERENDER_P, name='BOTTOM MARGIN')]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_

            y += 45
            _tc_ = [_Paragraph_inheritance_menu( 15, y, width=120, p=p[0], attribute='margin_top', source=self._partition), 
                    _Paragraph_inheritance_menu( 145, y, width=120, p=p[0], attribute='margin_bottom', source=self._partition) ]
            self._items.append( _TWO_COLUMN( * _tc_))
            self._items += _tc_

            y += 15
            self._items.append(create_p_field(kookies.Checkbox, 15, y + 15, 100, 'hyphenate', p[0], after=self._TURNOVER_WITH_RERENDER_P, 
                            value_acquire = lambda A, p: fonttable.p_table.get_paragraph(p)[A], 
                            name='HYPHENATE') )
            y += 30
            self._items.append(_Paragraph_inheritance_menu( 15, y, width=250, p=p[0], attribute='hyphenate', source=self._partition))

            y += 30
            self._items.append(kookies.Orderable( 15, y, 200, 180,
                        list_acquire=lambda: fonts.TAGS[fonts.paragraph_classes[p[0]]['tags']], 
                        new = lambda L: {'name': '{new}', 'exclusive': 'False'},
                        display = lambda l: l['name'],
                        before=un.history.save, after=self.synchronize ))
            y += 180
            self._items.append(kookies.Blank_space(15, y, width=250, 
                    callback=fonts.q_set, 
                    value_acquire=fonts.q_read, 
                    params = ('name', p[0]), before=un.history.save, after=self.synchronize, name='TAG NAME'))

            y += 45
            self._items.append(kookies.Checkbox( 15, y + 15, 100, callback=fonts.q_set, 
                            value_acquire = fonts.q_read, params = ('exclusive', p[0]),
                            before = un.history.save,
                            after = self._TURNOVER_WITH_RERENDER_P,
                            name = 'EXCLUSIVE') )

        elif self._tab == 'page':
            self._items.append(kookies.Integer_field( 15, y, 250, 
                        callback = penclick.page.set_width,
                        value_acquire = lambda: str(penclick.page.WIDTH),
                        name = 'WIDTH' ))
            
            y += 45
            self._items.append(kookies.Integer_field( 15, y, 250,
                        callback = penclick.page.set_height,
                        value_acquire = lambda: str(penclick.page.HEIGHT),
                        name = 'HEIGHT' ))

        self._stack()

    def _reconstruct_channel_properties(self):
        # ALWAYS REQUIRES CALL TO _stack()
        c = meredith.mipsy.C()
        
        self._items = [self._tabstrip]
        self._active_box_i = None
        self._hover_box_ij = (None, None)
        
        y = 145
        
        self._items.append(kookies.Heading( 15, 90, 250, 30, 'Channel ' + str(c), upper=True))
        
        if self._tab == 'channels':
            if c is not None:
                self._items.append(kookies.Integer_field( 15, y, 250, 
                        callback = meredith.mipsy.change_channel_page, 
                        params = (c,),
                        value_acquire = lambda: str(meredith.mipsy.tracts[0].channels.channels[c].page),
                        name = 'PAGE' ))
                y += 30
            
        self._stack()
        
    def _swap_reconstruct(self, to):
        width = 140

        if to == 'text':
            tabs = (('page', 'M'), ('paragraph', 'P'), ('font', 'F'), ('', '?'))
            default = 1
            self._tabstrip = kookies.Tabs( (constants.window.get_h() - constants.UI[self._partition] - width)//2 , 50, width, 30, default=default, callback=self._tab_switch, signals=tabs)
            self._tab = tabs[default][0]
            self._reconstruct = self._reconstruct_text_properties

        elif to == 'channels':
            tabs = (('channels', 'C'), ('', '?'))
            default = 0
            self._tabstrip = kookies.Tabs( (constants.window.get_h() - constants.UI[self._partition] - width)//2 , 50, width, 30, default=default, callback=self._tab_switch, signals=tabs)
            self._tab = tabs[default][0]
            self._reconstruct = self._reconstruct_channel_properties
        
        self._reconstruct()


klossy = Properties(tabs = (('page', 'M'), ('paragraph', 'P'), ('font', 'F'), ('', '?')), default=1, partition=1 )

