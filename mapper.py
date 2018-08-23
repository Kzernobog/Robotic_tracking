# TODO: convert pixel coordinate to laser grid coordinates
# TODO: translate pixel coordinate system to laser coordinate system

class Mapper(object):

    def __init__(self):
        self.scale = None
        self.laser_max = None

    def get_laser_point(self, point):
        """splits the screen into quadrants, returns the quadrant corresponding to
        the point
        params: point - a tuple - (x, y) pixel co-ordinate to classify
                scale - a tuple - (x, y) signifying pixel/unit
        return: quad - a tuple - (x, y) corresponding to a quadrant"""
        (x, y) = point
        (x_sc, y_sc) = self.scale
        res_x = (int)(x/x_sc)
        res_y = (int)(y/y_sc)
        point = (res_x, res_y)
        return self.translate_system(point, self.laser_max)

    def set_scale(self, resolution, laser_max):
        """constructs a scale from the resolution of the image and maximum laser
        position
        params: resolution - a tuple - (x, y) resolution of the screen
                laser_max - a tuple - (x, y) maximum laser positions
        return: scale - a tuple - x and y scale"""
        (x_reso, y_reso) = resolution
        (x_laser, y_laser) = laser_max
        res_x = (int)(x_reso/(x_laser*2))
        res_y = (int)(y_reso/(y_laser*2))
        self.scale = (res_x, res_y)
        self.laser_max =  ((x_laser*2), (y_laser*2))
        return (res_x, res_y)

    def translate_system(self, point, resolution):
        """translates the pixel coordinate system to laser coordinate system -
        top corner origin to center origin
        params: point - a tuple - (x,y) coordinate to be translated
                resolution - a tuple - (x,y) resolution of the coordinate
                system
        return: new_point - a tuple - coordinate of the pixel in the new coordinate system"""
        (res_x, res_y) = resolution
        (x, y) = point
        translate_x = (int)(res_x/2)
        translate_y = (int)(res_y/2)
        new_x = x - translate_x
        new_y = y - translate_y
        return (new_x, new_y)
