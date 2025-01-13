<div align="center">

# Presenting the SMARTi Integration for Home Assistant  
## How Home Assistant dashboards should be!

</div>

<div align="center">
  <img src="assets/smartiDashboardPromo.png" width="900">
</div>

<br>



- Do you find it challenging to create a comprehensive dashboard that **meets the needs** of everyone in your household?  
<br>

- Are you **frustrated** with having to update your dashboard every time you add or remove a device to Home Assistant?  
<br>

- Do you wish your dashboard could feature a **sleek, professional, and clean design**?  
<br>

- Are you looking for a **single dashboard solution** that works seamlessly across all your devices—phones, tablets, and desktops? 
<br>

- Do you want a higher wife-aproval rating for your Home Assistant setup?
<br>


If the answer is **YES** to any one of the questions above, then **SMARTi** is the integration for you!

<br>
<br>


SMARTi delivers a complete, hassle-free maintenance experience with a seamless and intuitive dashboard for Home Assistant. By harnessing the full potential of Home Assistant, SMARTi automatically gathers all your devices into a single, auto-populated dashboard—designed for multiple devices and available in multiple languages.



### With SMARTi, you only need **one** dashboard to meet the needs of your entire household, across **all devices**.

From beautiful animations to advanced power monitoring and control, SMARTi is designed to simplify Home Assistant, offering a more user-friendly experience for everyone in your home.

<div align="center">

  <!-- Homepage Section -->
  <div style="display: flex; justify-content: center; gap: 10px; margin-bottom: 20px;">
    <img src="assets/homepagegif.gif" style="max-width: 1000px; height: auto;">
    <img src="assets/homepagetablet2.gif" style="max-width: 1000px; height: auto;">
  </div>
  <br<>>
  <!-- Themes Section -->
  <div>
    <img src="assets/colors5.png" style="max-width: 1000px; height: auto; margin-top: 20px;">
    <p style="text-align: center; max-width: 600px; margin: 0 auto;">Do you want to change the look and feel to make the dashboard more personalized? SMARTi includes 5 pre-installed themes to choose from.</p>
  </div>

</div>


# Versions

SMARTi Comes in a **FREE** (SMARTi Basic) verison and a **PAID** version (SMARTi PRO) which has a monthly subscription cost.

SMARTi Basic does not require a subscription to be downloaded and installed, but the Pro version does. A subrsctiption can be purchased at https://smarti.dev

The table below highlights the feature of the SMARTi dashboard and the differences between the Basic and Pro version:
# SMARTi Feature Basic vs Pro Comparison

| Category                  | SMARTi Basic - Free                                                                                          | SMARTi Pro - 2.99 EUR/month                                                                                  |
|---------------------------|-------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| **Dashboard**             | **Auto-Populated**                                                                                         | **Auto-Populated**                                                                                           |
|                           | _Description:_ Provides fully automated, dynamic dashboards for a seamless experience.                     | _Description:_ Provides fully automated, dynamic dashboards for a seamless experience.                       |
| **Dashboard Device Support** | **Desktops, Tablets**                                                                                     | **Desktops, Tablets, Phones**                                                                                |
|                           | _Description:_ Optimized for use on desktop computers and tablets.                                         | _Description:_ Fully compatible with desktops, tablets, and mobile phones.                                   |
| **Automations**           | **None**                                                                                                   | **Water Leak Alert, Fire Alert, Smoke Alert, Gas Alert, Main Fuse Overload Alert**                           |
|                           | _Description:_ No automation options are included in the free version.                                     | _Description:_ Includes pre-configured automations for common safety alerts (can be disabled).               |
| **Customizations**        | **None**                                                                                                   | **Customization**                                                                                             |
|                           | _Description:_ No customization options for dashboard layout or content.                                   | _Description:_ Allows some control over dashboard layout and content.                                        |
| **Language**              | **English**                                                                                                | **English, French, German, Spanish, Norwegian, Dutch**                                                      |
|                           | _Description:_ Only English is available in the free version.                                              | _Description:_ Offers support for multiple languages for a global audience.                                  |
| **Power Control**         | **None**                                                                                                   | **PowerFlow - Coming Soon**                                                                                  |
|                           | _Description:_ Basic tools for monitoring energy usage.                                                    | _Description:_ Coming soon - Advanced tools for energy monitoring and management.                            |
| **Themes**                | **Single Theme**                                                                                           | **Multiple Themes**                                                                                          |
|                           | _Description:_ Only one default theme is available.                                                       | _Description:_ Offers five custom-made distinct themes for visual customization.                             |
| **Kiosk Mode**            | **Not Supported**                                                                                          | **Enabled**                                                                                                  |
|                           | _Description:_ Kiosk Mode is not available in the free version.                                            | _Description:_ Provides advanced Kiosk Mode, including dynamic header/sidebar visibility and media queries.  |
| **Token Lifetime**        | **30 Days**                                                                                                | **Continuous (Active Subscription + Remaining Days)**                                                        |
|                           | _Description:_ Tokens are valid for 30 days; users must generate a new token manually after expiration.     | _Description:_ Tokens remain valid as long as the subscription is active, with additional remaining days.    |
| **Feature Updates**       | **Yearly**                                                                                                 | **Monthly**                                                                                                  |
|                           | _Description:_ Features are updated only once per year.                                                   | _Description:_ Features are updated every month with new capabilities.                                       |
| **Updates**               | **Quarterly**                                                                                              | **Continuous**                                                                                               |
|                           | _Description:_ Non-breaking bugs are addressed roughly every three months in the free version.             | _Description:_ Bugs are fixed on an ongoing basis for faster resolutions.                                    |


