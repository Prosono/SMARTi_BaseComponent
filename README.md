# Presenting the SMARTi Integration for Home Asssitant - How Home Asssitant dashboards should be done!

- Do you find it challenging to create a comprehensive dashboard that meets the needs of everyone in your household?  
- Are you frustrated with having to update your dashboard every time you add a new device to Home Assistant?  
- Do you wish your dashboard could feature a sleek, professional, and clean design?  
- Are you looking for a single dashboard solution that works seamlessly across all your devices—phones, tablets, and desktops? 
- Are you tired of having to update all your custom cards from HACS manually?

If the answer is yes to any one of the questions above, SMARTi is the integration for you!

SMARTi delivers a complete, hassle-free maintenance experience with a seamless and intuitive dashboard for Home Assistant. By harnessing the full potential of Home Assistant, SMARTi automatically gathers all your devices into a single, auto-populated dashboard—designed for multiple devices and available in multiple languages.

##That’s right! With SMARTi, you only need one dashboard to meet the needs of your entire household, across all devices.

From stunning animations to advanced power monitoring and control, SMARTi is designed to simplify Home Assistant, offering a more user-friendly experience for everyone in your home.


SMARTi Comes in a FREE (SMARTi Basic) verison and a PAID version (SMARTi PRO) which has a monthly subscription cost

The table below highlights the differences:
# SMARTi Feature Comparison

| Category                  | SMARTi Basic - Free                                                                                          | SMARTi Pro - 2.99 EUR/month                                                                                  |
|---------------------------|-------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| **Dashboard**             | **Auto-Populated**                                                                                         | **Auto-Populated**                                                                                           |
|                           | _Description:_ Automatically generates dashboards with basic information.                                  | _Description:_ Provides fully automated, dynamic dashboards for a seamless experience.                       |
| **Dashboard Device Support** | **Desktops, Tablets**                                                                                     | **Desktops, Tablets, Phones**                                                                                |
|                           | _Description:_ Optimized for use on desktop computers and tablets.                                         | _Description:_ Fully compatible with desktops, tablets, and mobile phones.                                   |
| **Automations**           | **None**                                                                                                   | **Water Leak Alert, Fire Alert, Smoke Alert, Gas Alert**                                                     |
|                           | _Description:_ No automation options are included in the free version.                                     | _Description:_ Includes pre-configured automations for common safety alerts.                                 |
| **Customizations**        | **None**                                                                                                   | **Full Customization**                                                                                       |
|                           | _Description:_ No customization options for dashboard layout or content.                                   | _Description:_ Allows complete control over dashboard layout and content.                                    |
| **Language**              | **English**                                                                                                | **English, French, German, Spanish, Norwegian, Dutch**                                                      |
|                           | _Description:_ Only English is available in the free version.                                              | _Description:_ Offers support for multiple languages for a global audience.                                  |
| **Power Control**         | **None**                                                                                                   | **PowerFlow**                                                                                                |
|                           | _Description:_ No tools for monitoring or managing energy usage.                                           | _Description:_ Includes advanced tools for energy monitoring and management.                                 |
| **Themes**                | **Single Theme**                                                                                           | **Multiple Themes**                                                                                          |
|                           | _Description:_ Only one default theme is available.                                                       | _Description:_ Offers five distinct themes for visual customization.                                         |
| **Feature Updates**       | **Yearly**                                                                                                 | **Monthly**                                                                                                  |
|                           | _Description:_ Features are updated only once per year.                                                   | _Description:_ Features are updated every month with new capabilities.                                       |
| **Updates**               | **Quarterly**                                                                                              | **Continuous**                                                                                               |
|                           | _Description:_ Bugs are addressed every three months in the free version.                                  | _Description:_ Bugs are fixed on an ongoing basis for faster resolutions.                                    |


Q: Why is there a monthly subscription cost for the PRO verison?
A: In order to fully dedicate to an enviroment that is constantly changing and to provide usefull updates to the usabviliusability ty of the SMARTi dashboard and its automations, a monthly cost is needed to run the developemnt.


## Installation
SMARTi can be installed in two seperate ways (for both the Basic and Pro Verison)

### Manual

If selecting manual mode when settign up the integration, SMARTi will NOT download any of the required cards from HACS. This will have to be done manually by the end user. T

### Automatic

If selecting automatic mode when setting up the integraiton, SMARTi will enable .yaml mode for you HOme Assistant installation and download all the cards required by the SMARTi dashboard. The also means that your Home Assistant isntalltion will now be in .yaml mode meaning that if you are to download more cards form HACS (or have other cards form HACS installed that is not included in the SMARTi integration), you will have to add theese manually to your configuration.yaml file after installing form HACS. 

#### Example:
Lets say that you want to download another custom card not included with the SMARTi integration - e.g the "lovelace-dual-gauge-card" you will then have to add the following line to your configuration.yaml:

<pre> ```yaml - url: /community_plugin/dual-gauge-card/dual-gauge-card.js type: js ``` </pre>

Energy Management: Dynamically monitor energy usage with categorized devices.
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



Setup

Go to Settings > Devices & Services > Add Integration in Home Assistant.
Search for SMARTi and select it.
SMARTi will be automatically configured—no additional input required.

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
