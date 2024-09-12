from vispy import scene
import numpy as np
from vispy.visuals.transforms import MatrixTransform


class GridLines():
    """ Visual subclass displaying an empty labeled cube that matches the shape of
    seismic data which will be rendered inside.

    Parameters:
    shape : Tuple (x, y, z)
    """
    def __init__(self, shape, parent=None):
        # Initialize scene parent to add visuals
        self.parent = parent

        # Define the 8 corners of the cube
        self.cube_vertices = np.array([
            [0, 0, 0],  # Origin
            [1, 0, 0],  # X axis positive
            [1, 1, 0],  # XY face positive
            [0, 1, 0],  # Y axis positive
            [0, 0, 1],  # Z axis positive
            [1, 0, 1],  # XZ face positive
            [1, 1, 1],  # XYZ positive
            [0, 1, 1]   # YZ face positive
        ])

        # Define the edges of the cube (connecting the vertices)
        self.cube_edges = np.array([
            [0, 1], [1, 2], [2, 3], [3, 0],  # Bottom face
            [4, 5], [5, 6], [6, 7], [7, 4],  # Top face
            [0, 4], [1, 5], [2, 6], [3, 7]   # Vertical edges
        ])
        
        if shape is not None:
            # Scale factor
            Nx = shape[0] + 2
            Ny = shape[1] + 2
            Nz = shape[2] + 2
            scalex = Nx
            scaley = Ny
            scalez = Nz
            scale = [scalex, scaley, scalez] 
            self.scaled_vertices = self.cube_vertices * scale

            # Add axis labels with names
            self.axis_length = scale  # Length of the axis
            self.spacingx = 20  # Spacing between labels
            self.spacingy = 20
            self.spacingz = 40
            
            transform = MatrixTransform()
            transform.scale((scale, scale, scale))

    def center_data(self, data):
        self.cube_center = scene.transforms.STTransform(translate=(1.5, 1.5, 0.5))
        data.transform = self.cube_center

    def draw_edges(self):
        # Get the positions of the edges by referencing the scaled vertices
        positions = np.concatenate([self.scaled_vertices[edge] for edge in self.cube_edges])

        # Create the Line visual for the edges of the cube
        self.box = scene.visuals.Line(pos=positions, color='white', width=2, connect='segments')

        # Add the box to the parent scene
        if self.parent is not None:
            self.parent.add(self.box)

        return self.box

    def draw_labels(self, parent=None):

        # Store labels in lists for each axis
        label_x_list = []
        label_y_list = []
        label_z_list = []

        # X axis labels (from 0 to axis_length)
        for i in range(0, int(self.axis_length[0] // self.spacingx) + 1, self.spacingx):
            label_pos = np.array([i * self.spacingx, 0, 0])
            label_x = scene.visuals.Text(f'{i * self.spacingx:.1f}', pos=label_pos, color='red', font_size=500000, anchor_x='center', anchor_y='center', depth_test=True)
            label_x.order = 1  # Set render order
            label_x_list.append(label_x)
        
        label_name_x = scene.visuals.Text('Crossline', pos=np.array([self.axis_length[0] / 2, -0.5, 0]), color='red', font_size=1000000, anchor_x='center', anchor_y='center', depth_test=True)
        label_name_x.order = 1  # Set render order

        # Y axis labels (from 0 to axis_length)
        for i in range(0, int(self.axis_length[1] // self.spacingy) + 1, self.spacingy):
            label_pos = np.array([0, i * self.spacingy, 0])
            label_y = scene.visuals.Text(f'{i * self.spacingy:.1f}', pos=label_pos, color='green', font_size=500000, anchor_x='center', anchor_y='center', parent=parent, depth_test=True)
            label_y.order = 1
            label_y_list.append(label_y)

        label_name_y = scene.visuals.Text('Inline', pos=np.array([0, self.axis_length[1] / 2, -0.5]), color='green', font_size=1000000, anchor_x='center', anchor_y='center', parent=parent, depth_test=True)
        label_name_y.order = 1

        # Z axis labels (from axis_length to 0)
        for i in range(int(self.axis_length[2] // self.spacingz), -1, -1):
            label_pos = np.array([0, 0, i * self.spacingz])
            label_z = scene.visuals.Text(f'{i * self.spacingz:.1f}', pos=label_pos, color='blue', font_size=500000, anchor_x='center', anchor_y='center', parent=parent, depth_test=True)
            label_z.order = 1
            label_z_list.append(label_z)

        label_name_z = scene.visuals.Text('Time', pos=np.array([0, -0.5, self.axis_length[2] / 2]), color='blue', font_size=1000000, anchor_x='center', anchor_y='center', parent=parent, depth_test=True)
        label_name_z.order = 1

        # Return the lists of labels along with axis names
        return label_x_list, label_y_list, label_z_list, label_name_x, label_name_y, label_name_z
