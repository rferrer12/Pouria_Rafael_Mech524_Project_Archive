from __future__ import annotations
from enum import Enum
from math import sqrt, exp

from Constants import *
from colour import Color

blue = Color("blue")
color_scale = list(blue.range_to(Color("red"), COLOR_RANGE))

class Coordinates(Enum):
    EAST = 0
    WEST = 1
    SOUTH = 2
    NORTH = 3

class Point:
    """
    Class representing a point location in a 2D grid.
    """
    x: int
    y: int
    def __init__(self, x, y):
        """
        Initialize the Point object with x and y coordinates.
        :param x: The x-coordinate of the Point
        :param y: The y-coordinate of the Point
        """
        self.x = x
        self.y = y
        self.neighbors = []

    def __hash__(self):
        """
        Generate a hash value for the Point object.
        :return: Returns a hash value for the Point object.
        """
        return hash((self.x, self.y))

    def __eq__(self, other):
        """
        Checks equality between two Point objects.
        :param other: Any object of type Point that can be compared with self.
        :return: Returns True if the x and y coordinates of the two Point objects are
        equal, returns False if otherwise.
        """
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False

    def __add__(self, other):
        """
        Adds two instances of Point objects together.
        :param other: The Point object to be added to self.
        :return: The addition of both point objects.
        """
        self.x = self.x + other.x
        self.y = self.y + other.y
        return self

    def __mul__(self, other):
        self.x = self.x * other
        self.y = self.y * other
        return self


