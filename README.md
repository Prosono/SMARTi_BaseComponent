SMARTi Integration for Home Assistant

SMARTi is a powerful Home Assistant integration designed to enhance your smart home experience. It simplifies energy management, device control, and automation setup while providing seamless updates through HACS.
Features

    Energy Management: Dynamically monitor and control energy usage with categorized devices.
    Smart Device Control: Automatically manage device states based on power consumption thresholds.
    Seamless Updates: Now fully compatible with HACS for effortless installation and updates.
    Localization: Supports multiple languages, including Norwegian and English.
    Pre-configured Settings: Easy setup with minimal user input required.

Installation
Via HACS

    Ensure you have HACS installed in your Home Assistant instance.
    Add this repository as a custom repository:
        Open HACS in Home Assistant.
        Go to Settings > Custom Repositories.
        Add the repository URL: https://github.com/yourusername/smarti.
        Set the category to Integration and click Add.
    Search for SMARTi in HACS and click Install.
    Restart Home Assistant.

Manual Installation

    Clone this repository or download it as a ZIP file.
    Extract the contents and copy the custom_components/smarti directory to your Home Assistant config/custom_components/ directory.
    Restart Home Assistant.

Setup

    Go to Settings > Devices & Services > Add Integration in Home Assistant.
    Search for SMARTi and select it.
    SMARTi will be automatically configured—no additional input required.

Energy Management Features

SMARTi allows you to categorize devices into three groups for power management:

    Category 1: Devices that never turn off.
    Category 2: Devices that can turn off when needed.
    Category 3: Devices that turn off first to reduce energy consumption.

Easily monitor and control these devices from the SMARTi dashboard.
Translations

SMARTi supports multiple languages:

    English (default)
    Norwegian (Norsk)

More languages can be added upon request.
Contributing

We welcome contributions! If you'd like to add features or report bugs:

    Fork this repository.
    Create a new branch.
    Submit a pull request with your changes.

License

This project is licensed under the MIT License. See the LICENSE file for details.
Support

If you encounter any issues, please open an issue in the GitHub repository.

Let me know if you want to customize specific sections or add additional details!
