import cv2
from collections import deque
import numpy as np
from context import get_context

def shape_match(source, template, roi=None, threshold=0.75):
    """Match shapes ignoring color and texture"""
    # Convert grayscale to remove color information
    source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    source_gray = cv2.GaussianBlur(source_gray, (3, 3), 0)
    template_gray = cv2.GaussianBlur(template_gray, (3, 3), 0)

    # Apply adaptive thresholding to binarize images
    # This removes texture and focuses on shape outlines
    source_bin = cv2.adaptiveThreshold(source_gray, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 19, 0)
    template_bin = cv2.adaptiveThreshold(template_gray, 255,
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 19, 0)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
    source_processed = cv2.morphologyEx(source_bin, cv2.MORPH_CLOSE, kernel)
    template_processed = cv2.morphologyEx(template_bin, cv2.MORPH_CLOSE, kernel)

    # Apply ROI if specified
    if roi is not None:
        x, y, w, h = roi
        source_roi = source_processed[y:y + h, x:x + w]
    else:
        source_roi = source_processed

    # Perform template matching
    result = cv2.matchTemplate(source_roi, template_processed,
                               cv2.TM_CCOEFF_NORMED)

    # Find matches above threshold
    locs = np.where(result >= threshold)
    matches = []
    h, w = template_processed.shape

    for pt in zip(*locs[::-1]):  # Switch x,y coordinates
        if roi:
            global_pt = (pt[0] + roi[0], pt[1] + roi[1])
        else:
            global_pt = (pt[0], pt[1])

        matches.append({
            'location': global_pt,
            'size': (w, h),
            'confidence': result[pt[1], pt[0]]  # y,x format
        })

    return matches

def estimate_block_size(matches):
    widths = [m['size'][0] for m in matches]
    heights = [m['size'][1] for m in matches]
    return int(np.mean(widths)), int(np.mean(heights))

def deduplicate_matches(matches, pixel_thresh=10):
    deduped = []
    seen = []
    for m in matches:
        x, y = m['location']
        if all(abs(x - sx) > pixel_thresh or abs(y - sy) > pixel_thresh for sx, sy in seen):
            seen.append((x, y))
            deduped.append(m)
    return deduped

def snap_to_grid(x, y, w, h, tolerance=0.3):
    gx = int((x + w * tolerance) // w)
    gy = int((y + h * tolerance) // h)
    return gx, gy

def convert_matches_to_grid(matches, w, h, tolerance=0.3):
    grid_points = set()
    for m in matches:
        x, y = m['location']
        gx, gy = snap_to_grid(x, y, w, h, tolerance)
        grid_points.add((gx, gy))
    return grid_points

def group_grid_shapes(points):
    visited = set()
    groups = []

    def bfs(start):
        q = deque([start])
        group = []
        while q:
            x, y = q.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            group.append((x, y))
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                neighbor = (x+dx, y+dy)
                if neighbor in points and neighbor not in visited:
                    q.append(neighbor)
        return group

    for pt in points:
        if pt not in visited:
            groups.append(bfs(pt))
    return groups

def shape_to_matrix(shape):
    xs = [x for x, y in shape]
    ys = [y for x, y in shape]
    min_x, min_y = min(xs), min(ys)
    width = max(xs) - min_x + 1
    height = max(ys) - min_y + 1
    mat = [[0]*width for _ in range(height)]
    for x, y in shape:
        mat[y - min_y][x - min_x] = 1
    return min_x, mat

def extract_sorted_shape_matrices(matches, tolerance=0.3, pixel_dedup=10):
    matches = deduplicate_matches(matches, pixel_thresh=pixel_dedup)
    w, h = estimate_block_size(matches)
    grid_points = convert_matches_to_grid(matches, w, h)
    grouped_shapes = group_grid_shapes(grid_points)
    shape_matrices = [shape_to_matrix(g) for g in grouped_shapes]
    shape_matrices.sort(key=lambda x: x[0])  # sort left to right
    print(f"<UNK> Shape Matrices:\n{shape_matrices}")
    return [(mat, _) for _, mat in shape_matrices]

def get_block_shapes(img_path, threshold=0.28):
    template = cv2.imread(get_context().block_template_path)
    source = cv2.imread(img_path)
    matches = shape_match(source, template, roi=get_context().block_roi, threshold=threshold)
    return extract_sorted_shape_matrices(matches, tolerance=0.3, pixel_dedup=10)

if __name__ == "__main__":
    import os
    from context import set_context
    set_context(13)

    image_files = "test_data/"
    for i, image_file in enumerate(os.listdir(image_files)):
        if image_file.startswith("."):
            continue
        img_path = os.path.join(image_files, image_file)
        print(f"{i}: {img_path}")
        source = cv2.imread(img_path)
        shapes = get_block_shapes(img_path)
        print(shapes)
        # Visualize results
        # output_img = source.copy()
        # for match in matches:
        #     x, y = match['location']
        #     w, h = match['size']
        #     cv2.rectangle(output_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #     cv2.putText(output_img, f"Conf: {match['confidence']:.2f}",
        #                 (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)
        # cv2.imshow(f'Matches_{i}', output_img)
        # cv2.waitKey(0)

