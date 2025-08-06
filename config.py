
# config.py

class Iphone13:
    width = 1170
    height = 2532
    scale = 3
    device_name = "< your device name >"
    ios_version = "< your ios version >"
    device_id = '< your device id >'

    # pop up ads
    pop_up_high_close = (1086, 1247)
    pop_up_low_close = (1086, 1539)

    # click next/no thanks
    no_thanks_daily = (588, 1950)
    start_game_button = (588, 1380)
    more_score_wheel_no_thanks_button = (588, 1987)
    diamond_no_thanks_button = (588, 2184)
    diamond_next_button = (865, 2016)
    level_up_next_button = (865, 1770)

    # board top left
    board_top_left = (78, 664)
    # block size
    block_size_on_board = 100

    # candidate blocks
    start_blocks = [(250, 1900), (585, 1900), (915, 1900)]

    #roi
    board_roi = (78, 664, 1015, 1015)
    block_roi = (74, 1754, 1020, 288)

    block_template_path = "templates/block_3.png"
    board_template_path = "templates/screen_template.jpeg"
    current_screen_template_path = "templates/current_screen.png"



class Config2:
    tap_pos = [(180, 1070), (375, 1070), (555, 1070)]

# Master dictionary to select config based on target
CONFIGS = {
    13 : Iphone13,
    2: Config2
}