Q: Why is there a monthly subscription cost for the Pro verison?
<br>

A: In order to fully dedicate to an enviroment that is constantly changing and to provide usefull updates to the SMARTi dashboard and its automations, a monthly cost is needed to properly develop, run, test and deploy the solution.


# Installation

Installation

Pre-requisties:

* ## This integration only supports Home Assistant 2024.8 and above. Installing and configuring this integration on a Home Assistant installation with a lower version than this will result in errors and the integration will not work properly.

Before starting you installation, make sure you have the two following lines in you configuration.yaml file:
<pre>
homeassistant:
    packages: !include_dir_named packages 
</pre>

Via HACS

Ensure you have HACS installed in your Home Assistant instance.
Add this repository as a custom repository:
   - Open HACS in Home Assistant.
   - Go to Settings > Custom Repositories.
   - Add the repository URL: https://github.com/Prosono/SMARTi_BaseComponent
   - Set the category to Integration and click Add.
   - Search for SMARTi in HACS and click Install.
   - Restart Home Assistant.
   - Go to Settings > Devices & Services > Add Integration in Home Assistant.
Search for SMARTi and select it.
   - You now have to select the SMARTi Basic or the SMARTi Pro option.
   - After that you now have the following two choices:


A SMARTi Basic token is generated and sent to you by email upon initial configuration when selecting "I do not have a token". This token will expire after 30 days, which then requires you to generate a new one by setting up the integration again.

A SMARTi Pro token must be purchased from our website at https://www.smarti.dev/smarti-store/p/smarti-powerflow-xe7ft and after a sucessfull payment, will be sent to you by email. 

After you have selected your SMARTi version and you have sucessfully entered your token and email, you will have the two following installation options:

- ### Manual

If you select manual mode during the setup of the SMARTi integration, none of the required cards will be automatically downloaded from HACS. Instead, it will be the responsibility of the end user to install these cards manually, either by directly downloading them or by using HACS.

A complete list of the cards required for the SMARTi integration can be found in the "Required Cards" section at the end of this README. Please ensure that all listed cards are properly installed to fully utilize the SMARTi dashboard and its features.

- ### Automatic

If you select automatic mode during the setup of the SMARTi integration, it will automatically enable YAML mode for your Home Assistant installation and download all the cards required for the SMARTi dashboard.

Please note that enabling YAML mode changes the way resources are managed in your Home Assistant setup. By default, Home Assistant operates in storage mode, but with YAML mode enabled, any additional cards you download from HACS (or existing cards not included with the SMARTi integration) must be manually added to your configuration.yaml file after installation.

For a list of cards included with the SMARTi integration, refer to the "Included Cards" section at the bottom of the README. Be sure to follow this process for any extra cards you wish to use to ensure proper functionality.

#### Example:
If you want to download and use another custom card not included with the SMARTi integration, such as the "lovelace-dual-gauge-card", you will need to manually add the following line to your configuration.yaml file:

