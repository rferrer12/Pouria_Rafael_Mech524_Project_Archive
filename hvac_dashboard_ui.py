from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

class Ui_Dialog(object):
    """
    Base class for all UI components

    Attributes:
        mainLayout: Grid layout for the main dialog window.
        TempPlotWidget: Plot widget for displaying temperature readings.
        AirflowPlotWidget: Plot widget for displaying airflow readings.
        SystemStatus: Label for displaying the current system status.
        InitialConditions: Frame for setting initial conditions.
        Control: Frame for controlling system modes and settings.
        SetInitialConditions: Label for displaying initial conditions setup.
        SetControllerModes: Label for controller modes setup.
        OnOffButton: Checkbox for toggling the system on or off.
        IndoorTemperature: Label for indoor temperature slider.
        IndoorTempSlider: Slider for setting the indoor temperature.
        OutdoorTemperature: Label for outdoor temperature slider.
        OutdoorTempSlider: Slider for setting the outdoor temperature.
        HeaterTempDial, CoolerTempDial, FanSpeedDial: Dials for setting heater, cooler, and fan speeds.
        HeaterTemp, CoolerTemp, FanSpeed: Labels for heater, cooler, and fan speed dials.
        HeaterDialValue, CoolerDialValue, FanSpeedDialValue: Labels for displaying the values of the dials.
        HeatingModeButton, CoolingModeButton, VentilationModeButton, AutoModeButton: Buttons for setting various modes.
        TempSetPoint: Label for temperature setpoint slider.
        SliderTempSetPointAuto: Slider for setting temperature setpoints in auto mode.
    """
    def setupUi(self, Dialog):
        """
        Sets up the UI for the dialog window

        Arguments:
            Dialog: The main dialog window
        """
        Dialog.setObjectName("Dialog")
        Dialog.resize(1000, 700)

        # Set main layout
        self.mainLayout = QtWidgets.QGridLayout(Dialog)
        self.mainLayout.setContentsMargins(10, 10, 10, 10)

        # Temperature Plot
        self.TempPlotWidget = pg.PlotWidget(Dialog)
        self.TempPlotWidget.setBackground("w")
        self.TempPlotWidget.setTitle("Sensor Temperature Readings", color="k", size="12pt")
        self.TempPlotWidget.setLabel("left", "Temperature (°C)", color="k", size="14pt")
        self.TempPlotWidget.setLabel("bottom", "Time (s)", color="k", size="14pt")
        self.TempPlotWidget.addLegend()
        self.TempPlotWidget.showGrid(x=True, y=True)
        self.mainLayout.addWidget(self.TempPlotWidget, 1, 0, 1, 2)

        # Airflow Plot
        self.AirflowPlotWidget = pg.PlotWidget(Dialog)
        self.AirflowPlotWidget.setBackground("w")
        self.AirflowPlotWidget.setTitle("Sensor Airflow Readings", color="k", size="12pt")
        self.AirflowPlotWidget.setLabel("left", "Airflow (m³/s)", color="k", size="14pt")
        self.AirflowPlotWidget.setLabel("bottom", "Time (s)", color="k", size="14pt")
        self.AirflowPlotWidget.addLegend()
        self.AirflowPlotWidget.showGrid(x=True, y=True)
        self.mainLayout.addWidget(self.AirflowPlotWidget, 2, 0, 1, 2)  # Positioned below the temperature plot

        # System Status Label
        self.SystemStatus = QtWidgets.QLabel("System Status:", Dialog)
        self.SystemStatus.setObjectName("SystemStatus")
        self.mainLayout.addWidget(self.SystemStatus, 0, 2, 1, 1)

        # Initial Conditions Frame
        self.InitialConditions = QtWidgets.QFrame(Dialog)
        self.InitialConditions.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.InitialConditions.setObjectName("InitialConditions")
        self.setupInitialConditions()
        self.mainLayout.addWidget(self.InitialConditions, 1, 2, 1, 2)

        # Control Frame
        self.Control = QtWidgets.QFrame(Dialog)
        self.Control.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Control.setObjectName("Control")
        self.setupControlFrame()
        self.mainLayout.addWidget(self.Control, 2, 2, 1, 2)

        # Retranslation and Slot Connections
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def setupInitialConditions(self):
        """
        Sets up the initial conditions frame
        """
        layout = QtWidgets.QVBoxLayout(self.InitialConditions)

        self.SetInitialConditions = QtWidgets.QLabel("Set Initial Conditions", self.InitialConditions)
        self.SetInitialConditions.setObjectName("SetInitialConditions")
        layout.addWidget(self.SetInitialConditions)

        # Center the text in the layout
        self.SetInitialConditions.setAlignment(QtCore.Qt.AlignCenter)

        # Set a larger font
        font_SetInitialConditions = QtGui.QFont()
        font_SetInitialConditions.setPointSize(11) 
        self.SetInitialConditions.setFont(font_SetInitialConditions)

        # System On/Off Button
        self.OnOffButton = QtWidgets.QCheckBox("System On / Off", self.InitialConditions)
        self.OnOffButton.setObjectName("OnOffButton")
        layout.addWidget(self.OnOffButton)

        # Set a bold font
        font_OnOffButton = QtGui.QFont()
        font_OnOffButton.setBold(True)
        self.OnOffButton.setFont(font_OnOffButton)

        # Indoor Temperature Slider
        self.IndoorTemperature = QtWidgets.QLabel("Indoor Temperature")
        self.IndoorTempSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.IndoorTempSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.IndoorTempSlider.setTickInterval(3)
        self.IndoorTempSlider.setRange(-5, 35)
        layout.addWidget(self.IndoorTemperature)
        layout.addWidget(self.IndoorTempSlider)

        # Outdoor Temperature Slider
        self.OutdoorTemperature = QtWidgets.QLabel("Outdoor Temperature")
        self.OutdoorTempSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.OutdoorTempSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.OutdoorTempSlider.setTickInterval(4)
        self.OutdoorTempSlider.setRange(-20, 45)
        layout.addWidget(self.OutdoorTemperature)
        layout.addWidget(self.OutdoorTempSlider)

        # Dials Layout
        dialLayout = QtWidgets.QHBoxLayout()

        self.HeaterTempDial = self.createDial("HeaterTempDial", 30, 85)
        self.CoolerTempDial = self.createDial("CoolerTempDial", 0, 15)
        self.FanSpeedDial = self.createDial("FanSpeedDial", 10, 30)

        self.HeaterTemp = QtWidgets.QLabel("Heater Temp")
        self.CoolerTemp = QtWidgets.QLabel("Cooler Temp")
        self.FanSpeed = QtWidgets.QLabel("Fan Speed")

        dialLayout.addWidget(self.HeaterTempDial)
        dialLayout.addWidget(self.CoolerTempDial)
        dialLayout.addWidget(self.FanSpeedDial)

        labelLayout = QtWidgets.QHBoxLayout()
        labelLayout.addWidget(self.HeaterTemp)
        labelLayout.addWidget(self.CoolerTemp)
        labelLayout.addWidget(self.FanSpeed)

        self.HeaterDialValue = QtWidgets.QLabel("", self.InitialConditions)
        self.CoolerDialValue = QtWidgets.QLabel("", self.InitialConditions)
        self.FanSpeedDialValue = QtWidgets.QLabel("", self.InitialConditions)

        valueLayout = QtWidgets.QHBoxLayout()
        valueLayout.addWidget(self.HeaterDialValue)
        valueLayout.addWidget(self.CoolerDialValue)
        valueLayout.addWidget(self.FanSpeedDialValue)

        layout.addLayout(dialLayout)
        layout.addLayout(labelLayout)
        layout.addLayout(valueLayout)

    def setupControlFrame(self):
        """
        Sets up the control frame
        """
        layout = QtWidgets.QVBoxLayout(self.Control)

        self.SetControllerModes = QtWidgets.QLabel("Set Controller Modes", self.Control)
        self.SetControllerModes.setObjectName("SetControllerModes")
        layout.addWidget(self.SetControllerModes)

        # Center the text in the layout
        self.SetControllerModes.setAlignment(QtCore.Qt.AlignCenter)

        # Set a larger font
        font_SetControllerModes = QtGui.QFont()
        font_SetControllerModes.setPointSize(11) 
        self.SetControllerModes.setFont(font_SetControllerModes)

        # Mode Buttons
        buttonLayout = QtWidgets.QVBoxLayout()

        self.HeatingModeButton = self.createButton("Heating")
        self.CoolingModeButton = self.createButton("Cooling")
        self.VentilationModeButton = self.createButton("Ventilation")
        self.AutoModeButton = self.createButton("Auto")

        buttonLayout.addWidget(self.HeatingModeButton)
        buttonLayout.addWidget(self.CoolingModeButton)
        buttonLayout.addWidget(self.VentilationModeButton)
        buttonLayout.addWidget(self.AutoModeButton)

        layout.addLayout(buttonLayout)

        # Temperature Setpoint Slider
        self.TempSetPoint = QtWidgets.QLabel("Temperature Setpoint")
        self.SliderTempSetPointAuto = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.SliderTempSetPointAuto.setRange(10, 30)
        self.SliderTempSetPointAuto.setValue(20)
        self.SliderTempSetPointAuto.setTickInterval(2)  # Tick marks every 2 units
        self.SliderTempSetPointAuto.setTickPosition(QtWidgets.QSlider.TicksBelow)
        layout.addWidget(self.TempSetPoint)
        layout.addWidget(self.SliderTempSetPointAuto)

    def retranslateUi(self, Dialog):
        """
        Sets the translations and titles for the UI components

        Arguments:
            Dialog: The main dialog window
        """
        Dialog.setWindowTitle("HVAC System")

    def createDial(self, name, minimum, maximum):
        """
        Creates a QDial widget

        Arguments:
            name: The object name of the dial
            minimum: The minimum value of the dial
            maximum: The maximum value of the dial

        Returns:
            QDial: A configured QDial widget
        """
        dial = QtWidgets.QDial()
        dial.setObjectName(name)
        dial.setRange(minimum, maximum)
        dial.setNotchesVisible(True)
        return dial

    def createButton(self, text):
        """
        Creates a QPushButton widget

        Arguments:
            text: The text to display on the button

        Returns:
            QPushButton: A configured QPushButton widget
        """
        button = QtWidgets.QPushButton(text)
        return button

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
