import os
import yaml
import math
import imageio
import numpy as np

class FreePointFinder:
    
    def __init__(
        self,
        map_yaml_filename,
        robot_radius_m=0.3,
        max_distance_m=15.0,
        distance_increment_m=None,
        angle_increment_deg=2.0
    ):
        """Create a FreePointFinder instance.

        Args:
        map_yaml_filename (str): Filename of the map YAML file.
        robot_radius_m (float, optional): Robot's radius, in meters. Defaults to 0.3.
        max_distance_m (float, optional): Max distance to look for a free point, in meters. Defaults to 15.0.
        distance_increment_m (float, optional): Distance increment step, in meters. Defaults to the map resolution.
        angle_increment_deg (float, optional): Angle increment step, in degrees. Defaults to 2.0.
        """
        map_yaml_file = open(map_yaml_filename)
        map_data = yaml.load(map_yaml_file)
        map_yaml_file.close()
        if map_data['origin'][2] != 0:
            raise Exception('Non-zero origin yaw is not supported.')
        map_image_filename = \
            map_data['image'] if os.path.isabs(map_data['image']) else \
            os.path.join(os.path.dirname(map_yaml_filename), map_data['image'])
        self._map_image = imageio.imread(map_image_filename)
        if not map_data['negate']:
            self._map_image = 255 - self._map_image
        self._free_thresh = math.ceil(map_data['free_thresh'] * 255)
        self._resolution_mppx = float(map_data['resolution'])
        self._origin_x_px = -int(map_data['origin'][0] / self._resolution_mppx)
        self._origin_y_px = self._map_image.shape[0] + int(map_data['origin'][1] / self._resolution_mppx)
        self._robot_radius_px = math.ceil(robot_radius_m / self._resolution_mppx)
        self._robot_area_shape = (self._robot_radius_px * 2, self._robot_radius_px * 2)
        self._max_distance_px = math.ceil(max_distance_m / self._resolution_mppx)
        self._distance_increment_px = \
            1 if distance_increment_m is None else \
            math.max(1, math.floor(distance_increment_m / self._resolution_mppx))
        self._angle_increment_rad = angle_increment_deg * math.pi / 180.0

    def _m_to_px(self, x_m, y_m):
        """Transform a point from the map coordinate system (meters, map origin)
        to the image coordinate system (pixels, top-left pixel as origin).

        Args:
        x_m (float): The point's x-coordinate, in meters.
        y_m (float): The point's y-coordinate, in meters.

        Returns:
        (int, int): The point in the image coordinate system.
        """
        return (
            round(x_m / self._resolution_mppx) + self._origin_x_px,
            -round(y_m / self._resolution_mppx) + self._origin_y_px
        )

    def _px_to_m(self, x_px, y_px):
        """Transform a point from the image coordinate system (pixels, top-left pixel as origin)
        to the map coordinate system (meters, map origin).

        Args:
        x_px (int): The point's x-coordinate, in pixels.
        y_px (int): The point's y-coordinate, in pixels.

        Returns:
        (float, float): The point in the map coordinate system.
        """
        return (
            (x_px - self._origin_x_px) * self._resolution_mppx,
            -(y_px - self._origin_y_px) * self._resolution_mppx
        )

    def _is_free_px(self, x_px, y_px):
        """Check whether a point is free, in the image coordinate system.

        Args:
        x_px (int): The point's x-coordinate, in pixels.
        y_px (int): The point's y-coordinate, in pixels.

        Returns:
        bool: True if the point is free, False otherwise.
        """
        area = self._map_image[
            y_px-self._robot_radius_px:y_px+self._robot_radius_px,
            x_px-self._robot_radius_px:x_px+self._robot_radius_px
        ]
        if area.shape != self._robot_area_shape:
            return False
        return (area < self._free_thresh).all()

    def _closest_free_point_px(self, x_px, y_px):
        """Find the closest free point to a given point, in the image coordinate system.

        Args:
        x_px (int): The point's x-coordinate, in pixels.
        y_px (int): The point's y-coordinate, in pixels.

        Returns:
        (int, int): The x- and y-coordinate of the closest free point. Returns (None, None) if no free point could be found.
        """
        if self._is_free_px(x_px, y_px):
            return x_px, y_px
        for r_px in range(1, self._max_distance_px + 1, self._distance_increment_px):
            for a_rad in np.arange(0, 2 * math.pi, self._angle_increment_rad):
                xt_px = round(x_px + r_px * math.cos(a_rad))
                yt_px = round(y_px + r_px * math.sin(a_rad))
                if self._is_free_px(xt_px, yt_px):
                    return xt_px, yt_px
        return None, None

    def is_free(self, x_m, y_m):
        """Check whether a point is free, in the map coordinate system.

        Args:
        x_m (float): The point's x-coordinate, in meters.
        y_m (float): The point's y-coordinate, in meters.

        Returns:
        bool: True if the point is free, False otherwise.
        """
        return self._is_free_px(*self._m_to_px(x_m, y_m))

    def closest_free_point(self, x_m, y_m):
        """Find the closest free point to a given point, in the map coordinate system.

        Args:
        x_m (float): The point's x-coordinate, in meters.
        y_m (float): The point's y-coordinate, in meters.

        Returns:
        (float, float): The x- and y-coordinate of the closest free point. Returns (None, None) if no free point could be found.
        """
        xf_px, yf_px = self._closest_free_point_px(*self._m_to_px(x_m, y_m))
        if xf_px is None and yf_px is None:
            return None, None
        return self._px_to_m(xf_px, yf_px)
