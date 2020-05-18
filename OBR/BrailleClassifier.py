from math import sqrt

def get_distance(p1, p2):
        x1,y1 = p1
        x2,y2 = p2
        return ((x2 - x1)**2) + ((y2 - y1)**2)

def get_left_nearest(dots, diameter, left):
        nearest = None
        for dot in dots:
            x,y = dot[0]
            dist = int(x - left)
            if dist <= diameter:
                if nearest is None:
                    nearest = dot
                else:
                    X,Y = nearest[0]
                    DIST = int(X - left)
                    if DIST > dist:
                        nearest = dot
        return nearest

def get_right_nearest(dots, diameter, right):
        nearest = None
        for dot in dots:
            x,y = dot[0]
            dist = int(right - x)
            if dist <= diameter:
                if nearest is None:
                    nearest = dot
                else:
                    X,Y = nearest[0]
                    DIST = int(right - X)
                    if DIST > dist:
                        nearest = dot
        return nearest

def get_dot_nearest(dots, diameter, pt1):
        nearest = None
        diameter **= 2
        for dot in dots:
            point = dot[0]
            dist_from_pt1 = get_distance(point, pt1)
            if dist_from_pt1 <= diameter:
                if nearest is None:
                    nearest = dot
                else:
                    pt = nearest[0]
                    ndist_from_pt1 = get_distance(pt, pt1)
                    if ndist_from_pt1 >= dist_from_pt1:
                        nearest = dot
        return nearest



def get_combination(box, dots, diameter):
        result = [0,0,0,0,0,0]
        left,right,top,bottom = box

        midpointY = int((bottom - top)/2)
        end = (right, midpointY)
        start = (left, midpointY)
        width = int(right - left)

        corners = { (left,top): 1, (right,top): 4, (left, bottom): 3, (right,bottom): 6,
                (left): 2, (right): 5}

        for corner in corners:
            if corner != left and corner != right:
                D = get_dot_nearest(dots, int(diameter), corner)
            else:
                if corner == left:
                    D = get_left_nearest(dots, int(diameter), left)
                else:
                    D = get_right_nearest(dots, int(diameter), right)

            if D is not None:
                dots.remove(D)
                result[corners[corner]-1] = 1

            if len(dots) == 0:
                break
        return end,start,width,tuple(result);

def translate_to_number(value):
    if value == 'a':
        return '1'
    elif value == 'b':
        return '2'
    elif value == 'c':
        return '3'
    elif value == 'd':
        return '4'
    elif value == 'e':
        return '5'
    elif value == 'f':
        return '6'
    elif value == 'g':
        return '7'
    elif value == 'h':
        return '8'
    elif value == 'i':
        return '9'
    else:
        return '0'

class Symbol(object):
    def __init__(self, value = None, letter = False, special = False):
        self.is_letter = letter
        self.is_special = special
        self.value = value

    def is_valid(self):
        r = True
        r = r and (self.value is not None)
        r = r and (self.is_letter is not None or self.is_special is not None)
        return r

    def letter(self):
        return self.is_letter

    def special(self):
        return self.is_special

class BrailleClassifier(object):
    symbol_table = {
         (1,0,0,0,0,0): Symbol('a',letter=True),
         (1,1,0,0,0,0): Symbol('b',letter=True),
         (1,0,0,1,0,0): Symbol('c',letter=True),
         (1,0,0,1,1,0): Symbol('d',letter=True),
         (1,0,0,0,1,0): Symbol('e',letter=True),
         (1,1,0,1,0,0): Symbol('f',letter=True),
         (1,1,0,1,1,0): Symbol('g',letter=True),
         (1,1,0,0,1,0): Symbol('h',letter=True),
         (0,1,0,1,0,0): Symbol('i',letter=True),
         (0,1,0,1,1,0): Symbol('j',letter=True),
         (1,0,1,0,0,0): Symbol('K',letter=True),
         (1,1,1,0,0,0): Symbol('l',letter=True),
         (1,0,1,1,0,0): Symbol('m',letter=True),
         (1,0,1,1,1,0): Symbol('n',letter=True),
         (1,0,1,0,1,0): Symbol('o',letter=True),
         (1,1,1,1,0,0): Symbol('p',letter=True),
         (1,1,1,1,1,0): Symbol('q',letter=True),
         (1,1,1,0,1,0): Symbol('r',letter=True),
         (0,1,1,1,0,0): Symbol('s',letter=True),
         (0,1,1,1,1,0): Symbol('t',letter=True),
         (1,0,1,0,0,1): Symbol('u',letter=True),
         (1,1,1,0,0,1): Symbol('v',letter=True),
         (0,1,0,1,1,1): Symbol('w',letter=True),
         (1,0,1,1,0,1): Symbol('x',letter=True),
         (1,0,1,1,1,1): Symbol('y',letter=True),
         (1,0,1,0,1,1): Symbol('z',letter=True),
         (0,0,1,1,1,1): Symbol('#',special=True),
    }
    def __init__(self):
        self.result = ''
        self.shift_on = False
        self.prev_end = None
        self.number = False
        return;

    def push(self, character):
        if not character.is_valid():
            return;
        box = character.get_bounding_box()
        dots = character.get_dot_coordinates()
        diameter = character.get_dot_diameter()
        end,start,width,combination = get_combination(box, dots, diameter)

        if combination not in self.symbol_table:
            self.result += "*"
            return;

        if self.prev_end is not None:
            dist = get_distance(self.prev_end, start)
            if dist*0.5 > (width**2):
                self.result += " "
        self.prev_end = end

        symbol = self.symbol_table[combination]
        if symbol.letter() and self.number:
            self.number = False
            self.result += translate_to_number(symbol.value)
        elif symbol.letter():
            if self.shift_on:
                self.result += symbol.value.upper()
            else:
                self.result += symbol.value
        else:
            if symbol.value == '#':
                self.number = True
        return;

    def digest(self):
        return self.result

    def clear(self):
        self.result = ''
        self.shift_on = False
        self.prev_end = None
        self.number = False
        return;
