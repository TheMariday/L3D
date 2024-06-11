import colorsys
import time
import cv2
import numpy as np
import open3d
from multiprocessing import Process
from lib.led_map_3d import LEDMap3D
from lib.camera_map_3d import CameraMap3D
from lib.file_monitor import FileMonitor
from lib.sfm.read_write_model import qvec2rotmat

def render_2d_model(led_map):
    display = np.ones((640, 640, 3)) * 0.2

    max_id = max(led_map.keys())

    for led_id in led_map:
        col = colorsys.hsv_to_rgb(led_id / max_id, 0.5, 1)
        image_point = (led_map[led_id]["pos"] * 640).astype(int)
        cv2.drawMarker(display, image_point, color=col)
        cv2.putText(
            display,
            str(led_id),
            image_point,
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color=col,
        )

    cv2.imshow("MariMapper", display)
    cv2.waitKey(0)


class Renderer3D(Process):

    def __init__(self, map_filename, camera_filename=None):
        super().__init__()
        self.file_monitor = FileMonitor(map_filename)
        self.camera_filename = camera_filename
        self._vis = None

    def __del__(self):
        if self._vis is not None:
            self._vis.destroy_window()

    def _initialise_visualiser(self):

        self._vis = open3d.visualization.Visualizer()
        self._vis.create_window(
            window_name=f"MariMapper - {self.file_monitor.filepath}",
            width=640,
            height=640,
        )

        self.point_cloud = open3d.geometry.PointCloud()

        view_ctl = self._vis.get_view_control()
        view_ctl.set_up((0, 1, 0))
        view_ctl.set_lookat((0, 0, 0))
        view_ctl.set_zoom(0.3)

        render_options = self._vis.get_render_option()
        render_options.point_show_normal = True
        render_options.point_color_option = (
            open3d.visualization.PointColorOption.YCoordinate
        )
        render_options.background_color = [0.2, 0.2, 0.2]

    def run(self):

        self.file_monitor.wait_for_existence()

        self._initialise_visualiser()

        self.reload_geometry(first=True)
        last_file_check = time.time()
        while True:
            if time.time() - last_file_check > 1:
                last_file_check = time.time()
                if self.file_monitor.file_changed():
                    self.reload_geometry()

            if not self._vis.poll_events():
                break

            self._vis.update_renderer()

    def reload_geometry(self, first=False):

        led_map = LEDMap3D(filename=self.file_monitor.filepath)

        xyz = [led_map[led_id]["pos"] for led_id in led_map.keys()]
        normals = [led_map[led_id]["normal"] for led_id in led_map.keys()]

        self.point_cloud.points = open3d.utility.Vector3dVector(xyz)
        self.point_cloud.normals = open3d.utility.Vector3dVector(normals)

        if first:
            self._vis.add_geometry(self.point_cloud, reset_bounding_box=True)

        self._vis.update_geometry(self.point_cloud)


def draw_camera(position, rotation):
    t = position
    R = qvec2rotmat(rotation)
    color = [0.8, 0.8, 0.8]

    # points in pixel
    points_pixel = [
        [0, 0, 0],
        [0, 0, 1],
        [1, 0, 1],
        [0, 1, 1],
        [1, 1, 1],
    ]


    # pyramid
    points_in_world = [(R @ p + t) for p in points_pixel]
    lines = [
        [0, 1],
        [0, 2],
        [0, 3],
        [0, 4],
    ]
    colors = [color for _ in range(len(lines))]
    line_set = open3d.geometry.LineSet(
        points=open3d.utility.Vector3dVector(points_in_world),
        lines=open3d.utility.Vector2iVector(lines),
    )
    line_set.colors = open3d.utility.Vector3dVector(colors)

    # return as list in Open3D format
    return line_set
