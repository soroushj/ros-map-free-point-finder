# Free Point Finder

Find the closest free point to an occupied point on a ROS map, taking the robot's radius into account.

## Options

```python
FreePointFinder(
    map_yaml_filename,
    robot_radius_m=0.3,
    max_distance_m=15.0,
    distance_increment_m=None,
    angle_increment_deg=2.0
)
```

- **`map_yaml_filename`** *(string)* Filename of the map YAML file.
- **`robot_radius_m`** *(float, optional)* Robot's radius, in meters. Defaults to 0.3.
- **`max_distance_m`** *(float, optional)* Max distance to look for a free point, in meters. Defaults to 15.0.
- **`distance_increment_m`** *(float, optional)* Distance increment step, in meters. Defaults to the map resolution.
- **`angle_increment_deg`** *(float, optional)* Angle increment step, in degrees. Defaults to 2.0.