class Node:
    """
    Class representing a node in a grid. It has knowledge of who their neighbor
    nodes are and changes temperature and color based on that information. It
    also has a spec which determines what NodeType it is part of, and what
    physical properties it will have because of it.
    """
    size: int = NODE_SIZE

    def __init__(self, location):
        """
        Initialize the Node object with a location as a Point object, a list of neighbor Nodes
        which will be updated later, a spec which defines its physical attributes, a color
        that will change based on temperature, and its temperature.
        :param location: A point object that defines the Node's location.
        """
        self.location: Point = location
        self.neighbors = []
        self.spec = None
        self.color = "white"
        self.temperature : float = 0.0
        self.velocity_nodes = []
        self.velocity_u : float = 0
        self.velocity_v : float = 0
        self.velocity_magnitude : float = 0

    def set_temperature(self, grid):
        """
        Calculate and set a new temperature for the node based on its neighbors' temperatures
        and physical properties. It iterates through all neighboring nodes to set a value. If the node
        is a sensor, it doesn't take in consideration the temperature of wall nodes, as it is only
        taking into account the temperature based on convection, not conduction.
        :return: The new temperature for the node.
        """
        sum_temperature: float = 0.0
        if isinstance(self, TemperatureScale):
            pass
        elif (isinstance(self.spec, Heater) or isinstance(self.spec, AirConditioner)) and self.spec.is_on:
            return self.spec.emit_temperature
        elif isinstance(self.spec, Sensor):
            for neighbor_location in self.neighbors:
                neighbor = grid.grid_map[neighbor_location]
                if isinstance(neighbor.spec, Wall):
                    continue
                else:
                    delta_temperature = neighbor.temperature - self.temperature
                    sum_temperature = sum_temperature + neighbor.spec.heat_k * delta_temperature
            new_temperature = self.temperature + sum_temperature
            return new_temperature
        else:
            for neighbor_location in self.neighbors:
                neighbor = grid.grid_map[neighbor_location]
                delta_temperature = neighbor.temperature - self.temperature
                sum_temperature = sum_temperature + neighbor.spec.heat_k * delta_temperature
            new_temperature = self.temperature + sum_temperature
            return new_temperature

    def change_color(self, grid):
        """
        Changes the color set for each node depending on its spec. If the node is a
        room node or an open door, it calls the function set_gradient, which will set
        the nodes color depending on its temperature. If it's a device, sensor, or any
        other feature, it sets a specific color to represent it.
        :return: None
        """
        self.temperature = self.set_temperature(grid)
        if isinstance(self.spec, Wall):
            self.color = "black"
        elif isinstance(self.spec, Outdoors):
            self.color = "white"
        elif isinstance(self.spec, Heater):
            if self.spec.is_on:
                self.color = "orange"
            else:
                self.color = "brown"
        elif isinstance(self.spec, AirConditioner):
            if self.spec.is_on:
                self.color = "green"
            else:
                self.color = "dark green"
        elif isinstance(self.spec, Sensor):
            self.color = "purple"
        elif isinstance(self.spec, Fan):
            if self.spec.is_on:
                self.color = "orange"
        elif isinstance(self.spec, Door):
            if not self.spec.open_status:
                self.color = "brown"
            else:
                self.set_gradient()
        elif isinstance(self.spec, TemperatureScale):
            pass
        else:
            self.set_gradient()

    def set_gradient(self):
        """
        Sets the color of the nodes with spec Room to a gradient based on its temperature.
        :return: None
        """
        if self.temperature > MAX_TEMPERATURE:
            self.color = "red"
        elif MIN_TEMPERATURE > self.temperature > 0.0:
            self.color = "blue"
        elif self.temperature < 0.0:
            self.color = "white"
        else:
            temperature_diff = MAX_TEMPERATURE - MIN_TEMPERATURE
            new_color = tuple(i * 255 for i in color_scale[int((self.temperature - MIN_TEMPERATURE) / temperature_diff
                                                            * (len(color_scale) - 1))].rgb)
            self.color = new_color

    def set_velocity_grid(self, hor_grid,vert_grid):
        i = self.location.x
        j = self.location.y
        if i+5 >= MAX_WIDTH or j+5 >= MAX_HEIGHT:
            return
        self.velocity_nodes.append(hor_grid.grid_map[(i + 5, j + 2)]) # EAST
        self.velocity_nodes.append(hor_grid.grid_map[(i, j + 2)])  # WEST
        self.velocity_nodes.append(vert_grid.grid_map[(i + 2, j + 5)]) # SOUTH
        self.velocity_nodes.append(vert_grid.grid_map[(i + 2, j )]) # NORTH

    def update_airflow(self, grid, hor_grid, vert_grid):
        enum = Coordinates
        i = self.location.x
        j = self.location.y
        divergence = 1.0
        east_wall = 1
        west_wall = 1
        north_wall = 1
        south_wall = 1
        if i+5 >= MAX_WIDTH or j+5 >= MAX_HEIGHT:
            return
        if isinstance(self.spec, Wall):
            hor_grid.velocity_map[self.velocity_nodes[enum.EAST.value]] = 0
            hor_grid.velocity_map[self.velocity_nodes[enum.WEST.value]] = 0
            vert_grid.velocity_map[self.velocity_nodes[enum.SOUTH.value]] = 0
            vert_grid.velocity_map[self.velocity_nodes[enum.NORTH.value]] = 0
        else:
            if isinstance(self.spec, Fan):
                if self.spec.direction.x >= 0:
                    hor_grid.velocity_map[self.velocity_nodes[enum.EAST.value]] = self.spec.emit_airflow * self.spec.direction.x
                else:
                    hor_grid.velocity_map[self.velocity_nodes[enum.WEST.value]] = self.spec.emit_airflow * self.spec.direction.x

                if self.spec.direction.y >= 0:
                    vert_grid.velocity_map[self.velocity_nodes[enum.SOUTH.value]] = self.spec.emit_airflow * self.spec.direction.y
                else:
                    vert_grid.velocity_map[self.velocity_nodes[enum.NORTH.value]] = self.spec.emit_airflow * self.spec.direction.y
            counter = 4
            for neighbor_location in self.neighbors:
                neighbor = grid.grid_map[neighbor_location]
                if isinstance(neighbor.spec, Wall):
                    counter = counter - 1
                    if neighbor.location.x < self.location.x:
                        hor_grid.velocity_map[self.velocity_nodes[enum.WEST.value]] = 0
                        west_wall = 0
                    elif neighbor.location.x > self.location.x:
                        hor_grid.velocity_map[self.velocity_nodes[enum.EAST.value]] = 0
                        east_wall = 0
                    elif neighbor.location.y < self.location.y:
                        vert_grid.velocity_map[self.velocity_nodes[enum.NORTH.value]] = 0
                        north_wall = 0
                    elif neighbor.location.y > self.location.y:
                        vert_grid.velocity_map[self.velocity_nodes[enum.SOUTH.value]] = 0
                        south_wall = 0
            while abs(divergence)<0.01:
                divergence = 1.9*(hor_grid.velocity_map[self.velocity_nodes[enum.EAST.value]]
                              -hor_grid.velocity_map[self.velocity_nodes[enum.WEST.value]]
                              -vert_grid.velocity_map[self.velocity_nodes[enum.SOUTH.value]]
                              +vert_grid.velocity_map[self.velocity_nodes[enum.NORTH.value]])

                hor_grid.velocity_map[self.velocity_nodes[enum.EAST.value]] = (hor_grid.velocity_map[self.velocity_nodes[enum.EAST.value]]
                                                                                - divergence/counter) * east_wall
                hor_grid.velocity_map[self.velocity_nodes[enum.WEST.value]] = (hor_grid.velocity_map[self.velocity_nodes[enum.WEST.value]]
                                                                                + divergence/counter) * west_wall
                vert_grid.velocity_map[self.velocity_nodes[enum.SOUTH.value]] = (vert_grid.velocity_map[self.velocity_nodes[enum.SOUTH.value]]
                                                                                + divergence/counter) * south_wall
                vert_grid.velocity_map[self.velocity_nodes[enum.NORTH.value]] = (vert_grid.velocity_map[self.velocity_nodes[enum.NORTH.value]]
                                                                                - divergence/counter) * north_wall

    def calculate_velocity_magnitude(self, hor_grid, vert_grid):
        i = self.location.x
        j = self.location.y
        if i+5 >= MAX_WIDTH or j+5 >= MAX_HEIGHT:
            return
        enum = Coordinates
        self.velocity_u = (hor_grid.velocity_map[self.velocity_nodes[enum.EAST.value]]
                 + hor_grid.velocity_map[self.velocity_nodes[enum.WEST.value]])
        self.velocity_v = (vert_grid.velocity_map[self.velocity_nodes[enum.SOUTH.value]]
                 + vert_grid.velocity_map[self.velocity_nodes[enum.NORTH.value]])
        self.velocity_magnitude = sqrt(self.velocity_u**2+self.velocity_v**2)


