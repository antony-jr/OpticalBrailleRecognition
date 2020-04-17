try:
    import cv2
    import numpy as np
except:
    print("Please make sure you have installed: ")
    print(" 1. OpenCV 4.x or 3.x")
    print(" 2. Numpy (any version)")
    raise ImportError

from math import sqrt
from collections import Counter



class BrailleCharacter(object):
    def __init__(self,boundingBox, dots, diameter):
        self.result = [0,0,0,0,0,0]
        left,right,top,bottom = boundingBox

        midpointY = int((bottom - top)/2)
        self.end = (right, midpointY)
        self.start = (left, midpointY)
        self.width = int(right - left)

        corners = { (left,top): 1, (right,top): 4, (left, bottom): 3, (right,bottom): 6,
                (left): 2, (right): 5}

        for corner in corners:
            if corner != left and corner != right:
                D = self.__get_dot_nearest(dots, int(diameter), corner)
            else:
                if corner == left:
                    D = self.__get_left_nearest(dots, int(diameter), left)
                else:
                    D = self.__get_right_nearest(dots, int(diameter), right)

            if D is not None:
                dots.remove(D)
                self.result[corners[corner]-1] = 1

            if len(dots) == 0:
                break
        return;

    def digest(self):
        return tuple(self.result)

    def __get_distance(self, p1, p2):
        x1,y1 = p1
        x2,y2 = p2
        return ((x2 - x1)**2) + ((y2 - y1)**2)

    def __get_left_nearest(self, dots, diameter, left):
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

    def __get_right_nearest(self, dots, diameter, right):
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

    def __get_dot_nearest(self, dots, diameter, pt1):
        nearest = None
        diameter **= 2
        for dot in dots:
            point = dot[0]
            dist_from_pt1 = self.__get_distance(point, pt1)
            if dist_from_pt1 <= diameter:
                if nearest is None:
                    nearest = dot
                else:
                    pt = nearest[0]
                    ndist_from_pt1 = self.__get_distance(pt, pt1)
                    if ndist_from_pt1 >= dist_from_pt1:
                        nearest = dot
        return nearest

