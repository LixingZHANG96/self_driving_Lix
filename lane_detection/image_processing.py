import cv2
from .parameters import *
import cv2

from .parameters import *


class image_feature:
    """
    The class takes in an image matrix and can do multiple openCV operations on the image.
    """
    def __init__(self, img):
        """
        The initialization takes in an image matrix.
        For 2-dim images, format must be GRAY;
        for 3-dim images, format must be BGR.

        :param img: 2-dim or 3-dim image matrix
        """

    def channel_selection(self, label):
        """TODO: Get the specified channel image."""

    def binary_threshold(self, thresholds):
        """TODO: Create a binary image, in which 0 refers to the region within the thresholds. """

    def gaussian_blur(self, sigma, k_size=3):
        """TODO: Use a Gaussian Kernel to blur the image"""

    def sobel_convolute(self, method, k_size=3):
        """TODO: Use a Sobel kernel to calculate the derivative of the image."""

    def __and__(self, other):
        """TODO: Return the bitwise-and result of 2 image matrices"""

    def __or__(self, other):
        """TODO: Return the bitwise-or result of 2 image matrices"""

    def __xor__(self, other):
        """TODO: Return the bitwise-xor result of 2 images matrices"""

    def __add__(self, other):
        """TODO: Combine the 2 image features by setting them to 2 color channels."""


class feature_collector:
    """
    Collects a list of features extracted from a single image.
    Use them for showing, combination, or simply acts as a pipeline.
    :self.attribute img: the BGR or GRAY image matrix
    :self.attribute feature_dict: list of image_feature instance
    :self.attribute color_model: the color model of image
    """

    def __init__(self, img, color_model='BGR'):
        """
        The initialization takes in an image matrix.
        Acceptable formats including:
            GRAY scale
            all validate color formats supported by openCV
        Images would be in default stored as uint8 format in BGR or GRAY.
        If the format is not BGR for a 3-dim image, a [format] must be assigned.

        :param img: 2-dim or 3-dim image matrix
        :param color_model: labels among: BAYER_BG, HLS, HSV, LAB, RGB, BGR, GRAY...
        """
        self.img = img
        self.feature_dict = dict(origin=img.copy())
        self.normalize()
        if len(img.shape) == 2:
            self.color_model = 'GRAY'
        elif color_model != 'BGR':
            l_valid_color_format = [key for key in cv2.__dict__.keys()
                                    if key.startswith('COLOR')
                                    and key.endswith('2BGR')
                                    and len(key.split('_')) == 2]
            if color_model in l_valid_color_format:
                cvt_method = "cv2.COLOR_"+color_model+"2BGR"
                self.img = cv2.cvtColor(self.img, eval(cvt_method))
            else:
                print('Unknown color model, please manually transfer to BGR.')
        self.color_model = 'BGR'

    def normalize(self):
        """TODO: Normalize the image."""

    def add_feature(self, key):
        """TODO: Add a new image_feature instance to the self.feature_dict by the key."""

    def __call__(self, method='and', **kwargs):
        """TODO: Combine all features in the self.feature_dict by the method."""


def region_of_interest(img, vertices):
    """
    Creates an image mask.

    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black.
    `vertices` should be a numpy array of integer points.
    """
    # defining a blank mask to start with
    mask = np.zeros_like(img)

    # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    # filling pixels inside the polygon defined by "vertices" with the fill color
    cv2.fillPoly(mask, vertices, ignore_mask_color)

    # returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def line_vertices(img_BGR):
    """
    Accepts an RGB image array, return a tuple of (lines, vertices) for region selection.

    Input:
    img_RGB: 3-tunnel image array, with size of Height * Width * Tunnels

    Output:
    lines: cordinates list of all lines to be drawn, size: 1 * Number_of_Lines * 4
    vertices: cordinates numpy array of all vertices, size: 1 * Number_of_Vertices * 2
    """
    y_max, x_max, _ = img_BGR.shape
    # Assign cordinates for the 4 corners
    Point_Lower_Left = (round(0.05 * x_max), y_max - 1)
    Point_Lower_Right = (round(0.98 * x_max), y_max - 1)
    Point_Upper_Left = (round(0.45 * x_max), round(0.6 * y_max))
    Point_Upper_Right = (round(0.55 * x_max), round(0.6 * y_max))
    Point_list = [Point_Lower_Left, Point_Lower_Right,
                  Point_Upper_Right, Point_Upper_Left]
    line = []
    vertices = []
    for i in range(len(Point_list)):
        line.append(Point_list[0] + Point_list[1])
        vertices.append(Point_list[0])
        Point_list = Point_list[1:] + Point_list[:1]
    lines = [line]
    vertices = np.array([vertices])
    return (lines, vertices)


