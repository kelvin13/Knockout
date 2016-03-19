from model.cat import cast_mono_line, calculate_vmetrics
from elements.elements import Inline_element, Node
from model.olivia import Inline

_namespace = 'mod:root'

class Index(Node):
    name = _namespace + ':i'
    textfacing = True

class Radicand(Node):
    name = _namespace + ':rad'
    textfacing = True

class Root(Inline_element):
    name = _namespace
    DNA = {'index': {}, 'radicand': {}}
    documentation = [(0, name), (1, 'index'), (1, 'radicand')]
    
    def _load(self):
        self._index, self._radicand = self.find_nodes(Index, Radicand)
    
    def _draw_radix(self, cr):
        cr.set_source_rgba( * self._color )
        cr.move_to(self._radix[0][0], self._radix[0][1])
        for u, v in self._radix[1:]:
            cr.line_to(u, v)
        cr.close_path()
        cr.fill()
    
    def cast_inline(self, LINE, x, y, PP, F, FSTYLE):
        self._color = FSTYLE['color']
        y += FSTYLE['shift']
        
        F_index, F_rad = self.styles(F, 'index', 'radicand')

        index = cast_mono_line(LINE, self._index.content, 13, PP, F_index)
        rad = cast_mono_line(LINE, self._radicand.content, 13, PP, F_rad)
        
        rad_asc, rad_desc = calculate_vmetrics(rad)

        k = x + index['advance']
        
        rfs = FSTYLE['fontsize']
        iy = y - rfs * 0.44 - FSTYLE['shift']
        ix = k - rfs * 0.30
        jx = ix - rad_desc * 0.4
        kx = jx + (rad_asc - rad_desc)*0.3
        
        index['x'] = x
        index['y'] = y - rfs * 0.6
        
        rad['x'] = k + rfs * 0.35
        rad['y'] = y

        self._radix = [(ix - rfs*0.050, iy),
                (ix + rfs*0.105, iy - rfs*0.02), #crest
                (ix + rfs*0.14, iy + rfs*0.08),
                (jx + rfs*0.135, y - rad_desc - rfs*0.35), # inner vertex
                (kx + rfs*0.05, y - rad_asc - rfs*0.04),
                
                (kx + rad['advance'] + rfs*0.45, y - rad_asc - rfs*0.04), # overbar
                (kx + rad['advance'] + rfs*0.445, y - rad_asc),
                
                (kx + rfs*0.09, y - rad_asc),
                (jx + rfs*0.15, y - rad_desc - rfs*0.24), # outer vertex
                (jx + rfs*0.08, y - rad_desc - rfs*0.24), # outer vertex
                (ix + rfs*0.06, iy + rfs*0.15),
                (ix + rfs*0.010, iy + rfs*0.04), # lip
                (ix - rfs*0.050, iy + rfs*0.03),
                ]
        
        index['x'] = x
        index['y'] = y - rfs * 0.6
        
        rad['x'] = kx + rfs * 0.30
        rad['y'] = y
        
        width = kx - x + rfs * 0.45 + rad['advance']
        
        return _MInline([index, rad], width, rad_asc + rfs*0.2, rad_desc, self._draw_radix)
        
    def __len__(self):
        return 8

class _MInline(Inline):
    def __init__(self, lines, width, A, D, draw):
        Inline.__init__(self, lines, width, A, D)
        self._draw = draw

    def deposit_glyphs(self, repository, x, y):
        for line in self._LINES:
            line.deposit(repository, x, y)
        repository['_paint'].append((self._draw, x, y))

members = [Root, Index, Radicand]
inline = True
