import numpy as np
import matplotlib.pyplot as plt
from skimage import measure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Create a simple scalar field with an interesting surface
x, y, z = np.linspace(-3, 3, 30), np.linspace(-3, 3, 30), np.linspace(-3, 3, 30)
X, Y, Z = np.meshgrid(x, y, z)
# Example scalar field: a spherical shape with varying radius
scalar_field = X**2 + Y**2 + Z**2

# Isosurface level
iso_level = 9

# Run the marching cubes algorithm to find the isosurface
vertices, faces, normals, values = measure.marching_cubes(scalar_field, level=iso_level)

# Create a 3D plot
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

# Plot the isosurface
mesh = Poly3DCollection(vertices[faces], alpha=0.7, edgecolor='k')
face_color = [0.45, 0.45, 0.75]  # Alternative: 'cyan'
mesh.set_facecolor(face_color)
ax.add_collection3d(mesh)

# Set the aspect ratio of the plot to be equal
ax.set_aspect('auto')

# Set the limits of the plot based on the scalar field bounds
ax.set_xlim(0, scalar_field.shape[0])
ax.set_ylim(0, scalar_field.shape[1])
ax.set_zlim(0, scalar_field.shape[2])

# Set labels
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')

# Show the plot
plt.tight_layout()
plt.show()
