# 🧩 Block Blast Game Automation

This project automates gameplay for the mobile puzzle game **Block Blast** using computer vision and iOS UI automation tools.

- 🎯 Uses **OpenCV** to detect the board and block shapes
- 🤖 Automates taps/moves via **Appium + XCUITest** on iOS

---

## 💖 Sponsor This Project

If you find this project helpful and want to support,

👉 [**Buy Me a Coffee**](https://buymeacoffee.com/rowanli199q)  
or  
👉 [**GitHub Sponsors**](https://github.com/sponsors/aicodeautomation)

Your support helps me keep building and improving open-source tools like this!

--

## ⚠️ Limitations

1. **Device Support: iPhone 13 Only**  
   The script uses `cv2.matchTemplate`, which is pixel-accurate.  
   Any difference in screen resolution or layout (other devices, zoomed mode, etc.) will cause detection issues.

2. **Android Not Supported**  
   Android devices have not been tested or configured.

---

## 🔧 Setup for Other Devices

To adapt this script to another iOS device:

### ✅ Checklist

- [ ] **Take a full game screenshot**  
  - Use it to extract screen coordinates.
  - Update or add new entries in `config.py` with your measurements.

- [ ] **Capture an empty board screenshot**  
  - Replace `templates/screen_template.jpeg` with this image.

- [ ] **Crop and replace a block image**  
  - Crop a single block from your screenshot.
  - Replace the file `block_3.png` with this block.
