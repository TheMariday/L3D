import numpy as np

from lib.map_read_write import get_all_maps
from lib.sfm.sfm import SFM


def check_dimensions(map_3d, max_error):
    cube_sides = []
    cube_sides.append(map_3d[2]["pos"] - map_3d[0]["pos"])
    cube_sides.append(map_3d[4]["pos"] - map_3d[6]["pos"])
    cube_sides.append(map_3d[18]["pos"] - map_3d[16]["pos"])
    cube_sides.append(map_3d[20]["pos"] - map_3d[22]["pos"])

    cube_sides.append(map_3d[4]["pos"] - map_3d[2]["pos"])
    cube_sides.append(map_3d[20]["pos"] - map_3d[18]["pos"])
    cube_sides.append(map_3d[6]["pos"] - map_3d[0]["pos"])
    cube_sides.append(map_3d[22]["pos"] - map_3d[16]["pos"])

    cube_sides.append(map_3d[16]["pos"] - map_3d[0]["pos"])
    cube_sides.append(map_3d[18]["pos"] - map_3d[2]["pos"])
    cube_sides.append(map_3d[20]["pos"] - map_3d[4]["pos"])
    cube_sides.append(map_3d[22]["pos"] - map_3d[6]["pos"])

    cube_side_lengths = [np.linalg.norm(v) for v in cube_sides]

    cube_side_length_avg = np.average(cube_side_lengths)

    cube_side_deviation = [
        length / cube_side_length_avg for length in cube_side_lengths
    ]

    assert max(cube_side_deviation) < 1 + max_error
    assert min(cube_side_deviation) > 1 - max_error


def test_reconstruction():
    maps = get_all_maps("test/scan")

    sfm = SFM(maps)

    sfm.process()

    sfm.print_points()

    assert len(sfm.maps_3d) == 21

    check_dimensions(
        sfm.maps_3d, max_error=0.01  # needs to have a max deviation of less than 1%
    )


def test_sparse_reconstruction():
    maps = get_all_maps("test/scan")

    maps_sparse = [maps[1], maps[3], maps[5], maps[7]]

    sfm = SFM(maps_sparse)

    assert sfm.process()

    sfm.print_points()

    assert len(sfm.maps_3d) == 21

    check_dimensions(
        sfm.maps_3d, max_error=0.03  # needs to have a max deviation of less than 3%
    )


def test_2_track_reconstruction():
    partial_map = get_all_maps("test/scan")[1:3]

    sfm = SFM(partial_map)

    assert sfm.process()

    sfm.print_points()

    assert len(sfm.maps_3d) == 15


def test_invalid_reconstruction_views():
    maps = get_all_maps("test/scan")

    invalid_maps = [maps[0], maps[4], maps[8]]  # no useful overlap

    sfm = SFM(invalid_maps)

    assert not sfm.process()


def test_reconstruct_higbeam():
    highbeam_map = get_all_maps("test/L3D-Test-Data/highbeam")

    sfm = SFM(highbeam_map)

    assert sfm.process()
