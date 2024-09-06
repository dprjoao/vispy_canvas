from PyQt5 import QtWidgets, QtCore
import numpy as np

from vispy_canvas.seismic_canvas_hdf5_pilot import CanvasWrapper

class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()

        self._canvas_wrapper = CanvasWrapper()
        main_layout.addWidget(self._canvas_wrapper.native)

        # Create UI controls
        control_layout = QtWidgets.QHBoxLayout()

        # X Slice Slider
        self.x_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.x_slider.setMinimum(0)
        self.x_slider.setMaximum(self._canvas_wrapper.vol.shape[0] - 1)
        self.x_slider.setValue(0)
        self.x_slider.valueChanged.connect(self.update_x_slice)
        control_layout.addWidget(QtWidgets.QLabel("X Slice"))
        control_layout.addWidget(self.x_slider)

        # Y Slice Slider
        self.y_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.y_slider.setMinimum(0)
        self.y_slider.setMaximum(self._canvas_wrapper.vol.shape[1] - 1)
        self.y_slider.setValue(self._canvas_wrapper.vol.shape[1] - 1)
        self.y_slider.valueChanged.connect(self.update_y_slice)
        control_layout.addWidget(QtWidgets.QLabel("Y Slice"))
        control_layout.addWidget(self.y_slider)

        # Z Slice Slider
        self.z_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.z_slider.setMinimum(0)
        self.z_slider.setMaximum(self._canvas_wrapper.vol.shape[2] - 1)
        self.z_slider.setValue(0)
        self.z_slider.valueChanged.connect(self.update_z_slice)
        control_layout.addWidget(QtWidgets.QLabel("Z Slice"))
        control_layout.addWidget(self.z_slider)

        # Add buttons to step through slices
        self.prev_x_button = QtWidgets.QPushButton("Previous X Slice")
        self.prev_x_button.clicked.connect(lambda: self.step_slice('x', -1))
        control_layout.addWidget(self.prev_x_button)

        self.next_x_button = QtWidgets.QPushButton("Next X Slice")
        self.next_x_button.clicked.connect(lambda: self.step_slice('x', 1))
        control_layout.addWidget(self.next_x_button)

        self.prev_y_button = QtWidgets.QPushButton("Next Y Slice")
        self.prev_y_button.clicked.connect(lambda: self.step_slice('y', -1))
        control_layout.addWidget(self.prev_y_button)

        self.next_y_button = QtWidgets.QPushButton("Previous Y Slice")
        self.next_y_button.clicked.connect(lambda: self.step_slice('y', 1))
        control_layout.addWidget(self.next_y_button)

        self.prev_z_button = QtWidgets.QPushButton("Next Z Slice")
        self.prev_z_button.clicked.connect(lambda: self.step_slice('z', 1))
        control_layout.addWidget(self.prev_z_button)

        self.next_z_button = QtWidgets.QPushButton("Previous Z Slice")
        self.next_z_button.clicked.connect(lambda: self.step_slice('z', -1))
        control_layout.addWidget(self.next_z_button)

        main_layout.addLayout(control_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle('3D Viewer')

    def update_x_slice(self, value):
        self._canvas_wrapper.xpos = value
        self._canvas_wrapper.set_position(self._canvas_wrapper.xpos , 'x')

    def update_y_slice(self, value):
        self._canvas_wrapper.ypos = value
        self._canvas_wrapper.set_position(self._canvas_wrapper.ypos , 'y')

    def update_z_slice(self, value):
        self._canvas_wrapper.zpos = value
        self._canvas_wrapper.set_position(self._canvas_wrapper.zpos , 'z')

    def step_slice(self, axis, step):
        if axis == 'x':
            new_value = self._canvas_wrapper.xpos + step
            new_value = np.clip(new_value, 0, self._canvas_wrapper.vol.shape[0] - 1)
            self._canvas_wrapper.xpos = new_value
            self.x_slider.setValue(new_value)
            self._canvas_wrapper.set_position(self._canvas_wrapper.xpos, axis)
        elif axis == 'y':
            new_value = self._canvas_wrapper.ypos + step
            new_value = np.clip(new_value, 0, self._canvas_wrapper.vol.shape[1] - 1)
            self._canvas_wrapper.ypos = new_value
            self.y_slider.setValue(new_value)
            self._canvas_wrapper.set_position(self._canvas_wrapper.ypos, axis)
        elif axis == 'z':
            new_value = self._canvas_wrapper.zpos + step
            new_value = np.clip(new_value, 0, self._canvas_wrapper.vol.shape[2] - 1)
            self._canvas_wrapper.zpos = new_value
            self.z_slider.setValue(new_value)
            self._canvas_wrapper.set_position(self._canvas_wrapper.zpos, axis)

        

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = MyMainWindow()
    win.show()
    app.exec_()