class Particle:
    """
    Class that initializes the particle object. It is an object that's spawned
    from Fan objects to represent airflow.
    """
    def __init__(self, location, velocity):
        """

        :param location:
        :param velocity:
        """
        self.location = location
        self.velocity = velocity/M_TO_NODE
        self.velocity_u : float = 0.0
        self.velocity_v : float = 0.0
        self.color = "black"
        self.radius = 2
        self.timer = 3

    def calculate_velocity(self, grid):
        for i in range(-2, 5):
            for j in range(-2, 5):
                if Point(self.location.x + i, self.location.y + j) in grid.grid_map.values():
                    node_info = grid.grid_map[Point(self.location.x + i, self.location.y + j)]
                    self.velocity_v = node_info.velocity_v
                    self.velocity_u = node_info.velocity_u


class NodeType:
    """
    Parent class of which all Node types inherit from. It determines the
    size of the grid space for each spec, it's hash map to identify it, its
    location, and sets its initial temperature as 0. It also includes the NODE_SIZE
    to ensure all calculations for rendering are done correctly.
    """
    node_size: int = NODE_SIZE
    #TODO Implement dynamic calculations for the heat transfer coefficient for natural and forced convection
    def __init__(self):
        self.temperature = 0.0
        self.spec_size = [0, 0]
        self.spec_map = {}
        self.location = Point(0, 0)

    def create_node_type_map(self, grid):
        """
        Function that generates a hash map with all the nodes that are part
        of an object. It's later used to assign all nodes to their spec.
        :param grid: The full grid created for the simulation.
        :return: None
        """
        for i in range(self.spec_size[0]):
            for j in range(self.spec_size[1]):
                location = Point(i * self.node_size + self.location.x, j * self.node_size + self.location.y)
                self.spec_map[location] = grid.grid_map[location]

    def set_node_type(self, grid):
        """
        Function that sets the spec for each node in the object's spec_map. If the
        object is a Door, it checks if the object's previous spec is a wall to ensure that
        it is only placed in the correct space.
        :param grid: The full grid created for the simulation.
        :return: None
        """
        for node in grid.grid_map.values():
            if isinstance(self, Door):
                if isinstance(node.spec, Wall) and node.location in self.spec_map:
                    node.spec = self
                    node.temperature = self.temperature
            else:
                if node.location in self.spec_map:
                    node.spec = self
                    node.temperature = self.temperature


