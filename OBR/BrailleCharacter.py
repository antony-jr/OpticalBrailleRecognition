class BrailleCharacter(object):
    def __init__(self, dot_coordinates, diameter, radius, parent_image):
        self.left = None
        self.right = None
        self.top = None
        self.bottom = None
        self.dot_coordinates = dot_coordinates
        self.diameter = diameter
        self.radius = radius
        self.parent_image = parent_image
        return;

    def mark(self):
        self.parent_image.bound_box(self.left,self.right,self.top,self.bottom)
        return;

    def get_parent_image(self):
        return self.parent_image

    def get_dot_diameter(self):
        return self.diameter

    def get_dot_radius(self):
        return self.radius

    def get_dot_coordinates(self):
        return self.dot_coordinates

    def get_left(self):
        return self.left

    def get_right(self):
        return self.right

    def get_top(self):
        return self.top

    def get_bottom(self):
        return self.bottom

    def get_opencv_left_top(self):
        return (self.left, self.top)
        
    def get_opencv_right_bottom(self):
        return (self.right, self.bottom)

    def get_bounding_box(self, form = "left,right,top,bottom"):
        r = []
        form = form.split(',')
        if len(form) < 4:
            return (self.left,self.right,self.top,self.bottom)

        for direction in form:
            direction = direction.lower()
            if direction == 'left':
                r.append(self.left)
            elif direction == 'right':
                r.append(self.right)
            elif direction == 'top':
                r.append(self.top)
            elif direction == 'bottom':
                r.append(self.bottom)
            else:
                return (self.left,self.right,self.top,self.bottom)
        
        return tuple(r)

    def is_valid(self):
        r = True
        r = r and (self.left is not None)
        r = r and (self.right is not None)
        r = r and (self.top is not None)
        r = r and (self.bottom is not None)
        return r

