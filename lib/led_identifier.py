import cv2
from lib.utils import cprint, Col


class LedResults:

    def __init__(self, u, v, width, height, contours):
        self.u = u
        self.v = v
        self.width = width
        self.height = height
        self.contours = contours

    def get_center_normalised(self):
        v_offset = (self.width - self.height) / 2.0

        return self.u / self.width, (self.v + v_offset) / self.width

    def get_center(self):
        return self.u, self.v


class LedFinder:

    def __init__(self, threshold=128):
        self.threshold = threshold

    def find_led(self, image):

        _, image_thresh = cv2.threshold(image, self.threshold, 255, cv2.THRESH_TOZERO)

        contours, _ = cv2.findContours(
            image_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        led_response_count = len(contours)
        if led_response_count == 0:
            return None
        elif led_response_count > 1:
            cprint(
                f"Warning! More than 1 light source found, found {led_response_count} light sources",
                format=Col.WARNING,
            )

        moments = cv2.moments(image_thresh)

        if moments["m00"] == 0:
            return None

        img_height = image.shape[0]
        img_width = image.shape[1]

        center_u = moments["m10"] / moments["m00"]
        center_v = moments["m01"] / moments["m00"]

        return LedResults(center_u, center_v, img_width, img_height, contours)

    @staticmethod
    def draw_results(image, results):

        render_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        if results:
            cv2.drawContours(render_image, results.contours, -1, (255, 0, 0), 1)
            cv2.drawMarker(
                render_image,
                [int(i) for i in results.get_center()],
                (0, 255, 0),
                markerSize=100,
            )

        return render_image
