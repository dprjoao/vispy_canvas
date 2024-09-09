import numpy as np
from PyQt5 import QtWidgets, QtCore
from vispy import scene
from vispy_canvas import volume_slices, XYZAxis, CanvasControls, AxisAlignedImage
from vispy_canvas.camera_mixin import InertiaTurntableCamera
from typing import Union, Tuple, List, Dict
import h5py

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
        *args, **kwargs):

        self.pngDir = savedir
        # Initialize the SceneCanvas with the proper parameters
        scene.SceneCanvas.__init__(self, 
                                   size=size, 
                                   keys=keys, 
                                   show=True,
                                   bgcolor=bgcolor,
                                   title=title,
                                   dpi=1)

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
        self.load_data(filepath='train_seismic.npy')

        self.xpos = 0
        self.ypos = 0
        self.zpos = 0      
        # Generate the slices using the volume_slices function
        self.slices = volume_slices(self.vol, 
                                    x_pos=self.xpos, 
                                    y_pos=self.ypos, 
                                    z_pos=self.zpos, 
                                    cmaps='gray',
                                    clims = [-1, 1]
                                    )
        
        # Add the slices to the scene
        for slice_ in self.slices:
            slice_.parent = self.view.scene

        # Set up a 3D camera with inertia
        self.camera = InertiaTurntableCamera(fov=45, elevation=30, azimuth=30)

        self.view.camera = self.camera
        # Connect events
        self.events.mouse_move.connect(self.camera.on_mouse_move)
        self.events.mouse_press.connect(self.camera.on_mouse_move)
        self.events.mouse_release.connect(self.camera.on_mouse_move)
        self.events.mouse_release.connect(self.camera.apply_inertia)

        self.view.camera = self.camera

        # Automatically set the range of the canvas, display, and wrap up.
        if auto_range: self.camera.set_range()
        # Record the scale factor for a consistent camera reset.
        self.scale_factor = self.camera.scale_factor
        # Zoom in or out after auto range setting.
        self.zoom_factor = zoom_factor
        self.camera.scale_factor /= self.zoom_factor
        self.show()
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

    # Adjust the path to match your dataset
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

