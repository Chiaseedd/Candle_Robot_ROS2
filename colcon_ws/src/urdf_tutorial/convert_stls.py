import os
import struct

def convert_ascii_to_binary(filepath):
    """Converts a single ASCII STL file to a Binary STL file."""
    try:
        with open(filepath, 'r') as f:
            header = f.readline().strip()
            if not header.lower().startswith("solid"):
                print(f"Skipping {filepath}: Doesn't start with 'solid' (might already be binary).")
                return False

            facets = []
            while True:
                line = f.readline()
                if not line:
                    break
                
                parts = line.split()
                if not parts:
                    continue
                
                if parts[0].lower() == "facet":
                    # facet normal ni nj nk
                    normal = [float(parts[2]), float(parts[3]), float(parts[4])]
                    f.readline() # outer loop
                    
                    # vertex v1x v1y v1z
                    v1 = [float(x) for x in f.readline().split()[1:4]]
                    # vertex v2x v2y v2z
                    v2 = [float(x) for x in f.readline().split()[1:4]]
                    # vertex v3x v3y v3z
                    v3 = [float(x) for x in f.readline().split()[1:4]]
                    
                    f.readline() # endloop
                    f.readline() # endfacet
                    
                    facets.append((normal, v1, v2, v3))
                elif parts[0].lower() == "endsolid":
                    break

        print(f"Read {len(facets)} facets from {filepath}.")

        # Write Binary STL
        with open(filepath, 'wb') as f:
            # 80 byte header
            f.write(b'\0' * 80)
            
            # Number of triangles (4 bytes, uint32)
            f.write(struct.pack('<I', len(facets)))
            
            for normal, v1, v2, v3 in facets:
                # Normal (3 floats)
                f.write(struct.pack('<3f', *normal))
                # V1 (3 floats)
                f.write(struct.pack('<3f', *v1))
                # V2 (3 floats)
                f.write(struct.pack('<3f', *v2))
                # V3 (3 floats)
                f.write(struct.pack('<3f', *v3))
                # Attribute byte count (2 bytes, uint16)
                f.write(struct.pack('<H', 0))
                
        print(f"Successfully converted {filepath} to binary.")
        return True
    
    except Exception as e:
        print(f"Error converting {filepath}: {e}")
        return False

def main():
    mesh_dir = '/mnt/c/Users/User/Downloads/Candle_TheRobot-main/colcon_ws/src/urdf_tutorial/meshes'
    if not os.path.exists(mesh_dir):
        print(f"Directory {mesh_dir} not found.")
        return

    for filename in os.listdir(mesh_dir):
        if filename.lower().endswith('.stl'):
            filepath = os.path.join(mesh_dir, filename)
            convert_ascii_to_binary(filepath)

if __name__ == '__main__':
    main()