class OBR(object): 
    def __init__(self, image):
        # Read source image
        self.original = cv2.imread(image)
        if self.original is None:
            raise IOError('Cannot open given image')

        # First Layer, Convert BGR(Blue Green Red Scale) to Gray Scale
        gray = cv2.cvtColor(self.original, cv2.COLOR_BGR2GRAY)
        
        # Save the binary image of the edge detected 
        self.edged_binary_image = self.__get_edged_binary_image(gray)

        # Now do the same to save a binary image to get the contents
        # inside the edges to see if the dot is really filled.
        self.binary_image = self.__get_binary_image(gray)
        self.final = None
        return;

    def digest(self):
        def distance(p1, p2):
            x1,y1 = p1
            x2,y2 = p2
            return ((x2 - x1)**2) + ((y2 - y1)**2)

        characters = self.get_characters()
        result = ""
        self.final = self.original.copy()

        alpha = {
                (1,0,0,0,0,0): "A",
                (1,1,0,0,0,0): "B",
                (1,0,0,1,0,0): "C",
                (1,0,0,1,1,0): "D",
                (1,0,0,0,1,0): "E",
                (1,1,0,1,0,0): "F",
                (1,1,0,1,1,0): "G",
                (1,1,0,0,1,0): "H",
                (0,1,0,1,0,0): "I",
                (0,1,0,1,1,0): "J",
                (1,0,1,0,0,0): "K",
                (1,1,1,0,0,0): "L",
                (1,0,1,1,0,0): "M",
                (1,0,1,1,1,0): "N",
                (1,0,1,0,1,0): "O",
                (1,1,1,1,0,0): "P",
                (1,1,1,1,1,0): "Q",
                (1,1,1,0,1,0): "R",
                (0,1,1,1,0,0): "S",
                (0,1,1,1,1,0): "T",
                (1,0,1,0,0,1): "U",
                (1,1,1,0,0,1): "V",
                (0,1,0,1,1,1): "W",
                (1,0,1,1,0,1): "X",
                (1,0,1,1,1,1): "Y",
                (1,0,1,0,1,1): "Z",
                (0,0,1,1,1,1): "#"
        }

        prevEnd = None
        for character in characters:
            if character.digest() not in alpha:
                print(character.digest())
                result += ""
                continue
            if prevEnd is None:
                prevEnd = character.end
                dist = character.width
            else:
                dist = distance(prevEnd, character.start)
                prevEnd = character.end
            if dist > (character.width**2)*1.5:
                result += " "
            result += alpha[character.digest()]
        return result

    def get_characters(self):
        contours = self.__process_contours()
        if len(contours) == 0:
            return None # Since we have not dots.
        enclosingCircles = self.__get_min_enclosing_circles(contours)
        if len(enclosingCircles) == 0:
            return None

        diameter,dots,radius = self.__get_valid_dots(enclosingCircles)
        if len(dots) == 0:
            return None

        characters = []
        nextEpoch = 0
        height, width, channels = self.original.shape
        cor = (0,0)

        while True:
            cor = self.__get_row_cor(dots, epoch=nextEpoch) # do not respect breakpoints
            if cor is None:
                break

            top = int(cor[1] - int(radius*1.5)) # y coordinate
            nextEpoch = int(cor[1] + radius)

            cor = self.__get_row_cor(dots,nextEpoch,diameter,True)
            if cor is None:
                # Assume nextEpoch
                nextEpoch = int(nextEpoch + (2*diameter))
            else:
                nextEpoch = int(cor[1] + radius)

            cor = self.__get_row_cor(dots,nextEpoch,diameter,True)
            if cor is None:
                # Assume nextEpoch
                nextEpoch = int(nextEpoch + (2*diameter))
            else:
                nextEpoch = int(cor[1] + radius)
            bottom = nextEpoch
            nextEpoch += int(2*diameter)
            
            DOI = self.__get_dots_from_region(dots, top, bottom)
            xnextEpoch = 0
            while True:
                xcor = self.__get_col_cor(DOI, xnextEpoch)
                if xcor is None:
                    break

                left = int(xcor[0] - radius) # x coordinate
                xnextEpoch = int(xcor[0] + radius)
                xcor = self.__get_col_cor(DOI,xnextEpoch,diameter,True)
                if xcor is None:
                    # Assumed
                    xnextEpoch += int(diameter*1.5)
                else:
                    xnextEpoch = int(xcor[0]) + int(radius)
                right = xnextEpoch

                box = (left, right, top, bottom)
                dts = self.__get_dots_from_box(DOI, box)
                characters.append(BrailleCharacter(box, dts, diameter))
        return characters

    def show(self, quitKey = 27): # Esc to quit the window
        if self.final is not None:
            cv2.imshow('Binary Image', self.get_binary_image())
            cv2.imshow('Final Image' , self.final)
            print("Press {} Key on the Image window to quit.".format(quitKey))
            while True:
                if cv2.waitKey(30) == quitKey:
                    return True
            cv2.destroyAllWindows()
            return True

    def get_final_image(self):
        return self.final

    def get_original_image(self):
        return self.original

    def get_edged_binary_image(self):
        return self.edged_binary_image

    def get_binary_image(self):
        return self.binary_image

    def __get_edged_binary_image(self, gray):
        # First Lvl Blur to Reduce Noise
        blur = cv2.GaussianBlur(gray,(3,3),0)
        # Adaptive Thresholding to define the  dots in Braille
        thres = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,5,4) 
        # Remove more Noise from the edges.
        blur2 = cv2.medianBlur(thres,3)
        # Sharpen again.
        ret2,th2 = cv2.threshold(blur2,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        # Remove more Noise.
        blur3 = cv2.GaussianBlur(th2,(3,3),0)
        # Final threshold
        ret3,th3 = cv2.threshold(blur3,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return cv2.bitwise_not(th3)

    def __get_binary_image(self, gray):
        blur     = cv2.GaussianBlur(gray,(3,3),0)
        ret2,th2 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        blur2    = cv2.medianBlur(th2,3)
        ret3,th3 = cv2.threshold(blur2,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return cv2.bitwise_not(th3)

    def __get_row_cor(self, dots, epoch = 0, diameter = 0, respectBreakpoint = False):
        if len(dots) == 0:
            return None
        minDot = None
        for dot in dots:
            x,y = dot[0]
            if y < epoch:
                continue

            if minDot is None:
                minDot = dot
            else:
                v = int(y - epoch)
                minV = int(minDot[0][1] - epoch)
                if minV > v:
                    minDot = dot
                else:
                    continue
        if minDot is None:
            return None
        if respectBreakpoint:
            v = int(minDot[0][1] - epoch)
            if v > (2*diameter):
                return None # indicates that the entire row is not set
        return minDot[0] # (X,Y)

    def __get_col_cor(self, dots, epoch = 0, diameter = 0, respectBreakpoint = False):
        if len(dots) == 0:
            return None
        minDot = None
        for dot in dots:
            x,y = dot[0]
            if x < epoch:
                continue

            if minDot is None:
                minDot = dot
            else:
                v = int(x - epoch)
                minV = int(minDot[0][0] - epoch)
                if minV > v:
                    minDot = dot
                else:
                    continue
        if minDot is None:
            return None
        if respectBreakpoint:
            v = int(minDot[0][0] - epoch)
            if v > (2*diameter):
                return None # indicates that the entire row is not set
        return minDot[0] # (X,Y)

    def __get_dots_from_box(self, dots, box):
        left,right,top,bottom = box
        result = []
        for dot in dots:
            x,y = dot[0]
            if x >= left and x <= right and y >= top and y <= bottom:
                result.append(dot)
        return result

    def __get_dots_from_region(self, dots, y1, y2):
        D = []
        if y2 < y1:
            return D

        for dot in dots:
            x,y = dot[0]
            if y > y1 and y < y2:
                D.append(dot)
        return D

    def __get_valid_dots(self, circles):
        tolerance = 0.45
        radii = []
        consider = []
        for circle in circles:
            x,y = circle[0]
            rad = circle[1]
            # OpenCV uses row major
            # Since we do a bitwise not, white pixels belong to the dot.
            
            # Go through the x axis and check if all those are white
            # pixels till you reach the rad
            it = 0
            while it < int(rad):
                if self.binary_image[y,x+it] > 0 and self.binary_image[y+it,x] > 0:
                    it += 1
                else:
                    break
            else:
                if self.binary_image[y,x] > 0:
                    consider.append(circle)
                    radii.append(rad)

        baserad = Counter(radii).most_common(1)[0][0]
        dots = []
        for circle in consider:
            x,y = circle[0]
            rad = circle[1]
            if rad <= int(baserad * (1+tolerance)) and rad >= int(baserad * (1-tolerance)):
                dots.append(circle)

        # Remove duplicate enclosing circles
        # (i.e) Remove circle enclosed by another other circle.
        for dot in dots:
            X1,Y1 = dot[0]
            C1 = dot[1]
            for sdot in dots:
                if dot == sdot:
                    continue
                X2,Y2 = sdot[0]
                C2 = sdot[1]
                D = sqrt(((X2 - X1)**2) + ((Y2-Y1)**2))
                if C1 > (D + C2):
                    dots.remove(sdot)
        
        # Filtered base radius
        radii = []
        for dot in dots:
            rad = dot[1]
            radii.append(rad)
        baserad = Counter(radii).most_common(1)[0][0] 
        return 2*(baserad), dots, baserad
            
    def __get_min_enclosing_circles(self, contours):
        circles = []
        radii = []
        for contour in contours:
            (x,y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            radii.append(radius)
            circles.append((center, radius))
        return circles

    def __process_contours(self):
        contours = cv2.findContours(self.edged_binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 2:
            contours = contours[0]
        else:
            contours = contours[1]
        return contours
