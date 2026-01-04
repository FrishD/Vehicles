import cv2
import numpy as np

class PerspectiveManager:
    def __init__(self, frame_size=(1920, 1080)):
        self.w, self.h = frame_size
        self.matrix = None
        self.inv_matrix = None

        # Default Trapezoid (approximation for 45-60 degree drone tilt)
        # These are normalized coordinates [0, 1]
        self.src_pts = np.float32([
            [0.35, 0.45], # Top Left
            [0.65, 0.45], # Top Right
            [0.95, 0.95], # Bottom Right
            [0.05, 0.95]  # Bottom Left
        ])

        self.dst_pts = np.float32([
            [0, 0],       # Top Left
            [1, 0],       # Top Right
            [1, 1],       # Bottom Right
            [0, 1]        # Bottom Left
        ])

        self._update_matrices()

    def _update_matrices(self):
        """Calculates the Homography matrix based on normalized points."""
        # Scale source points to frame size
        src = np.array([
            [self.src_pts[0][0] * self.w, self.src_pts[0][1] * self.h],
            [self.src_pts[1][0] * self.w, self.src_pts[1][1] * self.h],
            [self.src_pts[2][0] * self.w, self.src_pts[2][1] * self.h],
            [self.src_pts[3][0] * self.w, self.src_pts[3][1] * self.h]
        ], dtype=np.float32)

        # BEV size
        self.bev_size = (800, 800)

        # Scale destination points to BEV size
        dst = np.array([
            [self.dst_pts[0][0] * self.bev_size[0], self.dst_pts[0][1] * self.bev_size[1]],
            [self.dst_pts[1][0] * self.bev_size[0], self.dst_pts[1][1] * self.bev_size[1]],
            [self.dst_pts[2][0] * self.bev_size[0], self.dst_pts[2][1] * self.bev_size[1]],
            [self.dst_pts[3][0] * self.bev_size[0], self.dst_pts[3][1] * self.bev_size[1]]
        ], dtype=np.float32)

        self.matrix = cv2.getPerspectiveTransform(src, dst)
        self.inv_matrix = cv2.getPerspectiveTransform(dst, src)

    def to_bev(self, frame):
        """Warps a frame to Bird's Eye View."""
        return cv2.warpPerspective(frame, self.matrix, self.bev_size)

    def map_point_to_bev(self, x, y):
        """Maps a point (x,y) from original frame to BEV coordinates."""
        pts = np.float32([[x, y]]).reshape(-1, 1, 2)
        transformed = cv2.perspectiveTransform(pts, self.matrix)
        return transformed[0][0]

    def map_point_from_bev(self, x, y):
        """Maps a point from BEV back to original frame."""
        pts = np.float32([[x, y]]).reshape(-1, 1, 2)
        transformed = cv2.perspectiveTransform(pts, self.inv_matrix)
        return transformed[0][0]

    def set_source_points(self, points):
        """Allows manual calibration of the trapezoid."""
        if len(points) == 4:
            self.src_pts = np.float32(points)
            self._update_matrices()

    def auto_calibrate_by_vanishing_point(self, lines):
        """
        TODO: Implement automatic calibration based on lane line convergence.
        For now, we stick to the preset.
        """
        pass