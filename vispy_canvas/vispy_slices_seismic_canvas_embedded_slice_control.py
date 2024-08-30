import numpy as np
from PyQt5 import QtWidgets, QtCore
from vispy import scene
from vispy_canvas import volume_slices, XYZAxis, CanvasControls, AxisAlignedImage
from typing import Union, Tuple, List, Dict

IMAGE_SHAPE = (600, 800)  # (height, width)
CANVAS_SIZE = (800, 600)  # (width, height)

class CanvasWrapper(scene.SceneCanvas, CanvasControls):
    
    def __init__(
        self,
        size: Tuple = CANVAS_SIZE,
        visual_nodes: Union[List, Dict] = None,
        grid: Tuple = None,
        share: bool = False,
        bgcolor: str = 'black',
        cbar_region_ratio: float = 0.125,
        keys = 'interactive',

        # for camera
        scale_factor: float = None,
        center=None,
        fov: float = 30,
        azimuth: float = 50,
        elevation: float = 50,
        zoom_factor: float = 1.0,
        axis_scales: Tuple = (1.0, 1.0, 1.0),
        auto_range: bool = True,

        # for save
        savedir: str = './',
        title: str = '3D Viewer',
    ):

        self.pngDir = savedir
        # Initialize the SceneCanvas with the proper parameters
        scene.SceneCanvas.__init__(self, 
                                   size=size, 
                                   keys=keys, 
                                   show=True,
                                   bgcolor=bgcolor,
                                   title=title)

        self.unfreeze()

        self.init_size = size
        self.cbar_ratio = cbar_region_ratio
        self.fov = fov
        self.azimuth = azimuth
        self.elevation = elevation
        self.scale_factor = scale_factor
        self.center = center
        self.auto_range = auto_range
        if not self.auto_range:
            zoom_factor = 1
        self.zoom_factor = zoom_factor
        self.share = share

        # Initialize attributes required by CanvasControls
        self.drag_mode = False
        self.hover_on = None
        self.selected = None

        self.central_widget.add_grid()

        self.view = self.central_widget.add_view()

        # Load seismic data
        self.vol = self.load_data(filepath='train_seismic.npy')

        # Set initial slice indices
        self.slice_x = self.vol.shape[0] // 2
        self.slice_y = self.vol.shape[1] // 2
        self.slice_z = self.vol.shape[2] // 2

        # Generate the slices using the volume_slices function
        self.slices = volume_slices(self.vol, 
                                    x_pos=self.slice_x, 
                                    y_pos=self.slice_y, 
                                    z_pos=self.slice_z, 
                                    cmaps='gray')
        
        # Add the slices to the scene
        for slice_ in self.slices:
            slice_.parent = self.view.scene

        # Set up a 3D camera
        self.camera = scene.cameras.TurntableCamera(parent=self.view.scene, 
                                                    azimuth=self.azimuth, 
                                                    elevation=self.elevation, 
                                                    fov=self.fov, 
                                                    distance=500)
        
        self.view.camera = self.camera

        self.scale_factor = self.view.camera.scale_factor
        self.zoom_factor = self.view.camera.zoom_factor

        # Add XYZ Axis to the scene
        self.axis = XYZAxis()
        self.axis.parent = self.view
        self.axis.canvas_size = self.size
        self.events.resize.connect(self.axis.on_resize)
        self.axis.highlight.parent = self.view
        self.axis._update_axis()
        self.events.mouse_move.connect(self.axis.on_mouse_move)

        self.view.camera.set_range()

        self.freeze()

    def load_data(self, filepath, dtype=np.float32):
        self.vol = np.load(filepath).astype(dtype)
        return self.vol
            
    def set_position(self, pos, axis):
        
        if pos < 0 or len(self.slices) == 0:
            return
        
        pos = int(pos)
        
        for node in self.slices:
            if isinstance(node, AxisAlignedImage) and node.axis == axis:
                node._update_location(pos)

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
        self.x_slider.setValue(self._canvas_wrapper.slice_x)
        self.x_slider.valueChanged.connect(self.update_x_slice)
        control_layout.addWidget(QtWidgets.QLabel("X Slice"))
        control_layout.addWidget(self.x_slider)

        # Y Slice Slider
        self.y_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.y_slider.setMinimum(0)
        self.y_slider.setMaximum(self._canvas_wrapper.vol.shape[1] - 1)
        self.y_slider.setValue(self._canvas_wrapper.slice_y)
        self.y_slider.valueChanged.connect(self.update_y_slice)
        control_layout.addWidget(QtWidgets.QLabel("Y Slice"))
        control_layout.addWidget(self.y_slider)

        # Z Slice Slider
        self.z_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.z_slider.setMinimum(0)
        self.z_slider.setMaximum(self._canvas_wrapper.vol.shape[2] - 1)
        self.z_slider.setValue(self._canvas_wrapper.slice_z)
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

        self.prev_y_button = QtWidgets.QPushButton("Previous Y Slice")
        self.prev_y_button.clicked.connect(lambda: self.step_slice('y', -1))
        control_layout.addWidget(self.prev_y_button)

        self.next_y_button = QtWidgets.QPushButton("Next Y Slice")
        self.next_y_button.clicked.connect(lambda: self.step_slice('y', 1))
        control_layout.addWidget(self.next_y_button)

        self.prev_z_button = QtWidgets.QPushButton("Previous Z Slice")
        self.prev_z_button.clicked.connect(lambda: self.step_slice('z', -1))
        control_layout.addWidget(self.prev_z_button)

        self.next_z_button = QtWidgets.QPushButton("Next Z Slice")
        self.next_z_button.clicked.connect(lambda: self.step_slice('z', 1))
        control_layout.addWidget(self.next_z_button)

        main_layout.addLayout(control_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle('3D Viewer')

    def update_x_slice(self, value):
        self._canvas_wrapper.slice_x = value
        self._canvas_wrapper.set_position(self._canvas_wrapper.slice_x , 'x')

    def update_y_slice(self, value):
        self._canvas_wrapper.slice_y = value
        self._canvas_wrapper.set_position(self._canvas_wrapper.slice_y , 'y')

    def update_z_slice(self, value):
        self._canvas_wrapper.slice_z = value
        self._canvas_wrapper.set_position(self._canvas_wrapper.slice_z , 'z')

    def step_slice(self, axis, step):
        if axis == 'x':
            new_value = self._canvas_wrapper.slice_x + step
            new_value = np.clip(new_value, 0, self._canvas_wrapper.vol.shape[0] - 1)
            self._canvas_wrapper.slice_x = new_value
            self.x_slider.setValue(new_value)
            self._canvas_wrapper.set_position(self._canvas_wrapper.slice_x, axis)
        elif axis == 'y':
            new_value = self._canvas_wrapper.slice_y + step
            new_value = np.clip(new_value, 0, self._canvas_wrapper.vol.shape[1] - 1)
            self._canvas_wrapper.slice_y = new_value
            self.y_slider.setValue(new_value)
            self._canvas_wrapper.set_position(self._canvas_wrapper.slice_y, axis)
        elif axis == 'z':
            new_value = self._canvas_wrapper.slice_z + step
            new_value = np.clip(new_value, 0, self._canvas_wrapper.vol.shape[2] - 1)
            self._canvas_wrapper.slice_z = new_value
            self.z_slider.setValue(new_value)
            self._canvas_wrapper.set_position(self._canvas_wrapper.slice_z, axis)

        

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = MyMainWindow()
    win.show()
    app.exec_()
