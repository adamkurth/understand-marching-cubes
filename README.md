---
runme:
  id: 01HJYB3G69J4XCQXWTRHXG8FDN
  version: v2.0
---

## Marching Cubes Repository

#### Theory and Understanding

We have a function $f(x,y,z) → v$.

Use this function to sample points in regular intervals inside of the volume. Such that the highest value is white and lowest, black.

The white points represent the object, and black empty space. The white points represent the shape where it's at the surface or below (inside the shape).

**Goal**: Construct the surface marching cubes algorithm is to construct the surface from the points and display it as a mesh.


#### *Simplified* 

A cube contains 8 vertices, either inside or outside the shape. This gives $2^8$ possible configurations. 

When one point is active within the shape, this gives us a triangle. If the vertex above is active, then this gives is a plane intersecting the $xy$-axis, etc...

Only 14 unique cases, the rest are symmetries.

- Ex) Corner points 7 5 1 from 7 6 5 4 3 2 1 0 are active and converting to binary ⇒ 1 0 1 0 0 0 1 0 = 162

```python {"id":"01HJYC04KAEKDVXHPSQTTPJ9NB"}
# code to find index 
cube_index = 0
for i in range(1, 9):
    if cube.values[i] < surfaceLevel:
        cube_index |= 1 << i
```

- After finding this index in the triangulation table,  `{5, 0, 1, 5, 4, 0, 7, 6, 11}` join `(5, 0, 1)`, `(5, 4, 0)`, and `(7, 6, 11)` together to get the 3 triangles.

```python {"id":"01HJYCABWBQBQXWFHYJEA3MFFJ"}
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# cube vertices
vertices = [
    (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
    (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1),
    (0.5, 0.5, 0.5), (0.5, 0, 0), (0, 0.5, 0.5), (1, 1, 0.5)  # Additional vertices for the 11th index
]

#  Define using triangulation indices
triangulation_indices = [
    (5, 0, 1),  # 1
    (5, 4, 0),  # 2
    (7, 6, 11)  # 3
]

def plot_triangle(ax, vertices, triangle_indices):
    x = [vertices[i][0] for i in triangle_indices] + [vertices[triangle_indices[0]][0]]
    y = [vertices[i][1] for i in triangle_indices] + [vertices[triangle_indices[0]][1]]
    z = [vertices[i][2] for i in triangle_indices] + [vertices[triangle_indices[0]][2]]
    ax.plot(x, y, z, color='red')

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for triangle in triangulation_indices:
    plot_triangle(ax, vertices, triangle)
    
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Surface Triangles with Triangulation Indices')

plt.show()

```

The overarching goal is to *run through all of the cubes in the surface*, to generate the surface, in this manner.