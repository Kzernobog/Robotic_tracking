import queue
import math

class Turret_control(object):

    def __init__(self, max_locations = 100):
        """
        dist_per_pixel - in meters/pixel
        max_location - history of tracked locations
        """
        self._ratio_dict = {'z1A':8000/9, 'z1E':8000/6, 'z2A':8000/16, 'z2E':8000/12, 'z3A':8000/24, 'z3E':8000/18, 'z4A':8000/36, 'z4E':8000/24, 'z5A':8000/47, 'z5E':8000/26, 
                            'z6A':8000/53, 'z6E':8000/29, 'z7A':8000/64, 'z7E':8000/35}
        self._width = 720
        self._height = 480
        self._reference_x = self._width/2
        self._reference_y = self._height/2
        self.max_locations = max_locations
        self._last_n_locations = queue.Queue(self.max_locations) # history of tracked locations along with their time stamps


    def _dist_per_pixel(self, depth):
        return self._base_dist_per_pixel/depth

    def get_azimuth_elevation(self, data, zoom_level):
        """
        Takes in a pixel value and depth and returns the corresponding azimuth
        and elevation in radians
        @params:
            data - tuple (x, y, timestamp) - x, y are the pixel coordinates
            timestamp - in  miliseconds
            depth - depth in meters
        @return:
            theta_x, theta_y in degrees
            angular_v_x, angular_v_x in degrees/sec
        """
        # update the history data structure
        self._update_queue(data)

        # collect current data
        x, y, = data

        dif_x = (x - self._reference_x)
        dif_y = y - self._reference_y
        # determine ratios based on zoom level
        zA = self._ratio_dict[''.join(['z', str(zoom_level), 'A'])]
        zE = self._ratio_dict[''.join(['z', str(zoom_level), 'E'])]

        # retrieve previous timestep data
        # previous_x, previous_y, previous_timestamp = list(self._last_n_locations.queue)[-1]

        # check for center region immobility
        if abs(dif_x) < 15:
            dif_x = 0

        if abs(dif_y) < 10:
            dif_y = 0

        number_of_azimuth_steps = int( dif_x* zA)
        number_of_elevation_steps = int(dif_y * zE) 
        # calculate deltas
        # delta_x = x - previous_x
        # delta_y = y - previous_y
        # delta_t = (timestamp - previous_timestamp)/1000 # time diff in seconds

        # calculate arc lengths
        # arclen_x = (delta_x)*(self._dist_per_pixel(depth))
        # arclen_y = (delta_y)*(self._dist_per_pixel(depth))

        # calculate elevation and azimuth changes
        # theta_x = math.degrees(arclen_x/depth)
        # theta_y = math.degrees(arclen_y/depth)

        # calculate angular velocities
        # v_x = delta_x/delta_t
        # v_y = delta_y/delta_t
        # angular_v_x = math.degrees(v_x/depth)
        # angular_v_y = math.degrees(v_y/depth)
        result = (number_of_azimuth_steps, number_of_elevation_steps)
        return result

    def _update_queue(self, data):
        """
        updates the the history queue
        """
        if self._last_n_locations.full():
            self._last_n_locations.get()
            self._last_n_locations.put(data)
        else:
            self._last_n_locations.put(data)




if __name__ == "__main__":
    pass