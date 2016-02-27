import bisect
from itertools import groupby

from libraries.pyphen import pyphen
from bulletholes.counter import TCounter as Counter
from model.george import Swimming_pool
from style import styles
from elements.elements import Paragraph, OpenFontpost, CloseFontpost, Block_element
pyphen.language_fallback('en_US')
hy = pyphen.Pyphen(lang='en_US')

# linebreaking characters
_BREAK_WHITESPACE = set((' '))
_BREAK_ONLY_AFTER = set('-')
_BREAK_AFTER_ELSE_BEFORE = set('–—')

_BREAK = _BREAK_WHITESPACE | _BREAK_ONLY_AFTER | _BREAK_AFTER_ELSE_BEFORE

_BREAK_P = _BREAK | set(('</p>',))

_APOSTROPHES = set("'’")

class Glyphs_line(dict):
    def I(self, x, y):
        x -= self['x']
        y -= self['y']
        i = bisect.bisect(self['_X_'], x)
        if i:
            try:
                # compare before and after glyphs
                x1, x2 = self['_X_'][i - 1 : i + 1]
                if x2 - x > x - x1:
                    i -= 1
            except ValueError:
                i -= 1
    # glyphline is root, index
        return i + self['i']

    def deposit(self, repository, x=0, y=0):
        x += self['x']
        y += self['y']
        PP = self['PP']

        if self['hyphen'] is not None:
            glyphs = self['GLYPHS'] + [self['hyphen']]
        else:
            glyphs = self['GLYPHS']
        
        for glyph in glyphs:
            if glyph[0] < 0:
                if glyph[0] == -6:
                    repository['_annot'].append( (glyph[0], x, y + self['leading'], PP, glyph[3]))
                elif glyph[0] == -89:
                    glyph[6].deposit_glyphs(repository, x, y)
                else:
                    repository['_annot'].append((glyph[0], glyph[1] + x, glyph[2] + y, PP, glyph[3]))
            else:
                K = (glyph[0], glyph[1] + x, glyph[2] + y)
                N = glyph[3]['hash']
                try:
                    repository[N][1].append(K)
                except KeyError:
                    repository[N] = (glyph[3], [K])

class _LContainer(Swimming_pool):
    def __init__(self, SP):
        Swimming_pool.__init__(self, SP.railings, SP.page)
    
    def bounds(self, y):
        return self.edge(0, y)[0], self.edge(1, y)[0]

class _Margined_LContainer(Swimming_pool):
    def __init__(self, SP, left, right):
        Swimming_pool.__init__(self, SP.railings, SP.page)
        self._left = left
        self._right = right
    
    def bounds(self, y):
        return self.edge(0, y)[0] + self._left, self.edge(1, y)[0] - self._right

def typeset_chained(channels, LIQUID, c=0, y=None, LASTLINE = Glyphs_line({'j': 0, 'l': -1, 'P_BREAK': True})):
    SLUGS = []
    rchannels = channels[c:]
    rlen = len(rchannels) - 1
    c_leak = False
    for c_number, channel in enumerate(_LContainer(rc) for rc in rchannels):
        i = LASTLINE['j']
        if i >= len(LIQUID):
            break
        if y is None:
            y = channel.railings[0][0][1]
        if c_number == rlen:
            c_leak = True
        SLUGS += typeset_liquid(channel, LIQUID, LASTLINE, i, y, c_number + c, c_leak, root=True)
        y = None
        
        if SLUGS:
            LASTLINE = SLUGS[-1]

    return SLUGS

