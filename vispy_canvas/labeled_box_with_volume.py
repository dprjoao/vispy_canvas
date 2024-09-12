"""
Demonstration of an empty box (wireframe cube) with axis labels and 3D slices of random data using Vispy.
"""

import sys
from vispy import scene
import numpy as np

canvas = scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()

# Generate random 3D data
data_shape = (25, 50, 80)  # Size of the 3D data
data = np.random.random(data_shape)

# Define the 8 corners of the cube
cube_vertices = np.array([
    [0, 0, 0],  # Origin
    [1, 0, 0],  # X axis positive
    [1, 1, 0],  # XY face positive
    [0, 1, 0],  # Y axis positive
    [0, 0, 1],  # Z axis positive
    [1, 0, 1],  # XZ face positive
    [1, 1, 1],  # XYZ positive
    [0, 1, 1]   # YZ face positive
])

# Scale factor
Nx = data_shape[0] + 2
Ny = data_shape[1] + 2
Nz = data_shape[2] + 2
scalex = Nx
scaley = Ny
scalez = Nz
scale = [scalex, scaley, scalez] 
scaled_vertices = cube_vertices * scale
print(scaled_vertices)
# Define the edges of the cube (connecting the vertices)
cube_edges = np.array([
    [0, 1], [1, 2], [2, 3], [3, 0],  # Bottom face
    [4, 5], [5, 6], [6, 7], [7, 4],  # Top face
    [0, 4], [1, 5], [2, 6], [3, 7]   # Vertical edges
])

# Get the positions of the edges by referencing the scaled vertices
positions = np.concatenate([scaled_vertices[edge] for edge in cube_edges])

# Create the Line visual for the edges of the cube
box = scene.visuals.Line(pos=positions, color='white', width=2, connect='segments')

# Add the wireframe cube to the view
view.add(box)

# Add axis labels with names
axis_length = scale  # Length of the axis
spacingx = 1  # Spacing between labels
spacingy = 2
spacingz = 4
# X axis labels (from 0 to axis_length)
for i in range(0, int(axis_length[0] // spacingx) + 1, spacingx):
    label_pos = np.array([i * spacingx, 0, 0])
    label = scene.visuals.Text(f'{i * spacingx:.1f}', pos=label_pos, color='red', font_size=160, anchor_x='center', anchor_y='center')
    view.add(label)
label2 = scene.visuals.Text('Crossline', pos=np.array([axis_length[0] / 2, -0.5, 0]), color='red', font_size=200, anchor_x='center', anchor_y='center')
view.add(label2)

# Y axis labels (from 0 to axis_length)
for i in range(0, int(axis_length[1] // spacingy) + 1, spacingy):
    label_pos = np.array([0, i * spacingy, 0])
    label = scene.visuals.Text(f'{i * spacingy:.1f}', pos=label_pos, color='green', font_size=160, anchor_x='center', anchor_y='center')
    view.add(label)
label3 = scene.visuals.Text('Inline', pos=np.array([0, axis_length[1] / 2, -0.5]), color='green', font_size=200, anchor_x='center', anchor_y='center')
view.add(label3)

# Z axis labels (from axis_length to 0)
for i in range(int(axis_length[2] // spacingz), -1, -1):
    label_pos = np.array([0, 0, i * spacingz])
    label = scene.visuals.Text(f'{i * spacingz:.1f}', pos=label_pos, color='blue', font_size=160, anchor_x='center', anchor_y='center')
    view.add(label)
label4 = scene.visuals.Text('Time', pos=np.array([0, -0.5, axis_length[2] / 2]), color='blue', font_size=200, anchor_x='center', anchor_y='center')
view.add(label4)

# Create the Volume visual for the random data
volume = scene.visuals.Volume(data.T, method='iso', clim=(0, 1), cmap='viridis')

# Apply scaling transformation using MatrixTransform
from vispy.visuals.transforms import MatrixTransform
transform = MatrixTransform()
#transform.scale((scale, scale, scale))

center = scene.transforms.STTransform(translate=(1.5, 1.5, 0.5))
volume.transform = center

# Add the volume to the view
view.add(volume)

# Set the camera for 3D interaction
view.camera = 'turntable'

# Adjust camera settings to ensure the cube and labels are properly visible
view.camera.fov = 45  # Field of view for a better perspective
view.camera.distance = 30  # Increase the distance from the cube to the camera to fit the volume data

canvas.show()

if __name__ == '__main__':
    if sys.flags.interactive != 1:
        canvas.app.run()
