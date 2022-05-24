import os
import json
import numpy as np
from cv2 import cv2

def create_ellipse_contour(x0, y0, a, b, orientation):
    phis = np.linspace(0, 2 * np.pi, 360)
    center = np.array([[x0], [y0]])

    contour = np.array([a * np.cos(phis), b * np.sin(phis)])
    rotation = np.array([[np.cos(orientation), -np.sin(orientation)],
                         [np.sin(orientation), np.cos(orientation)]])

    contour = (center + rotation @ contour).astype(np.int32, copy=False)
    return contour


def draw_crosses(image, points, size, vertical_border, horizontal_border, channel):
    if points.shape == (0,):
        return image

    pixel = np.array([0, 0, 0])
    pixel[channel] = 255

    vertical_centers = points.T[1].astype(np.int32)
    vc = np.copy(vertical_centers)
    horisontal_centers = points.T[0].astype(np.int32)

    for i in range(size):
        vertical_centers_pi = vertical_centers + i
        vertical_centers_pi[vertical_centers_pi >= vertical_border] = vertical_border - 1
        vertical_centers_mi = vertical_centers - i
        vertical_centers_mi[vertical_centers_mi < 0] = 0

        horisontal_centers_pi = horisontal_centers + i
        horisontal_centers_pi[horisontal_centers_pi >= horizontal_border] = horizontal_border - 1
        horisontal_centers_mi = horisontal_centers - i
        horisontal_centers_mi[horisontal_centers_mi < 0] = 0

        image[vertical_centers, horisontal_centers_pi] = pixel
        image[vertical_centers_pi, horisontal_centers] = pixel
        image[vertical_centers, horisontal_centers_mi] = pixel
        image[vertical_centers_mi, horisontal_centers] = pixel

    return image


class Ellipse:
    def __init__(self, x0, y0, a, b, orientation):
        self.x0 = x0
        self.y0 = y0
        self.a = a
        self.b = b
        self.orientation = orientation

    def check_if_inside(self, x, y):
        center = np.array([[self.x0], [self.y0]])
        point = np.array([[x], [y]])
        axes_sizes = np.array([[self.a], [self.b]])

        anti_orientation = -self.orientation
        rotation = np.array([[np.cos(anti_orientation), -np.sin(anti_orientation)],
                             [np.sin(anti_orientation), np.cos(anti_orientation)]])

        point = (rotation @ (point - center)) / (axes_sizes + 0.0001)
        return True if np.sum(point ** 2) ** 0.5 < 1 else False

    def get_contour(self):
        return create_ellipse_contour(self.x0, self.y0, self.a, self.b, self.orientation)


class EllipsesPack(object):
    def __init__(self, metadata):
        self.ellipses = []
        for ellipse_parameters in metadata["regions"]:
            self.ellipses.append(Ellipse(int(ellipse_parameters["shape_attributes"]["cx"]),
                                         int(ellipse_parameters["shape_attributes"]["cy"]),
                                         int(ellipse_parameters["shape_attributes"]["rx"]),
                                         int(ellipse_parameters["shape_attributes"]["ry"]),
                                         float(ellipse_parameters["shape_attributes"]["theta"])))

    def get_contours_for_each_ellipse(self):
        pointses = []
        for ellipse in self.ellipses:
            pointses.append(ellipse.get_contour())
        return np.array(pointses)

    def get_ids_of_ellipses_with_point_inside(self, x, y):
        ellipses_id = []
        for i, ellipse in enumerate(self.ellipses):
            if ellipse.check_if_inside(x, y):
                ellipses_id.append(i)
        return ellipses_id


class MarkupIterator(object):
    def __init__(self, markup_json_file):
        with open(markup_json_file, "r") as markup_read_file:
            metadata = json.load(markup_read_file)["_via_img_metadata"]
            self.all_images_names = list(metadata.keys())

            self.current_image_id = 0

            self.ellipses_packs_for_each_image = [EllipsesPack(metadata[key]) for key in self.all_images_names]
            self.images_amount = len(self.ellipses_packs_for_each_image)

    def __iter__(self):
        self.current_image_id = -1
        return self

    def __next__(self):
        if self.current_image_id < self.images_amount - 1:
            self.current_image_id += 1
            return self
        else:
            raise StopIteration

    def get_contours_points(self):
        coordinats = self.ellipses_packs_for_each_image[self.current_image_id].get_contours_for_each_ellipse()
        coordinats = np.hstack(coordinats)
        return coordinats

    def get_name(self):
        return self.all_images_names[self.current_image_id]

    def get_ellipses(self):
        return self.ellipses_packs_for_each_image[self.current_image_id]


