#********************************* IMPORTS ************************************

from Constants import *
from Model import *
from PyQt5.QtCore import QObject
from hvac_dashboard_ui import Ui_Dialog

#***************************** CLASS DEFINITION *******************************

class Controller(QObject):
    """
    Controller class to manage the operation of HVAC devices and system modes.

    Attributes:
        devices (list): List of devices controlled by the system (Heater, Cooler, Fan, etc.).
        current_mode (str): Current mode of the system (Heating, Cooling, Ventilation, Auto).
        heating_setpoint (int): Initial setpoint temperature for heating.
        cooling_setpoint (int): Initial setpoint temperature for cooling.
    """
    def __init__(self):
        """
        Initializes the Controller class with default attributes and setpoints.
        """
        super().__init__()
        self.devices = []
        self.current_mode = ""
        self.heating_setpoint = UI_Constants.get_heater_initial_temperature()
        self.cooling_setpoint = UI_Constants.get_cooler_initial_temperature()

    def add_devices(self, devices):
        """
        Adds a list of devices to the controller.

        Args:
            devices (list): List of device objects (e.g., Heater, AirConditioner).
        """
        for device in devices:
            self.devices.append(device)

    def heating_mode(self):
        """
        Activates the heating mode by turning on the Heater and turning off other devices.
        Emits the updated mode signal.
        """
        self.current_mode = "Heating"
        for device in self.devices:
            if isinstance(device, Heater):
                device.is_on = True
            else:
                device.is_on = False

    def cooling_mode(self):
        """
        Activates the cooling mode by turning on the AirConditioner and turning off other devices.
        Emits the updated mode signal.
        """
        self.current_mode = "Cooling"
        for device in self.devices:
            if isinstance(device, AirConditioner):
                device.is_on = True
            else:
                device.is_on = False

    def ventilation_mode(self):
        """
        Activates the ventilation mode by turning on the Fan and turning off other devices.
        Emits the updated mode signal.
        """
        self.current_mode = "Ventilation"
        for device in self.devices:
            if isinstance(device, Fan):
                device.is_on = True
            else:
                device.is_on = False

    def auto_mode(self, current_temperature, set_point):
        """
        Activates the auto mode to maintain temperature automatically based on setpoints.

        Args:
            current_temperature (float): The current temperature of the environment.
            set_point (int): The target temperature to maintain.
        """
        if current_temperature < set_point - TOLERANCE:
            self.heating_mode()

        elif current_temperature > set_point + TOLERANCE:
            self.cooling_mode()

        else:
            self.ventilation_mode()  # Maintain temperature while fans balance the temperature

        self.current_mode = "Auto"