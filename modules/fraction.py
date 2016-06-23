from math import sqrt

from layout.otline import cast_mono_line

from meredith.box import Box, Inline

_namespace = 'mod:frac'

class Numerator(Box):
    name = _namespace + ':n'
    textfacing = True

class Denominator(Box):
    name = _namespace + ':d'
    textfacing = True
    
class Fraction(Inline):
    name = _namespace
    
    DNA = [('cl_fraction', 'texttc', '')]
    
    def _load(self):
        self._numerator, self._denominator = self.find_nodes(Numerator, Denominator)

    def _draw_vinculum(self, cr):
        cr.set_source_rgba( * self._color)
        cr.rectangle(0, 0, self._fracwidth, 0.5)
        cr.fill()
        
    def _cast_inline(self, LINE, x, y, runinfo, F, FSTYLE):
        self._color = FSTYLE['color']
        if self['cl_fraction']:
            F_fraction = F + self['cl_fraction']
        else:
            F_fraction = F
        
        ascent, descent = FSTYLE.vmetrics()
        vy = int(FSTYLE['fontsize'] * 0.25)
        
        numerator = cast_mono_line(LINE, self._numerator.content, runinfo, F_fraction)
        denominator = cast_mono_line(LINE, self._denominator.content, runinfo, F_fraction)
        
        gapline = cast_mono_line(LINE, [], runinfo, F_fraction)
        vgap = int(gapline['fstyle']['fontsize'] * 0.15)
        
        fracwidth = max(numerator['advance'], denominator['advance'])
        fracwidth = fracwidth + LINE['leading']*0.05 + sqrt(fracwidth)*LINE['leading']*0.05
        
        numerator['x'] = x + (fracwidth - numerator['advance'])/2
        numerator['y'] = y - vy - vgap + numerator['descent']
        
        denominator['x'] = x + (fracwidth - denominator['advance'])/2
        denominator['y'] = y - vy + vgap + denominator['ascent']
        
        fascent = vy + vgap+ numerator['ascent'] - numerator['descent']
        fdescent = vy - vgap - denominator['ascent'] + denominator['descent']
        self._fracwidth = fracwidth
        return [numerator, denominator], fracwidth, fascent, fdescent, (self._draw_vinculum, x, y - vy)

members = [Fraction, Numerator, Denominator]