def sobel_mag_thresh(img, sobel_kernel=3, mag_thresh=(0, 255), dir_thresh=(0,np.pi/2)):
    """Use Sobel kernels to calculate the magnitude&direction of derivatives of an image.

    :input: img: image object RGB/GRAY
    :input: mag_thresh: tuple of magnitude thresholds
    :input: dir_thresh: tuple of direction thresholds
    :input: sobel_kernel: size of the sobel kernel

    :output: output_img: pixels where the sobel magnitude and direction both fall in their thresholds.
    """
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    elif len(img.shape) == 2:
        img_gray = cv2.copy(img)
    dx_img_sobel = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=sobel_kernel)
    dy_img_sobel = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=sobel_kernel)
    d_img_mag = np.sqrt(np.square(dx_img_sobel) + np.square(dy_img_sobel))
    d_img_dir = np.arctan2(np.absolute(dy_img_sobel), np.absolute(dx_img_sobel))
    d_img_mag_scaled = np.uint8(255 * d_img_mag / d_img_mag.max())
    d_img_mag_bin = (d_img_mag_scaled > mag_thresh[0]) & (d_img_mag_scaled < mag_thresh[1])
    d_img_dir_bin = (d_img_dir > dir_thresh[0]) & (d_img_dir < dir_thresh[1])
    return np.uint8(d_img_mag_bin&d_img_dir_bin)*255


def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    """
    `img` should be the output of a Canny transform.

    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array(
        []), minLineLength=min_line_len, maxLineGap=max_line_gap)
    ##lane_line = hough2lane_lines(lines, img)
    ##line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    ##draw_lines(line_img, lane_line)
    return lines


def hough2lane_lines(hough_line_list, img):
    """
    According to given hough lines, calculate 2 lane lines which averages lane lines on both sides.
    """
    h_img, w_img, _ = img.shape
    kl_min = -10
    kl_max = -0.5
    kr_min = 0.5
    kr_max = 10

    # Group all lines into 2 lists. Each line should be listed together with its k.
    line_list_l = []
    line_list_r = []

    for hough_line in hough_line_list:
        k = (hough_line[0][3]-hough_line[0][1])/(hough_line[0][2]-hough_line[0][0])
        if k > kl_min and k < kl_max:
            line_list_l.append(hough_line)
        elif k > kr_min and k < kr_max:
            line_list_r.append(hough_line)

    # Average all ks
    k_l = 0
    k_r = 0
    x_list_l = []
    y_list_l = []
    x_list_r = []
    y_list_r = []

    if len(line_list_l) > 0:
        for line in line_list_l:
            x_list_l.append(line[0][0])
            x_list_l.append(line[0][2])
            y_list_l.append(line[0][1])
            y_list_l.append(line[0][3])
            k_l = (max(y_list_l)-min(y_list_l))/(max(x_list_l)-min(x_list_l))

    if len(line_list_r) > 0:
        for line in line_list_r:
            x_list_r.append(line[0][0])
            x_list_r.append(line[0][2])
            y_list_r.append(line[0][1])
            y_list_r.append(line[0][3])
            k_r = (max(y_list_r)-min(y_list_r))/(max(x_list_r)-min(x_list_r))

    # To Do: Calculate the 2 x cordinates in the 2 lines to be returned
    line_l = [0, h_img-1, 0, 0.6*h_img]
    line_r = [w_img-1, h_img-1, w_img-1, 0.6*h_img]
    if k_l != 0:
        line_l[0] = min(x_list_l) - (line_l[1] - max(y_list_l))/k_l
        line_l[2] = max(x_list_l) - (line_l[3] - min(y_list_l))/k_l
    if k_r != 0:
        line_r[0] = min(x_list_r) + (line_r[1] - min(y_list_r))/k_r
        line_r[2] = max(x_list_r) + (line_r[3] - max(y_list_r))/k_r
    line_l = [map(int,line_l)]
    line_r = [map(int,line_r)]

    return np.array([line_l, line_r])
