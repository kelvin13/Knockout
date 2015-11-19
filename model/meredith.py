from model import olivia
from model import george

class Meredith(object):
    def __init__(self):
        self.tracts = []
        self.page_context = 0
        self.hover_page_context = 0
        
        self.page_grid = [[], []]
        
    def reinit(self, kitty):
        self.tracts = [olivia.Text(k['text'], george.Washington([george.Swimming_pool( * c ) for c in k['outline']]), * k['cursors'] ) for k in kitty if k['outline']]
        self.t = 0
        self.rerender()
            
    def rerender(self):
        for tr in self.tracts:
            tr.deep_recalculate()
        
    def set_page_context(self, y):
        self.page_context = int((y + 50)//1100)
    def set_hover_page_context(self, y):
        self.hover_page_context = int((y + 50)//1100)
    
    def Y(self, y):
        return y - self.page_context*1100
    def Y_hover(self, y):
        return y - self.hover_page_context*1100
    
    def target_channel(self, x, y, radius):
            
        # try local
        c_local = self.tracts[self.t].channels.target_channel(x, y, self.page_context, radius)
        
        if c_local is None:
            for t, tract in enumerate(self.tracts):
                c = tract.channels.target_channel(x, y, self.page_context, radius)
                if c is not None:
                    return t, c

        return self.t, c_local
    
    def target_channel_c(self, x, y, radius):
        return self.tracts[self.t].channels.target_channel(x, y, self.page_context, radius)
    
    def set_t(self, tindex):
        self.t = tindex

    def set_cursor(self, t, i):
        self.tracts[t].cursor.set_cursor(
                i,
                self.tracts[t].text
                )

    def lookup_xy(self, t, c, x, y):
        return self.tracts[t].target_glyph(x, y, c=c)
            
    def set_cursor_xy(self, x, y, c=None):
        self.tracts[self.t].cursor.set_cursor(
                self.lookup_xy(self.t, c, x, y),
                self.tracts[self.t].text
                )
        
    def set_select_xy(self, x, y, c=None):
        self.tracts[self.t].select.set_cursor(
                self.lookup_xy(self.t, c, x, y),
                self.tracts[self.t].text
                )
    
    def select_all(self):
        self.tracts[self.t].expand_cursors()
    def select_word(self):
        self.tracts[self.t].expand_cursors_word()
    
    def text(self):
        return self.tracts[self.t].text
    
    def selection(self):
        return self.tracts[self.t].cursor.cursor, self.tracts[self.t].select.cursor

    def at_absolute(self, i):
        return self.tracts[self.t].text[i]
    
    def glyph_at(self, relativeindex=0):
        return self.tracts[self.t].text_index_location(self.tracts[self.t].cursor.cursor + relativeindex)
            
    def match_cursors(self):
        self.tracts[self.t].select.cursor = self.tracts[self.t].cursor.cursor
    
    def hop(self, dl):
        self.tracts[self.t].cursor.set_cursor(
                self.tracts[self.t].target_glyph(
                        self.tracts[self.t].text_index_location(self.tracts[self.t].cursor.cursor)[0], 
                        0, 
                        self.tracts[self.t].index_to_line(self.tracts[self.t].cursor.cursor) + dl
                        ), 
                self.tracts[self.t].text)
        
    def add_channel(self):
        self.tracts[self.t].channels.add_channel()
        self.rerender()
    
    def add_tract(self):
        self.tracts.append( comp.Text('<p>{new}</p>', channels.Channels([self.tracts[-1].channels.generate_channel()]), 1, 1 ) )
        self.t = len(self.tracts) - 1
        self.rerender()
    
    def rename_paragraph_class(self, old, new):
        for tract in self.tracts:
            tract.text[:] = [('<p>', new) if e == ('<p>', old) else e for e in tract.text]

    def change_paragraph_class(self, i, po):
        self.tracts[self.t].text[i] = ('<p>', po)
    
    def change_channel_page(self, page, c):
        self.tracts[self.t].channels.channels[c].set_page(page)
        self.rerender()
            
    def stats(self, spell=False):
        self.tracts[self.t].stats(spell)

mipsy = Meredith()
