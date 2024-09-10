from vispy import app, scene
import numpy as np

# Hardcoded dimensions
N_X = 10
N_Y = 10
N_frame = 10

# Create the canvas
canvas = scene.SceneCanvas(keys='interactive', size=(1280, 1024), position=(0, 0), bgcolor='white', dpi=450)

# Add a ViewBox to let the user zoom/rotate
view = canvas.central_widget.add_view()

# Draw the bounding lines
for p in ([1, 1, 1, -1, 1, 1], [1, 1, -1, -1, 1, -1], [1, -1, 1, -1, -1, 1],
          [1, -1, -1, -1, -1, -1], [1, 1, 1, 1, -1, 1], [-1, 1, 1, -1, -1, 1],
          [1, 1, -1, 1, -1, -1], [-1, 1, -1, -1, -1, -1], [1, 1, 1, 1, 1, -1],
          [-1, 1, 1, -1, 1, -1], [1, -1, 1, 1, -1, -1], [-1, -1, 1, -1, -1, -1]):
    line = scene.visuals.Line(pos=np.array([[p[0]*N_X/2, p[1]*N_Y/2, p[2]*N_frame/2],
                                            [p[3]*N_X/2, p[4]*N_Y/2, p[5]*N_frame/2]]),
                              color='black', parent=view.scene)

# Draw XYZ axes
axisX = scene.visuals.Line(pos=np.array([[0, -N_Y/2, 0], [0, N_Y/2, 0]]), color='red', parent=view.scene)
axisY = scene.visuals.Line(pos=np.array([[-N_X/2, 0, 0], [N_X/2, 0, 0]]), color='green', parent=view.scene)
axisZ = scene.visuals.Line(pos=np.array([[0, 0, -N_frame/2], [0, 0, N_frame/2]]), color='blue', parent=view.scene)

# Add axis labels
t = {}
for text in ['x', 'y', 't']:
    t[text] = scene.visuals.Text(text, parent=canvas.scene, color='black')
    t[text].font_size = 8
#t['x'].pos = canvas.size[0] // 3, canvas.size[1] - canvas.size[1] // 8
#t['y'].pos = canvas.size[0] - canvas.size[0] // 4, canvas.size[1] - canvas.size[1] // 8
#t['t'].pos = canvas.size[0] // 6, canvas.size[1] // 2

# Set up the camera
axis = scene.visuals.XYZAxis(parent=view.scene)
cam = scene.TurntableCamera(elevation=20, azimuth=30)
cam.fov = 45
cam.scale_factor = N_X * 2.
cam.set_range((-N_X/2, N_X/2), (-N_Y/2, N_Y/2), (-N_frame/2, N_frame/2))
view.camera = cam

# Render the canvas
canvas.show()
if __name__ == '__main__':
    app.run()
