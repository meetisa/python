# This class handles sprite sheets
# This was taken from www.scriptefun.com/transcript-2-using
# sprite-sheets-and-drawing-the-background
# I've added some code to fail if the file wasn't found..
# Note: When calling images_at the rect is the format:
# (x, y, x + offset, y + offset)

import pygame

class SpriteSheet(object):
    def __init__(self, filename, method='name'):
        try:
            if method == 'name':
                self.sheet = pygame.image.load(filename).convert()
            else:
                self.sheet = filename.convert()
        except pygame.error:
            print('Unable to load spritesheet image: ' + str(filename))
            raise SystemExit
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

    def load_grid(self, raws, columns, colorkey = None):
        height = self.sheet.get_height() / raws
        width = self.sheet.get_width() / columns
        x_t = 0
        y_t = 0
        tups = []
        surfs = []
        for raw in range(raws):
            surfs.append([])
            for column in range(columns):
                tups.append((x_t, y_t, width, height))
                x_t += width
                surfs[-1].append(self.image_at(tups[-1],colorkey))
            x_t = 0
            y_t += height
        return surfs 
