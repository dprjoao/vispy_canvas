import numpy as np
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from vispy import scene, app
from vispy_canvas import volume_slices, XYZAxis, CanvasControls
from typing import Union, Tuple, List, Dict

IMAGE_SHAPE = (600, 800)  # (height, width)
CANVAS_SIZE = (800, 600)  # (width, height)

class SeismicCanvas(scene.SceneCanvas, CanvasControls):
    
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
            print(slice_.pos)
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