class Outdoors(NodeType):
    """
    Class that defines the NodeType Outdoors and contains the physical properties
    for all nodes that are outside the simulated house. It inherits from NodeType.
    """
    def __init__(self, grid):
        """
        Initialization of the Outdoors class. It sets the temperature, heat coefficient, size
        of the area that includes these nodes, and a hash map of the nodes included in this area.
        :param grid: The full grid created for the simulation.
        """
        super().__init__()
        self.heat_k = K_AIR_GRID
        self.temperature = UI_Constants.get_outdoor_initial_temperature()
        self.spec_size = grid.grid_size
        self.spec_map = grid.grid_map
        super().set_node_type(grid)


class Room(NodeType):
    """
    Class that defines the NodeType Room and contains the physical properties
    for all nodes that are in a room. It inherits from NodeType.
    """
    def __init__(self, x_axis, y_axis, room_name, location, grid):
        """
        Initialization of the Room class. It sets the initial temperature, heat coefficient, size
        of the area that includes these nodes, and a hash map of the nodes included in this area.
        It also initializes a wall object that encloses each created room.
        :param x_axis: Amount of nodes that constitute the width of the room.
        :param y_axis: Amount of nodes that constitute the length of the room.
        :param room_name: The name of the room
        :param location: Location of the room's top left corner.
        :param grid: The grid created for the simulation.
        """
        super().__init__()
        self.heat_k = K_AIR_GRID
        self.spec_size = [x_axis, y_axis]
        self.location = location
        self.temperature = INITIAL_TEMPERATURE
        self.create_node_type_map(grid)
        self.room_name = room_name
        self.wall = Wall(x_axis, y_axis, room_name, location, grid)
        self.spec_map = {}
        super().create_node_type_map(grid)
        super().set_node_type(grid)


class Wall(NodeType):
    """
    Class that defines the NodeType Wall and contains the physical properties
    for all nodes that are in a wall. It inherits from NodeType.
    """
    def __init__(self, x_axis, y_axis, room_name, location, grid):
        """
        Initialization of the Wall class. It sets the initial temperature, heat coefficient, size
        of the area that includes these nodes, and a hash map of the nodes included in this area.
        It's initialized when a Room is created
        :param x_axis: Amount of nodes that constitute the width of the walls.
        :param y_axis: Amount of nodes that constitute the length of the walls.
        :param room_name: The name of the room
        :param location: Location of the wall's top left corner.
        :param grid: The grid created for the simulation.
        """
        super().__init__()
        self.heat_k = K_WALL
        self.name = room_name + " Walls"
        self.spec_size = [x_axis + 2, y_axis + 2]
        self.location = Point(location.x - WALL_THICKNESS, location.y - WALL_THICKNESS)
        self.temperature = UI_Constants.get_indoor_initial_temperature()
        self.spec_map = {}
        super().create_node_type_map(grid)
        super().set_node_type(grid)


