import sys
import numpy as np
from vispy import scene
from vispy.color import Color

# Create the canvas
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)

# Set up a viewbox to display the hollow cube with interactive controls
view = canvas.central_widget.add_view()
view.bgcolor = 'black'
view.camera = 'turntable'  # Use turntable camera for 3D interaction
view.padding = 100

# Define the edge color for the cube
edge_color = Color("Red")

color = Color("White", alpha=0.9)

# Create a hollow cube (no face color, only edge color)
cube = scene.visuals.Box(1, 1, 1, color=color, edge_color=edge_color, parent=view.scene)

# Create random 3D data (e.g., 50x50x50 grid of random values)
data = np.random.rand(50, 50, 50)

# Display the random data inside the cube as a volume
volume = scene.visuals.Volume(data, parent=view.scene, threshold=0.5, method = 'mip')

# Fit the volume inside the cube (scale and translate to fit within the cube's bounds)
volume.transform = scene.transforms.STTransform(scale=(1.0 / 50, 1.0 / 50, 1.0 / 50), translate=(-0.5, -0.5, -0.5))

if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas.app.run()
