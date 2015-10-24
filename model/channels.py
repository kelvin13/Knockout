import bisect

class Channel(object):
    def __init__(self, left, right):
        # create two railings, the borders
        self.railings = [left, right]
    
    def _is_outside(self, y):
        location = True
        if ( self.railings[0][0][1] <= y <= self.railings[1][-1][1] ):
            location = False
        return location
                    
    def edge(self, r, y):
        i = bisect.bisect([point[1] for point in self.railings[r]], y)
        # if y if below the last point
        try:
            xbelow = self.railings[r][i][0]
        except IndexError:
            return self.railings[r][-1]
        xabove = self.railings[r][i - 1][0]
        factor = (y - self.railings[r][i - 1][1])/(self.railings[r][i][1] - self.railings[r][i - 1][1])
        # returns an x coordinate, and the index of the point
        return (xbelow - xabove)*factor + xabove , i
    
    def insert_point(self, r, y):
        y = 10*round(y/10)
        # make sure to only insert points between the portals
        if not self._is_outside(y):
            x, i = self.edge(r, y)
            x = 10*round(x/10)
            self.railings[r].insert(i, [x, y, True])
            return i
        else:
            return None
    
    def can_fall(self, x, y):
        if [x, y] in [p[:2] for p in self.railings[0] + self.railings[1]]:
            return False
        else:
            return True

    def fix(self, r):
        # removes points that are outside the portals
        self.railings[r][:] = [point for point in self.railings[r] if not self._is_outside(point[1])]
        # sort list
        self.railings[r].sort(key = lambda k: k[1])
    
    def target_portal(self, x, y, radius=0):
        portal = None
        if self.railings[0][0][1] - radius - 5 <= y <= self.railings[0][0][1] + radius:
            if self.railings[0][0][0] < x < self.railings[1][0][0]:
                portal = ('entrance', x - self.railings[0][0][0], y - self.railings[0][0][1])

        elif self.railings[0][-1][1] - radius <= y <= self.railings[0][-1][1] + radius + 5:
            if self.railings[0][-1][0] < x < self.railings[1][-1][0]:
                portal = ('portal', x - self.railings[1][-1][0], y - self.railings[1][-1][1])
        return portal
    
    
class Channels(object):
    def __init__(self, ic):
        self.channels = ic
 #####################   
    def target_channel(self, x, y, radius):
        for c, channel in enumerate(self.channels):
            if y >= channel.railings[0][0][1] - radius and y <= channel.railings[1][-1][1] + radius:
                if x >= channel.edge(0, y)[0] - radius and x <= channel.edge(1, y)[0] + radius:
                    return c
        return None
#######################
    def target_point(self, x, y, radius):
        cc, rr, ii = None, None, None
        for c in range(len(self.channels)):
            for r in range(len(self.channels[c].railings)):
                for i, point in enumerate(self.channels[c].railings[r]):
                    if abs(x - point[0]) + abs(y - point[1]) < radius:

                        return c, r, i
                # if that fails, take a railing, if possible
                if not self.channels[c]._is_outside(y) and abs(x - self.channels[c].edge(r, y)[0]) <= radius:
                    cc, rr, ii = c, r, None
        return cc, rr, ii
    
    def is_selected(self, c, r, i):
        try:
            return self.channels[c].railings[r][i][2]
        except TypeError:
            return False
    
    def make_selected(self, c, r, i):
        self.channels[c].railings[r][i][2] = True
        
    def clear_selection(self):
        for c in range(len(self.channels)):
            for r in range(len(self.channels[c].railings)):
                for point in self.channels[c].railings[r]:
                    point[2] = False

    def expand_selection(self, c):
        if c is None:
            self._select_all()
        else:
            touched = False
            for r in range(len(self.channels[c].railings)):
                for point in self.channels[c].railings[r]:
                    if not point[2]:
                        point[2] = True
                        touched = True
            if not touched:
                self._select_all()
    
    def _select_all(self):
        for c in range(len(self.channels)):
            for r in range(len(self.channels[c].railings)):
                for point in self.channels[c].railings[r]:
                    point[2] = True

    def delete_selection(self):
        for c in range(len(self.channels)):
            for r, railing in enumerate(self.channels[c].railings):
                railing[:] = [point for i, point in enumerate(railing) if not point[2] or (i == 0 or i == len(railing) - 1)]

    def translate_selection(self, x, y, xo, yo):
        x, y = 10*round(x/10), 10*round(y/10)
        
        safe = True
        
        # survey conditions
        for c in range(len(self.channels)):
            for r in range(len(self.channels[c].railings)):
                for i, point in enumerate(self.channels[c].railings[r]):
                    if point[2]:
                        # do any of the points fall on another point?
                        if not self.channels[c].can_fall(x = point[0] + x - xo, y = point[1] + y - yo):
                            safe = False

        if safe:
            for c in range(len(self.channels)):
                for r in range(len(self.channels[c].railings)):
                    for i, point in enumerate(self.channels[c].railings[r]):
                        if point[2]:
                            self.channels[c].railings[r][i] = [point[0] + x - xo, point[1] + y - yo, True]
                # check y alignment
                if self.channels[c].railings[0][0] [1] != self.channels[c].railings[1][0] [1]:
                    self.channels[c].railings[1][0] [1] = self.channels[c].railings[0][0] [1]

                if self.channels[c].railings[0][-1] [1] != self.channels[c].railings[1][-1] [1]:
                    self.channels[c].railings[0][-1] [1] = self.channels[c].railings[1][-1] [1]

    def generate_channel(self):
        x1, y1, x2 = self.channels[-1].railings[0][-1][0], self.channels[-1].railings[0][-1][1] + 40, self.channels[-1].railings[1][-1][0]
        return Channel( [[x1, y1, False], [x1, y1 + 40, False]], [[x2, y1, False], [x2, y1 + 40, False]] )
    
    def add_channel(self):
        self.channels.append(self.generate_channel())