def typeset_liquid(channel, LIQUID, INIT, i, y, c, c_leak, root=False, overlay=None):
    SLUGS = []
    l = INIT['l'] + 1
    if INIT['P_BREAK']:
        gap = True
    else:
        PP = INIT['PP']
        PP.I_ = overlay
        F = INIT['F'].copy()
        R = INIT['R'] + 1
        PSTYLE = styles.PARASTYLES.project_p(PP)
        gap = False
    
    page = channel.page

    while True:
        if gap:
            try:
                i, container = next((a + i, v) for a, v in enumerate(LIQUID[i:]) if isinstance(v, (Paragraph, Block_element)))
            except StopIteration:
                # end of file
                break
            if type(container) is Paragraph:
                PP = container
                PP.I_ = overlay
                PSTYLE = styles.PARASTYLES.project_p(PP)
                
                F = Counter()
                R = 0
                
                if l != INIT['l'] + 1: # prevent accumulating y error
                    y += PSTYLE['margin_top']
                y += PSTYLE['leading']

                gap = False

            else:
                PSTYLE = styles.PARASTYLES.project_p(container.PP)
                y += PSTYLE['margin_top']
                try:
                    MOD = container.typeset(_Margined_LContainer(channel, PSTYLE['margin_left'], PSTYLE['margin_right']), c, y, overlay)
                    # see if the lines have overrun the portal
                    if MOD['y'] > channel.railings[1][-1][1] and not c_leak:
                        raise RuntimeError
                except RuntimeError:
                    break

                MOD['i'] = i
                MOD['j'] = i + 1
                MOD['l'] = l
                MOD['c'] = c
                MOD['page'] = page
                y = MOD['y']
                
                SLUGS.append(MOD)
                l += 1
                i += 1
                y += PSTYLE['margin_bottom']
                continue
        else:
            y += PSTYLE['leading']
        
        # see if the lines have overrun the portal
        if y > channel.railings[1][-1][1] and not c_leak:
            if not root:
                raise RuntimeError
            break
            
        x1, x2 = channel.bounds(y)

        # calculate indentation
        if R in PSTYLE['indent_range']:
            D, SIGN, K = PSTYLE['indent']
            if K:
                INDLINE = cast_mono_line({'R': R, 'l': l, 'c': c, 'page': page},
                    LIQUID[i : i + K + (not bool(R))], 
                    0,
                    PP,
                    F.copy()
                    )
                L_indent = PSTYLE['margin_left'] + D + INDLINE['advance'] * SIGN
            else:
                L_indent = PSTYLE['margin_left'] + D
        else:
            L_indent = PSTYLE['margin_left']
        
        R_indent = PSTYLE['margin_right']

        # generate line objects
        x1 += L_indent
        x2 -= R_indent
        if x1 > x2:
            x1, x2 = x2, x1
        # initialize line                               R: line number (within paragraph)
        LINE = Glyphs_line({'hyphen': None, 'P_BREAK': False, 'R': R, 'left': x1, 'y': y, 'l': l, 'c': c, 'page': page})
        cast_liquid_line(LINE,
                LIQUID[i : i + 1989], 
                i, 
                
                x2 - x1, 
                PSTYLE['leading'],
                PP,
                F.copy(), 
                
                hyphenate = PSTYLE['hyphenate']
                )

        # alignment
        if PSTYLE['align_to'] and LINE['GLYPHS']:
            searchtext = LIQUID[i : i + len(LINE['GLYPHS'])]
            ai = -1
            for aligner in '\t' + PSTYLE['align_to']:
                try:
                    ai = searchtext.index(aligner)
                    break
                except ValueError:
                    continue
            anchor = x1 + (x2 - x1) * PSTYLE['align']
            LINE['x'] = anchor - LINE['_X_'][ai]
        else:
            if not PSTYLE['align']:
                LINE['x'] = x1
            else:
                rag = LINE['width'] - LINE['advance']
                LINE['x'] = x1 + rag * PSTYLE['align']

        l += 1
        SLUGS.append(LINE)

        # get the index of the last glyph printed so we know where to start next time
        i = LINE['j']
        
        if LINE['P_BREAK']:
            y += PSTYLE['margin_bottom']
            gap = True
        else:
            F = LINE['F']
            R += 1

    return SLUGS

