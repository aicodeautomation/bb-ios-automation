import cv2
import numpy as np
import matplotlib.pyplot as plt
from context import get_context
def get_current_board(current_path):
    roi_board_coords = get_context().board_roi
    # Detect blocks with mean difference comparison
    board_matrix, threshold = detect_blocks_by_mean_difference(
        get_context().board_template_path,
        current_path,
        roi_board_coords,
        False,
    )
    print(f"board: {board_matrix} with threshold: {threshold:.2f}")
    return board_matrix, threshold

def detect_blocks_by_mean_difference(template_path, current_path, roi_coords=None, show_plot=False):
    """
    Detect blocks by comparing mean difference across entire cell areas
    """
    # Load both images
    template_img = cv2.imread(template_path)
    current_img = cv2.imread(current_path)

    if template_img is None or current_img is None:
        print("Error: Could not load images")
        return None, None

    # Apply ROI if specified
    if roi_coords:
        x, y, w, h = roi_coords
        template_img = template_img[y:y + h, x:x + w]
        current_img = current_img[y:y + h, x:x + w]

    # Convert to grayscale
    template_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
    current_gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)

    grid_rows, grid_cols = (10, 10)

    grid_top_left = (0, 0)
    block_size = get_context().block_size_on_board

    # Calculate cell regions
    cell_regions = []
    for row in range(grid_rows):
        for col in range(grid_cols):
            # Define cell boundaries with margin to avoid grid lines
            margin = block_size // 10
            x1 = grid_top_left[0] + block_size/2 - margin + block_size *col + col*2
            y1 = grid_top_left[1] + block_size/2 - margin + block_size *row + row*2
            x2 = grid_top_left[0] + block_size/2 + margin + block_size *col + col*2
            y2 = grid_top_left[1] + block_size/2 + margin + block_size *row + row*2

            # Skip invalid regions
            if x1 >= x2 or y1 >= y2:
                continue

            cell_regions.append((row, col, x1, y1, x2, y2))

    # Create visualization images
    template_rgb = cv2.cvtColor(template_img, cv2.COLOR_BGR2RGB)
    current_rgb = cv2.cvtColor(current_img, cv2.COLOR_BGR2RGB)

    # current_vis = current_img.copy()
    # for row, col, x1, y1, x2, y2 in cell_regions:
    #     cv2.rectangle(current_vis,
    #                   (int(x1), int(y1)),
    #                   (int(x2), int(y2)),
    #                   (0, 255, 0), 2)

    # Detect blocks by mean difference
    block_matrix = [[0 for _ in range(grid_cols)] for _ in range(grid_rows)]
    block_count = 0

    # Store differences for threshold calibration
    differences = []

    for row, col, x1, y1, x2, y2 in cell_regions:
        # Extract cell regions from both images
        template_cell = template_gray[int(y1):int(y2), int(x1):int(x2)]
        current_cell = current_gray[int(y1):int(y2), int(x1):int(x2)]

        if template_cell.size == 0 or current_cell.size == 0:
            continue

        # Resize to same dimensions if needed
        if template_cell.shape != current_cell.shape:
            current_cell = cv2.resize(current_cell, (template_cell.shape[1], template_cell.shape[0]))

        # Calculate mean absolute difference (MAD)
        diff = cv2.absdiff(template_cell, current_cell)
        mean_diff = np.mean(diff)
        differences.append(mean_diff)

        # Draw the difference value on visualization
        # diff_text = f"{mean_diff:.1f}"
        # cv2.putText(current_vis, diff_text,
        #             (int((x1 + x2) / 2) - 10, int((y1 + y2) / 2)),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 0, 255), 1)
    # cv2.imshow("current_vis", current_vis)
    # cv2.waitKey(0)

    # Calculate dynamic threshold based on median difference
    if differences:
        median_diff = np.min(differences)
        threshold = median_diff + 10 # Adjust multiplier as needed
        print(f"Calculated dynamic threshold: {threshold:.2f} (median diff: {median_diff:.2f})")
    else:
        threshold = 10  # Fallback value
        print(f"Using fallback threshold: {threshold}")

    # Second pass to detect blocks using the threshold
    for i, (row, col, x1, y1, x2, y2) in enumerate(cell_regions):
        mean_diff = differences[i]

        # If difference is significant, mark as block
        if mean_diff > threshold:
            block_count += 1
            block_matrix[row][col] = 1
            # Highlight block in visualization
            # cv2.rectangle(current_vis,
            #               (int(x1), int(y1)),
            #               (int(x2), int(y2)),
            #               (0, 255, 0), 2)
            #
            # # Draw block indicator
            # cv2.putText(current_vis, "B",
            #             (int((x1 + x2) / 2) - 5, int((y1 + y2) / 2) + 5),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    if show_plot:
        # Create visualization
        plt.figure(figsize=(20, 15))
        
        # Template image
        plt.subplot(2, 2, 1)
        plt.imshow(template_rgb)
        plt.title('Empty Board Template')
        plt.axis('off')
        
        # Current image
        plt.subplot(2, 2, 2)
        plt.imshow(current_rgb)
        plt.title('Current Board')
        plt.axis('off')
        
        # Current with detected blocks
        plt.subplot(2, 2, 3)
        #plt.imshow(cv2.cvtColor(current_vis, cv2.COLOR_BGR2RGB))
        plt.title(f'Detected Blocks: {block_count} blocks\nThreshold: {threshold:.2f}')
        plt.axis('off')
        
        # Block matrix visualization
        plt.subplot(2, 2, 4)
        plot_block_matrix(block_matrix, block_size)
        plt.title('Block Matrix')
        plt.axis('off')

        plt.tight_layout()
        plt.show()
        
        print(f"Detected {block_count} blocks on the board")
    return block_matrix, threshold

