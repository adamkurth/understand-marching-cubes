import numpy as np
import pandas 
from LorensenLookUpTable import(
    GEOMETRY_LOOKUP,
    EDGE_DELTA,
    EDGE_DIRECTION,
    DirectionX,
    DirectionY,
    DirectionZ,
)


def interpolate(a, b, level):
    if a == b:
        return 0.05
    else:
        return (level - a) / (b - a) #linear interpolation

def show_edge_id():
    dataframe = pd.DataFrame({'idx': range(11), 
                              'delta': [(x,y,z), (x+1,y,z),(x,y+1,z), (x,y,z), (x,y,z+1), (x+1,y,z+1), (x,y+1,z), (x,y,z+1), (x,y,z), (x+1,y+1,z), (x,y+1,z)], 
                              'dir.': ['X', 'Y', 'X', 'Y', 'X', 'X', 'Y', 'Z', 'Z', 'Z', 'Z']})
    return dataframe
    
def marching(volume, level=0.0):
    vertices = []
    vertex_ids = []  # store the unique vertex IDs
    triangle_ids = []  # store the unique triangle IDs
    triangles = []  # store the unique indexed triangles
    volume_test = volume > level
    dimZ, dimY, dimX = volume.shape
    dimXY = dimX * dimY 

    def calculate_vertex_id(x, y, z, direction):
        return (x + y * dimX + z * dimXY) * 3 + direction

    for z in range(dimZ - 1):
        for y in range(dimY - 1):
            for x in range(dimX - 1):
                
                def edge_to_vertex_id(edge_number):
                    dx, dy, dz = EDGE_DELTA[edge_number]
                    direction = EDGE_DIRECTION[edge_number]
                    return calculate_vertex_id(x + dx, y + dy, z + dz, direction)
                    
                # Check for a surface crossing and create vertices
                if volume_test[z, y, x] != volume_test[z, y, x + 1]:
                    delta = interpolate(volume[z, y, x], volume[z, y, x + 1], level)
                    vertices.append([x + delta, y, z])
                    vertex_ids.append(calculate_vertex_id(x, y, z, DirectionX))

                if volume_test[z, y, x] != volume_test[z, y + 1, x]:
                    delta = interpolate(volume[z, y, x], volume[z, y + 1, x], level)
                    vertices.append([x, y + delta, z])
                    vertex_ids.append(calculate_vertex_id(x, y, z, DirectionY))

                if volume_test[z, y, x] != volume_test[z + 1, y, x]:
                    delta = interpolate(volume[z, y, x], volume[z + 1, y, x], level)
                    vertices.append([x, y, z + delta])
                    vertex_ids.append(calculate_vertex_id(x, y, z, DirectionZ))

                # calculate volume type
                # calculating volume type: 2**8 = 256 possible configurations
                # in same direction: add 1 (x,y,z)
                # in x direction: add 2 (x+1,y,z)
                # in x, then y direction: add 4 (x+1,y+1,z)
                # in y direction: add 8 (x,y+1,z)
                # in z direction: add 16 (x,y,z+1)
                # in z then x direction: (x+1,y,z+1)
                # etc...
                
                volume_type = 0
                if volume_test[z, y, x]:
                    volume_type |= 1 << 0
                if volume_test[z, y, x + 1]:
                    volume_type |= 1 << 1
                if volume_test[z, y + 1, x + 1]:
                    volume_type |= 1 << 2
                if volume_test[z, y + 1, x]:
                    volume_type |= 1 << 3
                if volume_test[z + 1, y, x]:
                    volume_type |= 1 << 4
                if volume_test[z + 1, y, x + 1]:
                    volume_type |= 1 << 5
                if volume_test[z + 1, y + 1, x + 1]:
                    volume_type |= 1 << 6
                if volume_test[z + 1, y + 1, x]:
                    volume_type |= 1 << 7
                    
                # geometry for 256 times is reduced to 15 due to symmetry (rotation)
                # marching cubes algorithm doesn't exploit any symmetric properties
                # import look-up table which contains the geometry information we need.  
                
                # lookup geometry 
                lookup = GEOMETRY_LOOKUP[volume_type]
                for i in range(0, len(lookup), 3):
                    if lookup[i] < 0:
                        break
                    edge0, edge1, edge2 = lookup[i : i+3]
                    vertex_id0 = edge_to_vertex_id(edge0)
                    vertex_id1 = edge_to_vertex_id(edge1)
                    vertex_id2 = edge_to_vertex_id(edge2)
                    triangle_ids.append([vertex_id0, vertex_id1, vertex_id2])
            
    order_of_ids = {id: order for order, id in enumerate(vertex_ids)}
    for triangle_corners in triangle_ids:
        triangles.append([order_of_ids[id] for id in triangle_corners])


    return vertices, triangle_ids, vertex_ids


if __name__ == "__main__":
    volume = np.load('test_volume.npy')
    level = 0.05
    print(f'volume loaded with shape {volume.shape}')
    print(f'processing volume with level {level}')
    vertices, triangles, vertex_ids = marching(volume, level)
    print(f'marching {len(vertices)} vertices and {len(triangles)} triangles')
    
