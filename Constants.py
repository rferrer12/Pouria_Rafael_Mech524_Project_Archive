NODE_SIZE = 5
COLOR_RANGE = 50
M_TO_NODE = 1 / 10
DOOR_SIZE = 8
HEATER_SIZE = 4
COOLER_SIZE = 2
DT = 60
K_AIR_GRID = 1.4558e-7 * DT / M_TO_NODE ** 2
K_WALL = 8.348e-8 * DT / (2*M_TO_NODE) ** 2
DELTA_X = 0.01
TOLERANCE = 2.0
# OUTDOORS_TEMPERATURE = -10
# INITIAL_TEMPERATURE = 22.0
# HEATER_TEMPERATURE = 63
# COOLER_TEMPERATURE = 5
# AIRFLOW_SPEED = 10.0
DECAY_RATE = 1
MAX_TEMPERATURE = 30
MIN_TEMPERATURE = 15.0
GRID_WIDTH = 1200
GRID_HEIGHT = 650
MIN_WIDTH = 0
MIN_HEIGHT = 0
SCREEN_WIDTH = GRID_WIDTH + MIN_WIDTH * 2
SCREEN_HEIGHT = GRID_HEIGHT + MIN_HEIGHT * 2
MAX_WIDTH = SCREEN_WIDTH - MIN_WIDTH
MAX_HEIGHT = SCREEN_HEIGHT - MIN_HEIGHT
WALL_THICKNESS = NODE_SIZE
COLS = GRID_WIDTH // NODE_SIZE
ROWS = GRID_HEIGHT // NODE_SIZE
FPS = 60
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)


class UI_Constants:
    """
    Contains constants and methods for managing the initial conditions and settings of the HVAC system.

    Attributes:
        indoor_initial_temperature (int): Initial indoor temperature value.
        outdoor_initial_temperature (int): Initial outdoor temperature value.
        heater_initial_temperature (int): Initial temperature value for the heater.
        cooler_initial_temperature (int): Initial temperature value for the cooler.
        fan_airflow_speed (int): Initial airflow speed for the fan.
    """
    indoor_initial_temperature = 0
    outdoor_initial_temperature = 0
    heater_initial_temperature = 0
    cooler_initial_temperature = 0
    fan_airflow_speed = 0

    @classmethod
    def set_indoor_initial_temperature(cls, value):
        """
        Sets the initial indoor temperature.

        Args:
            value (int): The indoor temperature value to set.
        """
        cls.indoor_initial_temperature = value
    @classmethod
    def get_indoor_initial_temperature(cls):
        """
        Gets the initial indoor temperature.

        Returns:
            int: The indoor temperature value.
        """
        return cls.indoor_initial_temperature

    @classmethod
    def set_outdoor_initial_temperature(cls, value):
        """
        Sets the initial outdoor temperature.

        Args:
            value (int): The outdoor temperature value to set.
        """
        cls.outdoor_initial_temperature = value
    @classmethod
    def get_outdoor_initial_temperature(cls):
        """
        Gets the initial outdoor temperature.

        Returns:
            int: The outdoor temperature value.
        """
        return cls.outdoor_initial_temperature

    @classmethod
    def set_heater_initial_temperature(cls, value):
        """
        Sets the initial temperature for the heater.

        Args:
            value (int): The heater temperature value to set.
        """
        cls.heater_initial_temperature = value
    @classmethod
    def get_heater_initial_temperature(cls):
        """
        Gets the initial temperature for the heater.

        Returns:
            int: The heater temperature value.
        """
        return cls.heater_initial_temperature
    
    @classmethod
    def set_cooler_initial_temperature(cls, value):
        """
        Sets the initial temperature for the cooler.

        Args:
            value (int): The cooler temperature value to set.
        """
        cls.cooler_initial_temperature = value
    @classmethod
    def get_cooler_initial_temperature(cls):
        """
        Gets the initial temperature for the cooler.

        Returns:
            int: The cooler temperature value.
        """
        return cls.cooler_initial_temperature
    
    @classmethod
    def set_airflow_speed(cls, value):
        """
        Sets the initial airflow speed for the fan.

        Args:
            value (int): The airflow speed value to set.
        """
        cls.fan_airflow_speed = value

    @classmethod
    def get_airflow_speed(cls):
        """
        Gets the initial airflow speed for the fan.

        Returns:
            int: The airflow speed value.
        """
        return cls.fan_airflow_speed