class Door(NodeType):
    """
    Class that defines the NodeType Door and contains the physical properties
    for all nodes that are in a door. It inherits from NodeType.
    """
    def __init__(self, location, open_status, grid):
        """
        Initialization of the Door class. It sets the initial temperature, heat coefficient, size
        of the area that includes these nodes, and a hash map of the nodes included in this area.
        Every door must be initialized separately in the desired location.
        :param location: Location of the door's top left corner.
        :param open_status: Determines if the door is open or closed.
        :param grid: The grid created for the simulation.
        """
        super().__init__()
        self.location = Point(location.x, location.y)
        self.temperature = UI_Constants.get_indoor_initial_temperature()
        self.open_status = open_status
        self.door_size = DOOR_SIZE
        self.spec_size = [DOOR_SIZE, DOOR_SIZE]
        self.spec_map = {}
        if open_status:
            self.heat_k = K_AIR_GRID
        else:
            self.heat_k = K_WALL
        super().create_node_type_map(grid)
        super().set_node_type(grid)


class Device(NodeType):
    """
    Class that defines a Device and contains the properties that all types of devices
    have in common. It inherits from NodeType and is inherited by the Heater and
    AirConditioner classes.
    """
    def __init__(self, device_name, is_on):
        """
        Function that initializes the Device class. It sets the name of the device,
        the status of the device, the heat coefficient, and initializes the hash map that
        will include the nodes that are part of the device.
        :param device_name: The name of the device.
        :param is_on: Boolean to indicate if the device is on or off.
        """
        super().__init__()
        self.emit_temperature = None
        self.device_name = device_name
        self.is_on = is_on
        self.spec_map = {}
        self.heat_k = K_AIR_GRID


class Heater(Device):
    """
    Class that defines the Heater object and creates an object that emits constant high temperatures
    into the environment. It inherits from Device.
    """
    def __init__(self, device_name, location, is_on, grid):
        """
        Function that initializes the Heater class. It sets the constant temperature it emits, heat coefficient,
        size of the device. It fills the hash map with the nodes that are part of the device and sets
        those nodes' specs as the device.
        :param location: Top left corner of the heater's area.
        :param is_on: Boolean to indicate if the device is on or off.
        :param grid: The grid created for the simulation.
        """
        super().__init__(device_name, is_on)
        self.location = Point(location.x, location.y)
        self.temperature = UI_Constants.get_indoor_initial_temperature()
        self.emit_temperature = UI_Constants.get_heater_initial_temperature()
        self.spec_size = [HEATER_SIZE, HEATER_SIZE]
        super().create_node_type_map(grid)
        super().set_node_type(grid)


class AirConditioner(Device):
    """
    Class that defines the AirConditioner object and creates an object that emits constant high temperatures
    into the environment. It inherits from Device.
    """
    def __init__(self, device_name, location, is_on, grid):
        """
        Function that initializes the AirConditioner class. It sets the constant temperature it emits, heat coefficient,
        size of the device. It fills the hash map with the nodes that are part of the device and sets
        those nodes' specs as the device.
        :param location: Top left corner of the AirConditioner's area.
        :param is_on: Boolean to indicate if the device is on or off.
        :param grid: The grid created for the simulation.
        """
        super().__init__(device_name, is_on)
        self.location = Point(location.x, location.y)
        self.temperature = UI_Constants.get_indoor_initial_temperature()
        self.emit_temperature = UI_Constants.get_cooler_initial_temperature()
        self.spec_size = [COOLER_SIZE, COOLER_SIZE]
        super().create_node_type_map(grid)
        super().set_node_type(grid)


