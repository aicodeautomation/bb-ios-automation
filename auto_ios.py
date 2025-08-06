from selenium.webdriver.common.action_chains import ActionChains
from appium import webdriver
from appium.options.ios import XCUITestOptions
import time
from context import set_context, get_context
from board_detection import *
from block_detection import *
from placement import *
import traceback

def get_offset_from_counter(counter):
    x_range = list(range(-50, 50, 10))  # e.g., [-50, -45, ..., 45]
    y_range = list(range(50, -50, -10))  # e.g., [25, 30, ..., 115]

    if counter == 0:
        return 0, 0  # First attempt: no offset
    counter -= 1  # Adjust for 0,0 being used already

    if counter >= len(x_range) * len(y_range):
        return None, None  # All combinations exhausted

    y_idx = counter // len(x_range)  # y loop outside
    x_idx = counter % len(x_range)   # x loop inside

    x_offset = x_range[x_idx]
    y_offset = y_range[y_idx]

    return x_offset, y_offset

def compute_target_pixel(shape, board_origin, cell_size, place_row, place_col):
    shape_row, shape_col = len(shape), len(shape[0])

    shape_final_width = (shape_col * cell_size + (shape_col - 1) * 15) / 2 + (5 - shape_col) * 5
    shape_final_height = (shape_row + 1) * cell_size + shape_row * 15 + (5 - shape_row) * 5 if shape_row < 4 else (shape_row + 0.5) * cell_size + shape_row * 15

    board_target_x = board_origin[0] + place_col * cell_size + place_col
    board_target_y = board_origin[1] + place_row * cell_size + place_row

    pixel_x = board_target_x + shape_final_width
    pixel_y = board_target_y + shape_final_height
    return pixel_x, pixel_y

def setup_board_shape(retry=0, max_retries=500, delay=0.5):
    try:
        time.sleep(delay * (retry // 5))
        print(f"[setup_board_shape] Attempt #{retry+1}")
        driver.save_screenshot(get_context().current_screen_template_path)
        board, threshold = get_current_board(get_context().current_screen_template_path)
        shapes = get_block_shapes(get_context().current_screen_template_path)
        return board, shapes
    except Exception as e:
        print(f"[setup_board_shape] Failed attempt #{retry+1}: {e}")
        traceback.print_exc()
        if retry >= max_retries:
            print(f"[setup_board_shape] Giving up after {max_retries} retries.")
            return None
        return setup_board_shape(retry + 1, max_retries, delay)

def click_on_pos(coord):
    x, y = coord
    iphone_scale = get_context().scale
    actions = ActionChains(driver)
    actions.w3c_actions.pointer_action.move_to_location(x / iphone_scale, y / iphone_scale)  # Move to start
    actions.w3c_actions.pointer_action.pointer_down()  # Press down
    actions.w3c_actions.pointer_action.pointer_up()  # Release
    actions.perform()

def move_to_pos(from_coord, to_coord):
    from_x, from_y = from_coord
    to_x, to_y = to_coord
    iphone_scale = get_context().scale
    actions = ActionChains(driver)
    actions.w3c_actions.pointer_action.move_to_location(from_x / iphone_scale, from_y / iphone_scale)  # Move to start
    actions.w3c_actions.pointer_action.pointer_down()  # Press down
    #actions.w3c_actions.pointer_action.pause(0.2)  # Small pause for realistic press
    actions.w3c_actions.pointer_action.move_to_location(to_x / iphone_scale, to_y / iphone_scale)  # Move while pressed
    actions.w3c_actions.pointer_action.pause(0.5)
    actions.w3c_actions.pointer_action.pointer_up()  # Release
    actions.perform()

def is_board_updated_np(original, updated):
    return not np.array_equal(np.array(original), np.array(updated))

def get_tap_pos(shape_index):
    tap_pos = get_context().start_blocks
    if shape_index < 6:
        return tap_pos[0]
    elif shape_index < 12:
        return tap_pos[1]
    else:
        return tap_pos[2]

def auto_play(driver):
    last_board = None
    count = 0
    cfg = get_context()
    while True:
        app_info = driver.execute_script("mobile: activeAppInfo")
        if app_info["bundleId"] != 'com.puzzle.sea.block1010':
            print("⚠️ Not in the game, switching back...")
            driver.activate_app("com.puzzle.sea.block1010")

        print("----- LOOP START -----")

        # close adds
        click_on_pos(cfg.pop_up_high_close)
        click_on_pos(cfg.pop_up_low_close)

        # click next/no thanks
        click_on_pos(cfg.start_game_button)
        click_on_pos(cfg.more_score_wheel_no_thanks_button)
        click_on_pos(cfg.diamond_no_thanks_button)
        click_on_pos(cfg.diamond_next_button)
        click_on_pos(cfg.no_thanks_daily)
        click_on_pos(cfg.level_up_next_button)

        board, shapes = setup_board_shape()

        if len(shapes) > 4:
            continue

        offset_x = 0
        offset_y = 0
        if not is_board_updated_np(last_board, board):
            offset_x, offset_y = get_offset_from_counter(count)
            count += 1
        else:
            count = 0
        last_board = board

        while shapes:
            board, shape_idx, shape_loc, pos = smart_place_best_shape(board, shapes)
            if shape_idx is None or offset_x is None or offset_y is None:
                break  # stop when no shapes can be placed
            from_x, from_y = get_tap_pos(shape_loc)
            print(f"up_b: {board}, pos: {pos}")

            to_x, to_y = compute_target_pixel(shapes[shape_idx][0], get_context().board_top_left, get_context().block_size_on_board, pos[0], pos[1])
            print(f"to_x: {to_x} with offset {offset_x}, to_y: {to_y} with offset {offset_y}")

            move_to_pos((from_x, from_y), (to_x + offset_x, to_y + offset_y))
            print(f"moved to ({to_x + offset_x}, {to_y + offset_y}).")
            del shapes[shape_idx]  # remove the used shape


            # test_data = cv2.imread("test_1.png")
            # dot_color = (0, 0, 255)  # BGR (Red)
            # dot_radius = 15
            # cv2.circle(test_data, (from_x, from_y), dot_radius, dot_color, -1)
            # cv2.circle(test_data, (int(to_x), int(to_y)), dot_radius, dot_color, -1)
            # # Show the image with the dot
            # cv2.imshow("Image with Dot", test_data)
            #
            # # Wait for any key press to continue
            # cv2.waitKey(0)


if __name__ == "__main__":
    set_context(13)
    cfg = get_context()

    desired_capabilities = {
        "platformName": "iOS",
        "appium:deviceName": cfg.device_name,
        "appium:platformVersion": cfg.ios_version,
        "appium:bundleId": "com.puzzle.sea.block1010",
        "appium:automationName": "XCUITest",
        "appium:udid": cfg.device_id,
        "appium:includeSafariInWebviews": True,
        "appium:newCommandTimeout": 3600,
        "appium:connectHardwareKeyboard": True,
        "appium:noReset": True
    }
    appium_server_url = "http://localhost:4723"  # Default Appium server address


    driver = None  # Initialize driver to None
    try:
        print(f"Connecting to Appium server at {appium_server_url}...")
        options = XCUITestOptions().load_capabilities(desired_capabilities)
        driver = webdriver.Remote(appium_server_url, options=options)
        print("Appium driver initialized successfully. App launched on phone.")
        auto_play(driver)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
    finally:
        # --- 4. Close the session ---
        if driver:
            print("Quitting Appium driver session.")
            driver.quit()
        print("Script execution completed.")
