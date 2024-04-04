import argparse
import sys

sys.path.append("./")

from lib.remesher import remesh, save_mesh
from lib.map_read_write import read_3d_map
from lib.visualize_model import render_3d_model
from lib.utils import cprint, Col

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert a 3D map to a mesh")

    parser.add_argument(
        "map_filename",
        type=str,
        help="The CSV 3D map file generated by reconstruct.py",
    )

    parser.add_argument(
        "mesh_filename", type=str, help="The output PLY filename", default="mesh.ply"
    )

    parser.add_argument(
        "--detail", type=int, help="the detail level of the mesh", default=8
    )

    args = parser.parse_args()

    if not args.mesh_filename.endswith(".ply"):
        cprint("Failed to remesh, file output extension must by .ply", format=Col.FAIL)
        quit()

    led_map = read_3d_map(args.map_filename)

    if led_map is None:
        quit()

    mesh = remesh(led_map, args.detail)

    if not save_mesh(mesh, args.mesh_filename):
        cprint(f"Failed to save mesh to {args.mesh_filename}", format=Col.FAIL)
    render_3d_model(led_map, mesh=mesh)