def plot_block_matrix(block_matrix, block_size=50):
    """Create a visualization of the block matrix"""
    rows = len(block_matrix)
    cols = len(block_matrix[0]) if rows > 0 else 0

    if rows == 0 or cols == 0:
        return

    # Create blank image
    img = np.ones((rows * block_size, cols * block_size, 3), dtype=np.uint8) * 255
    print(block_matrix)
    for row in range(rows):
        for col in range(cols):
            if block_matrix[row][col]:
                color = (100, 200, 100)  # Green for blocks
            else:
                color = (230, 230, 230)  # Light gray for empty

            top_left = (col * block_size, row * block_size)
            bottom_right = ((col + 1) * block_size, (row + 1) * block_size)
            cv2.rectangle(img, top_left, bottom_right, color, -1)

            # Draw grid lines
            cv2.rectangle(img, top_left, bottom_right, (150, 150, 150), 1)

            # Add text for blocks
            if block_matrix[row][col]:
                cv2.putText(img, "B",
                            (col * block_size + block_size // 2 - 5, row * block_size + block_size // 2 + 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    plt.imshow(img)
    plt.title('Block Matrix (B = Block)')


# Example usage
if __name__ == "__main__":
    # Paths to your images
    template_path = "templates/screen_template.jpeg"  # Empty board image
    current_path = "test_data/test_2.PNG"  # Current board with blocks

    # ROI coordinates (if needed)
    roi_coords = (78, 664, 1015, 1015)  # Example coordinates

    # Detect blocks with mean difference comparison
    block_matrix, threshold = detect_blocks_by_mean_difference(
        template_path,
        current_path,
        roi_coords,
        True
    )
    # Print block positions
    if block_matrix:
        print("\nBlock positions:")
        print(block_matrix)
        for row in range(len(block_matrix)):
            for col in range(len(block_matrix[0])):
                if block_matrix[row][col]:
                    print(f" - Cell ({row}, {col})")