<pre>
lovelace:
mode: yaml
resources: 
    url: /community_plugin/dual-gauge-card/dual-gauge-card.js 
    type: js  
</pre>

This also means that the SMARTi integration takes full responsibility for managing the provided cards, including updating, adding, and removing them as needed.

For the best experience, we recommend using the automatic installation during the initial setup of the SMARTi integration to ensure everything is installed and configured correctly. If you encounter conflicts with pre-existing dashboards that use cards not provided by the SMARTi integration, you can uninstall and re-install the integration in manual mode to maintain compatibility with your custom setup.

## When uninstalling the integration ALL settings, files, dashboards, automations etc related to the SMARTi integration is deleted and your installation will return to its original state. 

# Usage

## Have SMARTi **NOT** show devices/entities
If you prefer SMARTi to exclude certain entities from appearing on its dashboards, simply hide those entities in your Home Assistant settings. Once hidden, SMARTi will automatically exclude them from display, ensuring a more tailored and clutter-free experience. Make sure to refresh the page once an entity has been hidden in roder to see the reflected changes. 

## Set up power measurement sensor
Since SMARTi uses a more general power sensor, this will have to be set. This can be set under the settings page under "Dynamic Power Sensor". IKf no sensors are present here, just click the button "Update power Sensor Lsit" ANd it will populate with all sensors haveing a power measurement and you can select the proper one. 

# Dependencies:

The SMARTi integration does not require any additional integrations to function. However, to unlock its full potential and access advanced features, it is recommended to install the following integrations:

- ## Browser Mod
<br>
The Browser Mod integration enhances the functionality of SMARTi by enabling certain popups to operate as designed. Additionally, it plays a key role in monitoring and displaying active devices directly within the SMARTi navigation bar, providing a seamless and interactive user experience. While not mandatory, this integration is highly recommended for full feature compatibility.

- ## Alarmo
<br>
The Alarmo integration enables users to set up a customizable and feature-rich alarm system within Home Assistant. Fully integrated into the SMARTi ecosystem, Alarmo is a required component for the proper functionality of SMARTi’s alarm panels and alert systems. This seamless integration ensures that your security features are optimized and operate as intended, providing a reliable and user-friendly alarm solution.

- ## Ping (ICMP)
<br>
By adding a ping sensor named "smarti_internet" in the Home Assistant UI, you can monitor your internet connection with detailed statistics. Additionally, this sensor provides a convenient status icon in the navigation bar, allowing you to quickly view the state of your connection at a glance.


## Required Cards (cards that must be installed manually if selecting the manual mode):

- Alarmo Card
- ApexCharts Card
- Bar Card
- Bubble Card
- Button Card
- Button Text Card
- Clock Weather Card
- Comfortable Environment Card
- Config Template Card
- HA Sankey Chart
- Logbook Card
- Lottie Card
- Auto Entities
- Card Mod
- Card Templater
- Card Tools
- Kiosk Mode
- Home Feed Card
- Hourly Weather Card
- Hui Element
- Layout Card
- Mushroom Card
- Mini Graph Card
- Numberbox Card
- Slider Button Card
- Stack-in-Card
- Tabbed Card
- Time Bar Card
- Uptime Card
- Vertical Stack-in-Card
- Weather Chart Card
- Better Moment Card
- Maxi Media Player
- Swipe Card

# Disclaimer

This integration enhances your Home Assistant setup by adding multiple automations, sensors, entities, and helpers. All components are prefixed with "SMARTi_xxx" to ensure easy filtering and to prevent conflicts with any existing items in your installation. Rest assured, the integration is designed to seamlessly coexist with your current setup. However, if this naming convention is a concern for you, the SMARTi integration may not be the right fit.

# License

This repository is licensed under the MIT license, granting you the freedom to fork, copy, modify, and redistribute its contents as you see fit. However, please note that the configuration files downloaded to your Home Assistant installation are not covered under the same license. Upon installation, the applicable licenses for these configuration files are placed in the "smartilicenses" folder for your reference.

# Support, bugs and reporting


If you encounter any non-breaking bugs, please open an issue in the GitHub repository.
For any immediate issues, bugs, issues, or feedback, please contact our support team at support@smarti.dev. We value your input and strive to continuously improve our products and services.