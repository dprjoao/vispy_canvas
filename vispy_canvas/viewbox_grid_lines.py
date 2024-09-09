from vispy import scene
import numpy as np

# Create a canvas and add a viewbox to it
canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='black')

# Add a view (ViewBox) to the canvas
view = canvas.central_widget.add_view()

# Set up a 3D camera (e.g., TurntableCamera) to interact with the grid
view.camera = scene.cameras.TurntableCamera(fov=45, azimuth=30, elevation=30)

# Define grid line properties (color, thickness)
grid_color = (0.5, 0.5, 0.5, 1)  # light gray
grid_thickness = 2

# Add grid lines in the XY plane
grid_xy = scene.visuals.GridLines(color=grid_color)
view.add(grid_xy)

# Add grid lines in the XZ plane by rotating the grid
grid_xz = scene.visuals.GridLines(color=grid_color)
grid_xz.transform = scene.transforms.MatrixTransform()
grid_xz.transform.rotate(90, (1, 0, 0))  # Rotate the grid to the XZ plane
view.add(grid_xz)

# Add grid lines in the YZ plane by rotating the grid
grid_yz = scene.visuals.GridLines(color=grid_color)
grid_yz.transform = scene.transforms.MatrixTransform()
grid_yz.transform.rotate(90, (0, 1, 0))  # Rotate the grid to the YZ plane
view.add(grid_yz)

# Show the canvas
canvas.show()

if __name__ == '__main__':
    canvas.app.run()