def cast_liquid_line(LINE, letters, startindex, width, leading, PP, F, hyphenate=False):
    LINE['i'] = startindex
    LINE['width'] = width
    LINE['leading'] = leading
    LINE['F'] = F
    LINE['PP'] = PP
    
    # list that contains glyphs
    GLYPHS = []

    # retrieve font style
    fstat = F.copy()
    FSTYLE = styles.PARASTYLES.project_f(PP, F)
    x = 0
    y = -FSTYLE['shift']
    caps = FSTYLE['capitals']
    glyphwidth = 0

    for letter in letters:
        CT = type(letter)
        if CT is str:
            if letter == '</p>':
                LINE['P_BREAK'] = True
                GLYPHS.append((-3, x, y, FSTYLE, fstat, x))
                break
            
            elif letter == '<br/>':
                GLYPHS.append((-6, x, y, FSTYLE, fstat, x))
                break
            else: # regular letter
                if caps:
                    letter = letter.upper()
                glyphwidth = FSTYLE['fontmetrics'].advance_pixel_width(letter) * FSTYLE['fontsize']
                GLYPHS.append((
                        FSTYLE['fontmetrics'].character_index(letter),  # 0
                        x,                                              # 1
                        y,                                              # 2
                        
                        FSTYLE,                                         # 3
                        fstat,                                          # 4
                        x + glyphwidth                                  # 5
                        ))
        
        elif CT is OpenFontpost:
            T = letter.F
            TAG = T.name
            
            # increment tag count
            F[T] += 1
            fstat = F.copy()
            
            FSTYLE = styles.PARASTYLES.project_f(PP, F)
            y = -FSTYLE['shift']
            caps = FSTYLE['capitals']
            
            GLYPHS.append((-4, x, y, FSTYLE, fstat, x))
            continue
            
        elif CT is CloseFontpost:
            GLYPHS.append((-5, x, y, FSTYLE, fstat, x))
            
            T = letter.F
            TAG = T.name
            
            # increment tag count
            F[T] -= 1
            fstat = F.copy()
            
            FSTYLE = styles.PARASTYLES.project_f(PP, F)
            y = -FSTYLE['shift']
            caps = FSTYLE['capitals']
            continue
            
        elif CT is Paragraph:
            if GLYPHS:
                break
            else:
                # we don’t load the style because the outer function takes care of that
                GLYPHS.append((
                        -2,                      # 0
                        x - leading,             # 1
                        y,                       # 2
                        
                        FSTYLE,                  # 3
                        fstat,                   # 4
                        x - leading              # 5
                        ))
                continue
        
        else:
            try:
                inline = letter.cast_inline(LINE, x, y, PP, F, FSTYLE)
                glyphwidth = inline.width                               #6. object
                GLYPHS.append((-89, x, y, FSTYLE, fstat, x + glyphwidth, inline))
            except AttributeError:
                glyphwidth = leading
                GLYPHS.append((-23, x, y, FSTYLE, fstat, x + leading))
        
        x += glyphwidth

        # work out line breaks
        if x > width:
            n = len(GLYPHS)
            CHAR = str(letter)
            if CHAR not in _BREAK_WHITESPACE:

                LN = letters[:n]

                try:
                    if CHAR in _BREAK_ONLY_AFTER:
                        i = next(i + 1 for i, v in zip(range(n - 2, 0, -1), reversed(LN[:-1])) if str(v) in _BREAK)
                    elif CHAR in _BREAK_AFTER_ELSE_BEFORE:
                        i = len(LN) - 1
                    else:
                        i = n - next(i for i, v in enumerate(reversed(LN)) if str(v) in _BREAK)
                
                except StopIteration:
                    del GLYPHS[-1]
                    i = 0
                
                ### AUTO HYPHENATION
                if hyphenate:
                    try:
                        j = i + next(i for i, v in enumerate(letters[i:]) if v in _BREAK_P)
                    except StopIteration:
                        j = i + 1989
                    except TypeError:
                        j = i
                    
                    word = ''.join(c if len(c) == 1 and c.isalpha() else "'" if c in _APOSTROPHES else ' ' for c in letters[i:j])

                    leading_spaces = len(word) - len(word.lstrip(' '))

                    for pair in hy.iterate(word.strip(' ')):
                        k = len(pair[0]) + leading_spaces
                        # no sense checking hyphenations that don’t fit
                        if k >= n - i:
                            continue
                        # prevent too-short hyphenations
                        elif len(pair[0].replace(' ', '')) < 2 or len(pair[1].replace(' ', '')) < 2:
                            continue
                        
                        # check if the hyphen overflows
                        HG = GLYPHS[i - 1 + k]
                        HFS = HG[3]
                        h_F = HG[4]
                        
                        if HG[5] + HFS['fontmetrics'].advance_pixel_width('-') * HFS['fontsize'] <= width:
                            i = i + k
                            LINE['hyphen'] = (
                                    HFS['fontmetrics'].character_index('-'), 
                                    HG[5], # x
                                    HG[2], # y
                                    HFS,
                                    h_F)
                            break
                ####################
                if i:
                    del GLYPHS[i:]

            elif letters[n] == '</p>':
                continue
            break
            
        else:
            x += FSTYLE['tracking']

    LINE['j'] = startindex + len(GLYPHS)
    LINE['GLYPHS'] = GLYPHS
    LINE['fstyle'] = FSTYLE
    # cache x's
    LINE['_X_'] = [g[1] for g in GLYPHS]

    try:
        LINE['F'] = GLYPHS[-1][4]
        LINE['advance'] = GLYPHS[-1][5]
    except IndexError:
        LINE['advance'] = 0

