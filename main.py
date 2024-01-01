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

    for z in range(dimZ):
        for y in range(dimY):
            for x in range(dimX):
                
                def edge_to_vertex_id(edge_number):
                    dx, dy, dz = EDGE_DELTA[edge_number]
                    direction = EDGE_DIRECTION[edge_number]
                    return calculate_vertex_id(x + dx, y + dy, z + dz, direction)
                    
                # Check for a surface crossing and create vertices
                if x < (dimX - 1) and volume_test[z, y, x] != volume_test[z, y, x + 1]:
                    delta = interpolate(volume[z, y, x], volume[z, y, x + 1], level)
                    vertices.append([x + delta, y, z])
                    vertex_ids.append(calculate_vertex_id(x, y, z, DirectionX))

                if y < (dimY - 1) and volume_test[z, y, x] != volume_test[z, y + 1, x]:
                    delta = interpolate(volume[z, y, x], volume[z, y + 1, x], level)
                    vertices.append([x, y + delta, z])
                    vertex_ids.append(calculate_vertex_id(x, y, z, DirectionY))

                if z < (dimZ - 1) and volume_test[z, y, x] != volume_test[z + 1, y, x]:
                    delta = interpolate(volume[z, y, x], volume[z + 1, y, x], level)
                    vertices.append([x, y, z + delta])
                    vertex_ids.append(calculate_vertex_id(x, y, z, DirectionZ))

                if x == (dimX - 1) or y == (dimY - 1) or z == (dimZ - 1):
                    continue
                    
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
        
    return vertices, triangle_ids


if __name__ == "__main__":
    volume = np.load('test_volume.npy')
    print(f'Volume loaded with shape {volume.shape}')
    
    for level in [0.05, -0.05, 0.0005, -0.0005]:
        print(f'Processing volume with level {level}', '\n\n')
        vertices, triangles = marching(volume, level)
        
        import skimage
        vertices_sk, triangles_sk, _, _ = skimage.measure.marching_cubes(volume, level=level, method="lorensen")
        vertices_sk = vertices_sk.tolist()
        
        print('Comparing results with skimage')
        print(f'Marching {len(vertices)} vertices and {len(triangles)} triangles')
        print(f'skimage {len(vertices_sk)} vertices and {len(triangles_sk)} triangles')
        print()
        
        vertices.sort()
        vertices_sk.sort()
        print('Comparing vertices')
        print(vertices[:10])
        print(vertices_sk[:10])
        

        np.savez(f"/Users/adamkurth/Documents/vscode/python_4_fun/marching_cubes_demo/tmp/marching_{level}.npz", 
                    vertices=vertices, 
                    triangles=triangles, 
                    vertices_sk=vertices_sk,
                    triangles_sk=triangles_sk
                    )
        