class QualityEstimator(object):
    def __init__(self, image, image_ellipses):
        ret, labels, stats, centroids = cv2.connectedComponentsWithStats(image)
        
        order = np.argsort(stats[:, -1])[::-1][1:]
        stats = stats[:, -1][order]
        points = centroids[order]
        
        mask = (stats > np.quantile(stats, 0.75))
        points = points[mask]
        stats = stats[mask]
        
        mean = np.mean(stats)
        median = np.median(stats)
        std = np.std(stats)

        mask = (stats > mean - std) * (stats < mean + 10 * std)
        self.points = points[mask]
        self.image_ellipses = image_ellipses

    def count_statistics(self):
        points = []
        ids_of_unique_ellipses_with_point_inside = []
        ids_of_ellipses_with_point_inside = []

        for point in self.points:
            ids = self.image_ellipses.get_ids_of_ellipses_with_point_inside(int(point[0]), int(point[1]))
            ids_of_ellipses_with_point_inside.extend(ids)
            points.extend([point.astype(np.int32) for _ in ids])

        points = np.array(points)
        ids_of_ellipses_with_point_inside = np.array(ids_of_ellipses_with_point_inside)

        ids_of_unique_ellipses_with_point_inside = np.unique(ids_of_ellipses_with_point_inside)

        true_positive = []
        repeated_detections = []
        for id in ids_of_unique_ellipses_with_point_inside:
            mask = (ids_of_ellipses_with_point_inside == id)
            true_positive.append(points[mask][0])
            repeated_detections.extend(points[mask][1:])

        return np.array(true_positive), np.array(repeated_detections)


def visualize_nn_work(MARKUP_PATH, INPUT_DIR_PATH, NN_OUTPUT_DIR_PATH, OUTPUT_DIR_PATH, TABLE_NAME,
                      negative_crosses_size=3, positive_crosses_size=5,
                      negative_color_channel=2, positive_color_channel=1):
    stats_tuples = []
    markup_iterator = MarkupIterator(MARKUP_PATH)
    if not os.path.exists(OUTPUT_DIR_PATH):
        os.makedirs(OUTPUT_DIR_PATH)

    for markup_iterator in markup_iterator:
        name = markup_iterator.get_name()
        if not os.path.exists(os.path.join(INPUT_DIR_PATH, name)):
            continue
        if not os.path.exists(os.path.join(NN_OUTPUT_DIR_PATH, name)):
            continue

        current_frame = cv2.imread(os.path.join(INPUT_DIR_PATH, markup_iterator.get_name()))
        current_nn_output = cv2.imread(os.path.join(NN_OUTPUT_DIR_PATH, markup_iterator.get_name()))
        gray_nn_output = cv2.cvtColor(current_nn_output, cv2.COLOR_BGR2GRAY)

        image_ellipses = markup_iterator.get_ellipses()
        quality_estimator = QualityEstimator(gray_nn_output, image_ellipses)

        draw_crosses(current_frame, quality_estimator.points,
                     negative_crosses_size,
                     gray_nn_output.shape[0], gray_nn_output.shape[1],
                     negative_color_channel)

        true_positive_list, repeated_detections_list = quality_estimator.count_statistics()
        true_positive = len(true_positive_list)
        false_positive = len(quality_estimator.points) - true_positive
        false_negative = len(image_ellipses.ellipses) - true_positive
        repeated_detections = len(repeated_detections_list)

        precision = true_positive / (true_positive + false_positive) if true_positive != 0 else 0
        recall = true_positive / (true_positive + false_negative) if true_positive != 0 else 0

        stats_tuples.append((markup_iterator.get_name(),
                             true_positive, false_positive, false_negative, repeated_detections,
                             precision, recall))

        contours_points = markup_iterator.get_contours_points()
        current_frame[contours_points[1], contours_points[0]] = np.array([255, 0, 0])
        draw_crosses(current_frame, true_positive_list,
                     positive_crosses_size,
                     gray_nn_output.shape[0], gray_nn_output.shape[1],
                     positive_color_channel)

        cv2.imwrite(os.path.join(OUTPUT_DIR_PATH, markup_iterator.get_name()), current_frame)

    stats_tuples = sorted(stats_tuples, key=lambda stats: stats[1])
    output = "name,true_positive,false_positive,false_negative,repeated_detections,precision,recall\n"

    mean_stats = []
    for stats in stats_tuples:
        mean_stats.append([max(0, stats[1]), 
                           max(0, stats[2]), 
                           max(0, stats[3]), 
                           max(0, stats[4]), 
                           np.max([0, stats[5]]), 
                           np.max([0, stats[6]])])
        output += f"{stats[0]}," + \
                  f"{max(0, stats[1])}," + \
                  f"{max(0, stats[2])}," + \
                  f"{max(0, stats[3])}," + \
                  f"{max(0, stats[4])}," + \
                  f"{np.round(np.max([0, stats[5]]), 2)}," + \
                  f"{np.round(np.max([0, stats[6]]), 2)}\n"
    mean_stats = np.array(mean_stats)
    mean_stats = np.mean(mean_stats, axis=0)
    output += f"mean," + \
              f"{int(mean_stats[0])},{int(mean_stats[1])},{int(mean_stats[2])},{int(mean_stats[3])}," + \
              f"{np.round(mean_stats[4], 2)}, {np.round(mean_stats[5], 2)}\n"

    with open(os.path.join(OUTPUT_DIR_PATH, TABLE_NAME), "w") as write_file:
        write_file.write(output)