def cast_mono_line(PARENT, letters, leading, PP, F):
    F = F.copy()
    LINE = Glyphs_line({
            'i': 0,
      
            'leading': leading,
            
            'F': F,
            'PP': PP,
            
            'hyphen': None,
            
            'R': PARENT['R'], 
            'l': PARENT['l'], 
            'c': PARENT['c'], 
            'page': PARENT['page']
            })
    
    # list that contains glyphs
    GLYPHS = []

    # retrieve font style
    fstat = F.copy()
    FSTYLE = styles.PARASTYLES.project_f(PP, F)
    x = 0
    y = -FSTYLE['shift']
    caps = FSTYLE['capitals']
    glyphwidth = 0

    for letter in letters:
        CT = type(letter)
        if CT is OpenFontpost:
            T = letter.F
            TAG = T.name
            
            # increment tag count
            F[T] += 1
            fstat = F.copy()
            
            FSTYLE = styles.PARASTYLES.project_f(PP, F)
            y = -FSTYLE['shift']
            caps = FSTYLE['capitals']
            
            GLYPHS.append((-4, x, y, FSTYLE, fstat, x))
            
        elif CT is CloseFontpost:
            GLYPHS.append((-5, x, y, FSTYLE, fstat, x))
            
            T = letter.F
            TAG = T.name
            
            # increment tag count
            F[T] -= 1
            fstat = F.copy()
            
            FSTYLE = styles.PARASTYLES.project_f(PP, F)
            y = -FSTYLE['shift']
            caps = FSTYLE['capitals']
            
        elif CT is Paragraph:
            GLYPHS.append((
                    -2,                      # 0
                    x - leading,             # 1
                    y,                       # 2
                    
                    FSTYLE,                  # 3
                    fstat,                   # 4
                    x - leading              # 5
                    ))
        
        elif letter == '</p>':
            GLYPHS.append((-3, x, y, FSTYLE, fstat, x))
        
        elif letter == '<br/>':
            GLYPHS.append((-6, x, y, FSTYLE, fstat, x))

        else:
            if CT is str:
                if caps:
                    letter = letter.upper()
                glyphwidth = FSTYLE['fontmetrics'].advance_pixel_width(letter) * FSTYLE['fontsize']
                GLYPHS.append((
                        FSTYLE['fontmetrics'].character_index(letter),  # 0
                        x,                                              # 1
                        y,                                              # 2
                        
                        FSTYLE,                                         # 3
                        fstat,                                          # 4
                        x + glyphwidth                                  # 5
                        ))
            else:
                try:
                    inline = letter.cast_inline(LINE, x, y, PP, F, FSTYLE)
                    glyphwidth = inline.width                               #6. object
                    GLYPHS.append((-89, x, y, FSTYLE, fstat, x + glyphwidth, inline))
                except AttributeError:
                    glyphwidth = leading
                    GLYPHS.append((-23, x, y, FSTYLE, fstat, x + leading))
            
            x += glyphwidth + FSTYLE['tracking']

    LINE['j'] = len(GLYPHS)
    LINE['GLYPHS'] = GLYPHS
    LINE['fstyle'] = FSTYLE
    # cache x's
    LINE['_X_'] = [g[1] for g in GLYPHS]
    
    try:
        LINE['F'] = GLYPHS[-1][4]
        LINE['advance'] = GLYPHS[-1][5]
    except IndexError:
        LINE['advance'] = 0
    
    return LINE

def calculate_vmetrics(LINE):
    ascent, descent = LINE['fstyle'].vmetrics()
    
    if LINE['GLYPHS']:
        specials = [(glyph[6].ascent, glyph[6].descent) for glyph in LINE['GLYPHS'] if glyph[0] == -89]
        if specials:
            A, D = zip( * specials )
            ascent, descent = max(ascent, max(A)), min(descent, min(D))
    return ascent, descent