class Fan(Device):
    """
    Class that defines the Fan object and creates an object that generates constant airflow.
    """
    def __init__(self, device_name, location, direction, is_on, grid):
        """
        Function that initializes a Fan object and sets its properties.
        :param device_name: Name of the Fan
        :param location: Top left corner of the Fan's area.
        :param direction: Direction the fan is facing (up, down, left, right)
        :param is_on: Boolean to indicate if the device is on or off.
        :param grid: The grid created for the simulation.
        """
        super().__init__(device_name, is_on)
        self.location = Point(location.x, location.y)
        self.temperature = UI_Constants.get_indoor_initial_temperature()
        self.emit_temperature = UI_Constants.get_indoor_initial_temperature()
        self.direction = Point(direction.x, direction.y)
        self.emit_airflow= UI_Constants.get_airflow_speed()
        self.spec_size = [COOLER_SIZE, COOLER_SIZE]
        self.location_center = Point(self.location.x + COOLER_SIZE*NODE_SIZE//2, self.location.y + COOLER_SIZE*NODE_SIZE//2)
        self.particles = []
        super().create_node_type_map(grid)
        super().set_node_type(grid)

    """def emit_particles(self, number, grid):
        
        Function that emits particles that move based on airflow grid
        :param number: number of particles emitted per instance
        :param grid: Grid created for the simulation
        :return: None
        
        #TODO Finish setting particles to move according to airflow
        counter = 0
        for _ in range(number):
            self.particles.append(Particle(Point(self.location_center.x, self.location_center.y - counter*4), self.emit_airflow))
            counter = counter + 1
            if counter > 4:
                counter = 0
        for particle in self.particles:
            particle.calculate_velocity(grid)
            particle.location = Point(particle.location.x + particle.velocity_u,
                                      particle.location.y + particle.velocity_v)
            particle.timer = particle.timer - 1
            if particle.timer < 0:
                self.particles.remove(particle)"""



class Sensor(NodeType):
    """
    Class that defines the Sensor object and creates an object that measures the temperature
    and other relevant data at a specific node. It inherits from NodeType.
    """
    def __init__(self, location, grid):
        """
        Function that initializes the Sensor class. It sets the location of the sensor, and
        the physical properties around the sensor.
        :param location: Location of the sensor.
        :param grid: The grid created for the simulation.
        """
        super().__init__()
        self.location = Point(location.x, location.y)
        self.temperature = UI_Constants.get_indoor_initial_temperature()
        self.sensor_size = 1
        self.spec_size = [1, 1]
        self.spec_map = {}
        self.heat_k = K_AIR_GRID
        self.data = []
        self.devices = []
        super().create_node_type_map(grid)
        super().set_node_type(grid)

    def set_device(self, device):
        """
        Function that adds a device to the sensor's list of  controlled devices.
        :param device: Object of class Device that will be controlled by the sensor.
        :return: None
        """
        self.devices.append(device)

    def heater_on(self):
        """
        Function that turns on the heaters in the simulation and turns off any
        A/C units controlled by the sensor
        :return: None
        """
        for device in self.devices:
            if isinstance(device, Heater):
                device.is_on = True
            else:
                device.is_on = False

    def ac_on(self):
        """
        Function that turns on the A/C units in the simulation and turns off any
        heater units controlled by the sensor
        :return: None
        """
        for device in self.devices:
            if isinstance(device, AirConditioner):
                device.is_on = True
            else:
                device.is_on = False

    def check_temperature(self, set_temperature):
        """
        Function that checks sensors are not above or below a set temperature. If they are,
        the relevant device will turn off or on. to keep the temperature in the desired range.
        :param set_temperature: Temperature desired for the environment.
        :return: None
        """
        for node in self.spec_map.values():
            if node.temperature < set_temperature - TOLERANCE:
                self.heater_on()
            elif node.temperature > set_temperature + TOLERANCE:
                self.ac_on()

class TemperatureScale(NodeType):
    """
    Class that defines the TemperatureScale object and creates an array of nodes that
    describes the color scale used to determine the temperature. It inherits from
    NodeType.
    """
    def __init__(self, location, grid):
        """
        Function that initializes the TemperatureScale class.
        :param location: Location of the top left corner of the scale area.
        :param grid: The grid created for the simulation.
        """
        super().__init__()
        self.location = Point(location.x, location.y)
        self.spec_map = {}
        self.temperature = UI_Constants.get_indoor_initial_temperature()
        self.spec_size = [20, COLOR_RANGE*2]
        self.heat_k = 0
        super().create_node_type_map(grid)
        super().set_node_type(grid)
        denominator = (self.spec_size[1] // COLOR_RANGE) * 5
        for node in self.spec_map.values():
            node.color = tuple(i * 255 for i in color_scale[(COLOR_RANGE-1)-(node.location.y-self.location.y)//denominator].rgb)


class House:
    """

    """
    #TODO create a class for the House that contains the layout of the houses created
    def __init__(self):
        self.rooms = []

    def add_room(self, room):
        self.rooms.append(room)


class Grid:
    """
    Class that defines the full grid and all the nodes inside of it. It includes a hash map
    that includes every node of the simulation.
    """
    grid_map = {}

    def __init__(self, location, grid_size, node_size):
        """
        Function that initializes the grid for the simulation and creates every node that
        will be modified.
        :param grid_size: Size of the grid that will be created in rows and columns of nodes.
        :param node_size: The size each node will be in pixels.
        """
        self.location = location
        self.grid_size = grid_size
        self.node_size = node_size
        self.neighbors = []
        self.create_grid()
        self.set_neighbors()

    def create_grid(self):
        """
        Function that creates the grid for the simulation and creates every node that
        will be used. It generates a hash map that uses the location of every node as
        keys for that specific node.
        :return: None
        """
        for i in range(self.grid_size[1]):
            for j in range(self.grid_size[0]):
                location = Point(i * self.node_size + MIN_WIDTH + self.location.x, j * self.node_size + MIN_HEIGHT+self.location.y)
                self.grid_map[location] = Node(location)

    def set_neighbors(self):
        """
        Function that makes every node have a list of all the nodes that are adjacent to it.
        It iterates through every node and generates a list of every neighbor node.
        :return: None
        """
        for node in self.grid_map.values():
            for i in range(-1, 2):
                for j in range(-1, 2):
                    sum_x = node.location.x + i * self.node_size
                    sum_y = node.location.y + j * self.node_size
                    if sum_x < MIN_WIDTH or sum_x > MAX_WIDTH or sum_y < MIN_HEIGHT or sum_y > MAX_HEIGHT:
                        continue
                    elif ((i == 0 and j == 0) or (i == -1 and j == -1) or (i == -1 and j == 1) or (i == 1 and j == -1)
                        or (i == 1 and j == 1)):
                        neighbor_location = Point(sum_x, sum_y)
                        if neighbor_location in self.grid_map:
                            node.neighbors.append(self.grid_map[neighbor_location].location)

                            
class StaggeredGrid:
    """
        Class that defines the full grid and all the nodes inside of it. It includes a hash map
        that includes every node of the simulation.
        """
    grid_map = {}

    def __init__(self, location, grid_size, node_size):
        """
        Function that initializes the grid for the simulation and creates every node that
        will be modified.
        :param grid_size: Size of the grid that will be created in rows and columns of nodes.
        :param node_size: The size each node will be in pixels.
        """
        self.location = location
        self.grid_size = grid_size
        self.node_size = node_size
        self.grid_map = {}
        self.velocity_map = {}
        self.velocity: float = 0
        self.neighbors = {}
        self.avg_perpendicular_vel: float = 0
        self.create_staggered_grid()

    def create_staggered_grid(self):
        """
        """
        for i in range(self.grid_size[1]):
            for j in range(self.grid_size[0]):
                location = (i * self.node_size + MIN_WIDTH + self.location.x,
                                 j * self.node_size + MIN_HEIGHT + self.location.y)
                self.grid_map[location] = location
                self.velocity_map[location] = self.velocity
