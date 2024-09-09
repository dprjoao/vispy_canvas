import numpy as np
from vispy import scene
from vispy.scene.visuals import Text
from vispy import scene
from vispy.visuals.transforms import STTransform

# Create a canvas with a 3D viewport
canvas = scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()
view.camera = scene.cameras.TurntableCamera(fov=45)

# Define the size of your grid
grid_size = 10
spacing = 1

# Create a grid using lines (visualization of the 3D grid)
grid_lines = []
for i in range(grid_size + 1):
    # X-axis lines (parallel to YZ plane)
    grid_lines.append([[i*spacing, 0, 0], [i*spacing, grid_size*spacing, 0]])  # Z = 0
    grid_lines.append([[i*spacing, 0, grid_size*spacing], [i*spacing, grid_size*spacing, grid_size*spacing]])  # Z = grid_size

    # Y-axis lines (parallel to XZ plane)
    grid_lines.append([[0, i*spacing, 0], [grid_size*spacing, i*spacing, 0]])  # Z = 0
    grid_lines.append([[0, i*spacing, grid_size*spacing], [grid_size*spacing, i*spacing, grid_size*spacing]])  # Z = grid_size

    # Z-axis lines (parallel to XY plane)
    grid_lines.append([[0, 0, i*spacing], [grid_size*spacing, 0, i*spacing]])
    grid_lines.append([[0, grid_size*spacing, i*spacing], [grid_size*spacing, grid_size*spacing, i*spacing]])

# Convert to numpy array for visual
grid_lines = np.array(grid_lines)
grid_visual = scene.visuals.Line(grid_lines, color='white', connect='segments')
view.add(grid_visual)

# Add axis labels
axis_labels = ['X', 'Y', 'Z']
for i, axis in enumerate(axis_labels):
    label = scene.visuals.Text(axis, color='white', font_size=20)
    label.transform = STTransform(translate=(grid_size*spacing if i == 0 else 0,
                                             grid_size*spacing if i == 1 else 0,
                                             grid_size*spacing if i == 2 else 0))
    view.add(label)

# Now create the 3D slices (assuming you have slices ready to visualize)
# Example: Creating a simple 3D slice (this will vary based on your data)
volume_data = np.random.rand(grid_size, grid_size, grid_size)

# Create a volume visual for the slices
volume = scene.visuals.Volume(volume_data, parent=view.scene, threshold=0.2)

# Set up the camera to look at the entire scene
view.camera.set_range((0, grid_size*spacing), (0, grid_size*spacing), (0, grid_size*spacing))

canvas.show()

if __name__ == '__main__':
    canvas.app.run()
