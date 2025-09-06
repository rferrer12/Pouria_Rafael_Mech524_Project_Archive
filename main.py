#********************************* IMPORTS ************************************

import pygame
import sys
from Constants import *
from Model import *
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, QObject
from hvac_dashboard_ui import Ui_Dialog
from Controller import *
import pyqtgraph as pg

#***************************** CLASS DEFINITION *******************************

class SimulationManager(QObject):
    """
    Manages the simulation of the HVAC system, integrating the UI with the controller and model.

    Signals:
        start_simulation (pyqtSignal): Emits initial conditions to start the simulation.
        auto_mode_simulation (pyqtSignal): Emits setpoint value for auto mode operation.

    Attributes:
        app (QApplication): The PyQt application instance.
        Dialog (QDialog): The main dialog window.
        ui (Ui_Dialog): The UI components setup.
        running (bool): Indicates whether the simulation is running.
        controller (Controller): The HVAC controller managing devices and modes.
        grid (Grid): The simulation grid (to be initialized).
    """
    start_simulation = pyqtSignal(dict)
    auto_mode_simulation = pyqtSignal(int) # to be passed from set_auto_mode to the controller auto_mode

    def __init__(self):
        """
        Initializes the SimulationManager with UI, controller, and signals.
        """
        super().__init__()
        self.app = QtWidgets.QApplication(sys.argv)
        self.Dialog = QtWidgets.QDialog()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.Dialog)
        self.running = False
        self.controller = Controller()

        self.connectSignal()
        self.Dialog.show()
        self.grid = None  # Initialize grid later

    def ConnectSignal(self):
        """
        Connects GUI signals to specific update functions and controller actions.
        """
        # Initial Condition Signals      
        self.ui.IndoorTempSlider.valueChanged.connect(
            lambda value: self.updateSliderValue(value, "IndoorTempSlider"))
        self.ui.OutdoorTempSlider.valueChanged.connect(
            lambda value: self.updateSliderValue(value, "OutdoorTempSlider"))
        self.ui.HeaterTempDial.valueChanged.connect(
            lambda value: self.updateDialValue(value, "HeaterTempDial"))
        self.ui.CoolerTempDial.valueChanged.connect(
            lambda value: self.updateDialValue(value, "CoolerTempDial"))
        self.ui.FanSpeedDial.valueChanged.connect(
            lambda value: self.updateDialValue(value, "FanSpeedDial"))
        
        # Connect system on/off
        self.ui.OnOffButton.toggled.connect(self.startSimulation)

        # Controller Signals
        self.ui.HeatingModeButton.pressed.connect(self.set_heating_mode)
        self.ui.CoolingModeButton.pressed.connect(self.set_cooling_mode) 
        self.ui.VentilationModeButton.pressed.connect(self.set_ventilation_mode)
        self.ui.AutoModeButton.pressed.connect(self.set_auto_mode)

        # End of Demo handling to exit the program when GUI window is closed
        self.Dialog.finished.connect(self.on_close)
    
    def set_auto_mode(self):
        """
        Activates auto mode and connects the setpoint slider to the controller.
        """
        self.ui.SliderTempSetPointAuto.setEnabled(True)
        self.ui.TempSetPoint.setEnabled(True)
        self.ui.SliderTempSetPointAuto.valueChanged.connect(
            lambda value: self.updateSliderValue(value, "SliderTempSetPointAuto"))
        self.setpoint_value = self.ui.SliderTempSetPointAuto.value()
        self.controller.current_mode = "Auto"
        self.auto_mode_simulation.emit(self.setpoint_value)

    def set_heating_mode(self):
        """
        Activates heating mode by disabling auto setpoint controls and updating the controller.
        """
        self.ui.SliderTempSetPointAuto.setEnabled(False)
        self.ui.TempSetPoint.setEnabled(False)
        self.controller.heating_mode()

    def set_cooling_mode(self):
        """
        Activates cooling mode by disabling auto setpoint controls and updating the controller.
        """
        self.ui.SliderTempSetPointAuto.setEnabled(False)
        self.ui.TempSetPoint.setEnabled(False)
        self.controller.cooling_mode()

    def set_ventilation_mode(self):
        """
        Activates ventilation mode by disabling auto setpoint controls and updating the controller.
        """
        self.ui.SliderTempSetPointAuto.setEnabled(False)
        self.ui.TempSetPoint.setEnabled(False)
        self.controller.ventilation_mode()

    def updateDialValue(self, value, dial_name):
        """
        Updates the corresponding label under each dial with the current value.

        Args:
            value (int): The current value of the dial.
            dial_name (str): The name of the dial (Heater, Cooler, FanSpeed).
        """
        if dial_name == "HeaterTempDial":
            self.ui.HeaterDialValue.setText(f"{value}°C")
        elif dial_name == "CoolerTempDial":
            self.ui.CoolerDialValue.setText(f"{value}°C")
        elif dial_name == "FanSpeedDial":
            self.ui.FanSpeedDialValue.setText(str(value))

    def updateSliderValue(self, value, slider_name):
        """
        Updates the label associated with each slider based on its current value.

        Args:
            value (int): The current value of the slider.
            slider_name (str): The name of the slider (IndoorTemp, OutdoorTemp, Auto Setpoint).
        """
        if slider_name == "IndoorTempSlider":
            self.ui.IndoorTemperature.setText(f"Indoor Temp: {value}°C")
        elif slider_name == "OutdoorTempSlider":
            self.ui.OutdoorTemperature.setText(f"Outdoor Temp: {value}°C")
        elif slider_name == "SliderTempSetPointAuto":
            self.setpoint_value = value
            self.ui.TempSetPoint.setText(f"Setpoint Temp: {value}°C")
        
    def startSimulation(self, checked):
        """
        Starts or stops the simulation based on the On/Off button state.

        Args:
            checked (bool): True if the button is toggled on, False otherwise.
        """
        if checked:
            initial_conditions = {
                "indoor_temp": self.ui.IndoorTempSlider.value(),
                "outdoor_temp": self.ui.OutdoorTempSlider.value(),
                "heater_temp": self.ui.HeaterTempDial.value(),
                "cooler_temp": self.ui.CoolerTempDial.value(),
                "fan_speed": self.ui.FanSpeedDial.value()
            }
            # Emit signal to start simulation
            self.running = True
            self.start_simulation.emit(initial_conditions)
            self.run_simulation(initial_conditions)
        else:
            self.running = False
            self.ui.SystemStatus.setText(f"System Status:")
            self.clear_plots()

    def update_plot(self):
        """
        Updates the plots with current temperature and airflow data.
        """
        # Derive time_data from the length of sensor1.data
        self.time_data_temp = list(range(len(self.sensor1.data)))

        # Update plot lines
        self.sensor1_line.setData(self.time_data_temp, self.sensor1.data)
        self.sensor2_line.setData(self.time_data_temp, self.sensor2.data)

        self.time_data_airflow = list(range(len(self.airflow_data))) ## TODO fix airflow plot
        self.airflow_line.setData(self.time_data_airflow, self.airflow_data) ## TODO fix airflow plot

    def clear_plots(self):
        """
        Clears the data from all plots to avoid overlapping plots on restart.
        """
        # Clear data for temperature plots
        self.sensor1.data = []
        self.sensor2.data = []
        self.time_data_temp = []
        self.sensor1_line.setData([], [])
        self.sensor2_line.setData([], [])

        # Clear data for airflow plot
        self.airflow_data = []
        self.time_data_airflow = []
        self.airflow_line.setData([], [])

        # Remove legends if they exist
        if self.ui.TempPlotWidget.plotItem.legend is not None:
            self.ui.TempPlotWidget.plotItem.legend.scene().removeItem(self.ui.TempPlotWidget.plotItem.legend)
            self.ui.TempPlotWidget.plotItem.legend = None

        if self.ui.AirflowPlotWidget.plotItem.legend is not None:
            self.ui.AirflowPlotWidget.plotItem.legend.scene().removeItem(self.ui.AirflowPlotWidget.plotItem.legend)
            self.ui.AirflowPlotWidget.plotItem.legend = None

        # Re-add legends
        self.ui.TempPlotWidget.addLegend()
        self.ui.AirflowPlotWidget.addLegend()

    def on_close(self):
        """
        Custom method to handle cleanup and exit when the GUI is closed.
        """
        print("System Shut Down.")
        sys.exit()

    def run_simulation(self, initial_conditions):

        UI_Constants.set_indoor_initial_temperature(initial_conditions["indoor_temp"])
        UI_Constants.set_outdoor_initial_temperature(initial_conditions["outdoor_temp"])
        UI_Constants.set_heater_initial_temperature(initial_conditions["heater_temp"])
        UI_Constants.set_cooler_initial_temperature(initial_conditions["cooler_temp"])
        UI_Constants.set_airflow_speed(initial_conditions["fan_speed"])

        # Initialize Pygame
        pygame.init()

        # Set up the display
        screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption('Visualization of Temperature Changes in a House')

        # Generate the grid
        vert_grid = StaggeredGrid(Point(-NODE_SIZE // 2, 0), [ROWS, COLS + 1], NODE_SIZE)
        hor_grid = StaggeredGrid(Point(0, -NODE_SIZE // 2), [ROWS + 1, COLS], NODE_SIZE)
        grid = Grid(Point(0, 0), [ROWS, COLS], NODE_SIZE)

        # Create the Layout for every room and object in the model
        outdoors = Outdoors(grid)
        room_a = Room(152, 55, "RoomA", Point(20 * NODE_SIZE, 50 * NODE_SIZE), grid)
        room_b = Room(58, 39, "RoomB", Point(100, 100), grid)
        room_c = Room(21, 39, "RoomC", Point(390, 100), grid)
        room_d = Room(72, 30, "RoomD", Point(500, 100), grid)
        door_b = Door(Point(310, 295), True, grid)
        door_c = Door(Point(400, 295), True, grid)
        door_d = Door(Point(800, 250), False, grid)
        heater = Heater("Heater RoomB", Point(200, 100), True, grid)
        cooler = AirConditioner("Air Conditioner RoomD", Point(600, 100), True, grid)
        fan = Fan("Fan RoomA", Point(300, 400), Point(0.5, 0.5), True, grid)
        fan2 = Fan("Fan RoomB", Point(400, 400), Point(0, 1), True, grid)
        self.airflow_sensor = grid.grid_map[Point(310, 400)] ## TODO fix airflow plot

        self.sensor1 = Sensor(Point(205, 290), grid)
        self.sensor2 = Sensor(Point(600, 110), grid)
        self.sensor1.set_device(heater)
        self.sensor2.set_device(cooler)
        devices = [heater, cooler, fan]
        
        # Set up real-time plot data
        self.time_data_temp = []
        self.time_data_airflow = []
        self.airflow_data = [] ## TODO fix airflow plot
        
        # Plot lines
        self.sensor1_line = self.ui.TempPlotWidget.plot(pen=pg.mkPen(color="r"), name="Sensor 1")
        self.sensor2_line = self.ui.TempPlotWidget.plot(pen=pg.mkPen(color="b"), name="Sensor 2")
        self.airflow_line = self.ui.AirflowPlotWidget.plot(pen=pg.mkPen(color="b"), name="Living Room") ## TODO fix airflow plot

        # Timer for updating the plot
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)  # Half a second
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

        self.controller.add_devices([heater, cooler])

        self.controller.add_devices([heater, cooler])

        scale = TemperatureScale(Point(1000, 90), grid)

        # Main loop
        clock = pygame.time.Clock()
        dt = clock.tick(FPS)

        # Create User event to gather data from sensor nodes and set it to poll every half second
        GET_SENSOR_DATA = pygame.USEREVENT + 1
        pygame.time.set_timer(GET_SENSOR_DATA, 500)

        # create user event to get sensors to check their current temperature and control devices
        CHECK_TEMPERATURE = pygame.USEREVENT + 2
        pygame.time.set_timer(CHECK_TEMPERATURE, 1000)

        GET_NODE_INFO = pygame.USEREVENT + 3
        pygame.time.set_timer(GET_NODE_INFO, 100)

        # Set text object font to be used in PyGame visualization
        text_font = pygame.font.SysFont('Arial', 15)
        location_info = text_font.render("", True, (0, 0, 0))
        node_info = Node(Point(0, 0))

        for node in grid.grid_map.values():
            node.set_velocity_grid(hor_grid, vert_grid)

        while self.running:
            # self.simulation_running = True
            # Act on any event
            for event in pygame.event.get():
                # When pyGame windows is closed
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    self.ui.OnOffButton.setChecked(False) # Uncheck the On/Off button when simulation windows is closed
                    self.ui.SystemStatus.setText(f"System Status:")

                # When half a second passes and user must get data
                if event.type == GET_SENSOR_DATA:
                    for node in grid.grid_map.values():
                        if isinstance(node.spec, Sensor):
                            node.spec.data.append(node.temperature)
                    
                if event.type == CHECK_TEMPERATURE:
                    for node in grid.grid_map.values():
                        if isinstance(node.spec, Sensor):
                            # Update System Status Label dynamically
                            self.ui.SystemStatus.setText(f"System Status: {self.controller.current_mode}")

                            # If the system is in Heating mode and the temperature exceeds the heater's temperature, the system switches to auto
                            if self.controller.current_mode == "Heating" and node.temperature > UI_Constants.get_heater_initial_temperature():
                                self.set_auto_mode()
                                self.controller.auto_mode(node.temperature, self.setpoint_value)
                            
                            # If the system is in Cooling mode and the temperature gets lower than the cooler's temperature, the system switches to auto
                            elif self.controller.current_mode == "Cooling" and node.temperature < UI_Constants.get_cooler_initial_temperature():
                                self.set_auto_mode()
                                self.controller.auto_mode(node.temperature, self.setpoint_value)

                            elif self.controller.current_mode == "Auto":
                                self.set_auto_mode()
                                self.controller.auto_mode(node.temperature, self.setpoint_value)
                  
                if event.type == GET_NODE_INFO:
                    position = pygame.mouse.get_pos()
                    transform_to_node = [(position[0] // 5) * 5, (position[1] // 5) * 5]
                    location = Point(transform_to_node[0], transform_to_node[1])
                    node_info = grid.grid_map[location]
                    location_info = text_font.render("Location: " + "{:.2f}".format(position[0]), True, (0, 0, 0)
                                                     
                    # For plotting
                    self.airflow_data.append(self.airflow_sensor.velocity_magnitude) ## TODO fix airflow plot

            for node in grid.grid_map.values():
                if isinstance(node.spec, TemperatureScale):
                    continue
                node.change_color(grid)
                node.update_airflow(grid, hor_grid, vert_grid)
                node.calculate_velocity_magnitude(hor_grid, vert_grid)

            # Draw nodes
            for node in grid.grid_map.values():
                pygame.draw.rect(screen, node.color, (node.location.x, node.location.y, NODE_SIZE, NODE_SIZE))

            temperature_info = text_font.render("Temperature: " + "{:.2f}".format(node_info.temperature), True,
                                                (0, 0, 0))
            airflow_info = text_font.render("Airflow: " + "{:.2f}".format(node_info.velocity_magnitude), True,
                                            (0, 0, 0))
            
            screen.blit(temperature_info, (50, 550))
            screen.blit(airflow_info, (50, 600))
            screen.blit(location_info, (200, 550))

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(FPS)

if __name__ == "__main__":
    sim_manager = SimulationManager()
    sys.exit(sim_manager.app.exec_())