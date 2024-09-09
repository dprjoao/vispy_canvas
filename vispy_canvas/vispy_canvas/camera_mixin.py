from vispy import scene
import numpy as np
from PyQt5 import QtCore

class InertiaTurntableCamera(scene.cameras.TurntableCamera):
    def __init__(self, inertia_factor=0.95, velocity_scale=0.1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inertia_factor = inertia_factor
        self.velocity_scale = velocity_scale
        self.last_mouse_pos = None
        self.mouse_vel = np.array([0.0, 0.0])
        self.inertia_active = False
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.apply_inertia())
        self.timer.start(8)  # ~60 FPS refresh rate


    def on_mouse_move(self, event):
        if event.is_dragging:
            if self.last_mouse_pos is not None:
                delta = (event.pos - self.last_mouse_pos) * self.velocity_scale
                self.mouse_vel = delta
                #print(f"Mouse velocity: {self.mouse_vel}")
            self.last_mouse_pos = event.pos
        else:
            self.last_mouse_pos = None
            if np.linalg.norm(self.mouse_vel) > 0:
                self.inertia_active = True

    def apply_inertia(self, _=None):
        #if self.inertia_active:
        #self.inertia_active = True
        #print(f"Inertia active? {self.inertia_active}")
        #print(f"Before decay: {self.mouse_vel}")
        self.mouse_vel *= self.inertia_factor  # Apply slow decay
        #print(f"After decay: {self.mouse_vel}")
        
        if np.linalg.norm(self.mouse_vel) < 0.00001:
            self.mouse_vel = np.array([0.0, 0.0])
            self.inertia_active = False

            self._simulate_camera_movement(self.mouse_vel)

    def _simulate_camera_movement(self, delta):
        # Calculate delta based on the current mouse position
        #print(f"Simulated delta: {delta}")

        # Adjust azimuth and elevation based on delta
        self.azimuth += delta[0] * 0.2  # Adjust this multiplier for sensitivity
        self.elevation += delta[1] * 0.2  # Adjust this multiplier for sensitivity

        # Apply the new state to the camera
        self.set_state({'azimuth': self.azimuth, 'elevation': self.elevation})
        print(f"Updated azimuth: {self.azimuth}, elevation: {self.elevation}")
        

        # Update last mouse position
        self.last_mouse_pos = self.last_mouse_pos + delta if self.last_mouse_pos is not None else np.array([0.0, 0.0])
