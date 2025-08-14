#!/bin/bash

install_homebrew() {
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "Homebrew is already installed."
    fi
}

install_xcode() {
    if ! xcode-select -p &> /dev/null; then
        echo "Installing Xcode Command Line Tools..."
        xcode-select --install
        echo "Follow the on-screen instructions to finish installation."
    else
        echo "Xcode Command Line Tools are already installed."
    fi
}

install_appium() {
    # Check if Appium is installed
    if ! command -v appium >/dev/null 2>&1; then
        echo "⚠️  Appium is not installed. Installing globally via npm..."
        npm install -g appium
    else
        echo "✅ Appium is installed."
    fi

    # Check if XCUITest driver is installed
    if appium driver list --installed --json | grep -q "xcuitest"; then
        echo "✅ XCUITest driver is already installed."
    else
        echo "⚠️  XCUITest driver not found. Installing..."
        appium driver install xcuitest
    fi
}

# Combined check and brew install function
check_and_install() {
    local cmd="$1"
    local pkg="$2"  # Homebrew package name, if different from cmd

    if command -v "$cmd" &> /dev/null; then
        echo "$cmd is already installed."
    else
        echo "$cmd not found."
        if [ -z "$pkg" ]; then
            pkg="$cmd"
        fi

        # Check if brew knows about this package
        if brew info "$pkg" &> /dev/null; then
            echo "Installing $pkg via Homebrew..."
            brew install "$pkg"
        else
            echo "No Homebrew package found for $pkg. Please install it manually."
        fi
    fi
}

# ---- Run steps ----
install_homebrew
install_xcode

check_and_install git
check_and_install node

install_appium
