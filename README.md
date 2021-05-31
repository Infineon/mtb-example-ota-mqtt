# AnyCloud: Over-the-air firmware update using MQTT

This code example demonstrates an OTA update with PSoC&trade; 6 MCU and CYW43xxx connectivity devices. The device establishes a connection with the designated MQTT Broker (this example uses a local Mosquitto broker). It periodically checks the job document to see if a new update is available. When a new update is available, it is downloaded and written to the secondary slot. On the next reboot, MCUboot swaps the new image in the secondary slot with the primary slot image and runs the application. If the new image is not validated in runtime, on the next reboot MCUboot reverts  to the previously validated image.

MCUboot is a secure bootloader for 32-bit MCUs. See the [README](https://github.com/cypresssemiconductorco/mtb-example-psoc6-mcuboot-basic/blob/master/README.md) of the [mtb-example-psoc6-mcuboot-basic](https://github.com/cypresssemiconductorco/mtb-example-psoc6-mcuboot-basic) code example for more details.

The OTA feature is enabled by the *Over-the-Air update middleware library*. See the [anycloud-ota](https://github.com/cypresssemiconductorco/anycloud-ota) middleware repository on Github for more details.

[Provide feedback on this code example.](https://cypress.co1.qualtrics.com/jfe/form/SV_1NTns53sK2yiljn?Q_EED=eyJVbmlxdWUgRG9jIElkIjoiQ0UyMzAwMzEiLCJTcGVjIE51bWJlciI6IjAwMi0zMDAzMSIsIkRvYyBUaXRsZSI6IkFueUNsb3VkOiBPdmVyLXRoZS1haXIgZmlybXdhcmUgdXBkYXRlIHVzaW5nIE1RVFQiLCJyaWQiOiJ5ZWt0IiwiRG9jIHZlcnNpb24iOiIzLjAuMCIsIkRvYyBMYW5ndWFnZSI6IkVuZ2xpc2giLCJEb2MgRGl2aXNpb24iOiJNQ0QiLCJEb2MgQlUiOiJJQ1ciLCJEb2MgRmFtaWx5IjoiUFNPQyJ9)

## Requirements

- [ModusToolbox&trade; software](https://www.cypress.com/products/modustoolbox-software-environment) v2.3
- Board Support Package (BSP) minimum required version: 2.0.0
- Programming Language: C
- Associated Parts: All [PSoC&trade; 6 MCU](http://www.cypress.com/PSoC6) parts with SDIO interface

## Supported toolchains (make variable 'TOOLCHAIN')

- GNU Arm® Embedded Compiler v9.3.1 (`GCC_ARM`) - Default value of `TOOLCHAIN`
- Arm compiler v6.13 (`ARM`)
- IAR C/C++ compiler v8.42.2 (`IAR`)

## Supported kits (make variable 'TARGET')

This example requires PSoC&trade; 6 MCU devices with at least 2-MB flash and 1-MB SRAM, and therefore supports only the following kits:

- [PSoC&trade; 6 Wi-Fi BT Prototyping Kit](https://www.cypress.com/CY8CPROTO-062-4343W) (`CY8CPROTO-062-4343W`) - Default value of `TARGET`
- [PSoC&trade; 62S2 Wi-Fi BT Pioneer Kit](https://www.cypress.com/CY8CKIT-062S2-43012) (`CY8CKIT-062S2-43012`)

## Hardware setup

This example uses the board's default configuration. See the kit user guide to ensure that the board is configured correctly.

## Software setup

Install a terminal emulator if you do not have one. Instructions in this document use [Tera Term](https://ttssh2.osdn.jp/index.html.en).

This examples uses mosquitto to setup a local MQTT broker, see section [Setting up the local MQTT mosquitto broker](#setting-up-the-local-mqtt-mosquitto-broker) for more details.

## Structure and overview

This code example is a dual-core project, where the MCUboot bootloader app runs on the CM0+ core and the OTA update app runs on the CM4 core. The OTA update app fetches the new image and places it in the flash memory; the bootloader takes care of updating the existing image with the new image. The [mtb-example-psoc6-mcuboot-basic](https://github.com/cypresssemiconductorco/mtb-example-psoc6-mcuboot-basic) code example is the bootloader project used for this purpose.

The bootloader project and this OTA update project should be built and programmed independently. They must be placed separately in the workspace as you would do for any other two independent projects. An example workspace would look something like this:

   ```
   <example-workspace>
      |
      |-<mtb-example-psoc6-mcuboot-basic>
      |-<mtb-example-anycloud-ota-mqtt>
      |
   ```

You must first build and program the MCUboot bootloader project into the CM0+ core; this needs to be done only once. The OTA update app can then be programmed into the CM4 core; you need to only modify this app for all application purposes.

## Building and programming MCUboot

The [mtb-example-psoc6-mcuboot-basic](https://github.com/cypresssemiconductorco/mtb-example-psoc6-mcuboot-basic) code example bundles two applications: the bootloader app that runs on CM0+, and the Blinky app that runs on CM4. For this code example, only the bootloader app is required and the root directory of the bootloader app is referred to as *\<bootloader_cm0p>* in this document.

1. Import the [mtb-example-psoc6-mcuboot-basic](https://github.com/cypresssemiconductorco/mtb-example-psoc6-mcuboot-basic) code example per the instructions in the [Using the Code Example](https://github.com/cypresssemiconductorco/mtb-example-psoc6-mcuboot-basic#using-the-code-example) section of its [README](https://github.com/cypresssemiconductorco/mtb-example-psoc6-mcuboot-basic/blob/master/README.md).

2. The bootloader and OTA applications must have the same understanding of the memory layout. Override the default memory layout by editing the make variables in the *\<bootloader_cm0p>/shared_config.mk* file. For this example, perform the following edits to match the memory layout with the OTA application:

   ```
   ifeq ($(USE_EXT_FLASH), 1)
   MCUBOOT_SLOT_SIZE=0x1C0000
   else
   MCUBOOT_SLOT_SIZE=0xF0000
   endif
   .
   .
   .
   MCUBOOT_SCRATCH_SIZE=0x4000
   ```

3. Copy the *\<mtb_shared>/mcuboot/\<tag>/boot/cypress/MCUBootApp/config* folder and paste it in the *\<bootloader_cm0p>* folder. 

4. Edit the *\<bootloader_cm0p>/config/mcuboot_config/mcuboot_config.h* file and comment out the following defines to skip checking the image signature:

   ```
   #define MCUBOOT_SIGN_EC256
   #define NUM_ECC_BYTES (256 / 8)
   .
   .
   .
   #define MCUBOOT_VALIDATE_PRIMARY_SLOT
   ```

5. Edit *\<bootloader_cm0p>/app.mk* and replace the MCUboot include `$(MCUBOOTAPP_PATH)/config` with `./config`. This gets the build system to find the new copy of the config directory that you pasted in the *\<bootloader_cm0p>* directory, instead of the default one supplied by the library.

6. Edit *\<bootloader_cm0p>/Makefile*: 

   1. Set `USE_EXT_FLASH` to '1', to use the external flash to store the secondary image.

   2. Set `SWAP_UPGRADE` to '1', to enable swap feature of MCUboot.

7. Connect the board to your PC using the provided USB cable through the KitProg3 USB connector.

8. Open a CLI terminal.

   On Linux and macOS, you can use any terminal application. On Windows, open the **modus-shell** app from the Start menu.

9. Navigate the terminal to the *\<mtb_shared>/mcuboot/\<tag>/scripts* folder.

10. Run the following command to ensure that the required modules are installed or already present ("Requirement already satisfied:" is printed).

      ```
      pip install -r requirements.txt
      ```

11. Open a serial terminal emulator and select the KitProg3 COM port. Set the serial port parameters to 8N1 and 115200 baud.

12. Build and program the application per the [Step-by-Step](https://github.com/cypresssemiconductorco/mtb-example-psoc6-mcuboot-basic#step-by-step-instructions) instructions in its [README](https://github.com/cypresssemiconductorco/mtb-example-psoc6-mcuboot-basic/blob/master/README.md).

    After programming, the bootloader application starts automatically.

    **Figure 1. Booting with No Bootable Image**

    ![](images/booting_without_bootable_image.png)

**Note:** This example does not demonstrate securely upgrading the image and booting from it using features such as image-signing and secure boot. See the [PSoC 64 Line of Secure MCUs](https://www.cypress.com/psoc64) that offer all those features built around MCUboot.

## Using the code example

Create the project and open it using one of the following:

<details><summary><b>In Eclipse IDE for ModusToolbox&trade;</b></summary>

1. Click the **New Application** link in the **Quick Panel** (or, use **File** > **New** > **ModusToolbox&trade; Application**). This launches the [Project Creator](http://www.cypress.com/ModusToolboxProjectCreator) tool.

2. Pick a kit supported by the code example from the list shown in the **Project Creator - Choose Board Support Package (BSP)** dialog.

   When you select a supported kit, the example is reconfigured automatically to work with the kit. To work with a different supported kit later, use the [Library Manager](https://www.cypress.com/ModusToolboxLibraryManager) to choose the BSP for the supported kit. You can use the Library Manager to select or update the BSP and firmware libraries used in this application. To access the Library Manager, click the link from the **Quick Panel**.

   You can also just start the application creation process again and select a different kit.

   If you want to use the application for a kit not listed here, you may need to update the source files. If the kit does not have the required resources, the application may not work.

3. In the **Project Creator - Select Application** dialog, choose the example by enabling the checkbox.

4. Optionally, change the suggested **New Application Name**.

5. Enter the local path in the **Application(s) Root Path** field to indicate where the application needs to be created.

   Applications that can share libraries can be placed in the same root path.

6. Click **Create** to complete the application creation process.

For more details, see the [Eclipse IDE for ModusToolbox&trade; User Guide](https://www.cypress.com/MTBEclipseIDEUserGuide) (locally available at *{ModusToolbox install directory}/ide_{version}/docs/mt_ide_user_guide.pdf*).

</details>

<details><summary><b>In Command-line Interface (CLI)</b></summary>

ModusToolbox provides the Project Creator as both a GUI tool and a command line tool to easily create one or more ModusToolbox&trade; applications. See the "Project Creator Tools" section of the [ModusToolbox&trade; User Guide](https://www.cypress.com/ModusToolboxUserGuide) for more details.

Alternatively, you can manually create the application using the following steps:

1. Download and unzip this repository onto your local machine, or clone the repository.

2. Open a CLI terminal and navigate to the application folder.

   On Linux and macOS, you can use any terminal application. On Windows, open the **modus-shell** app from the Start menu.

   **Note:** The cloned application contains a default BSP file (*TARGET_xxx.mtb*) in the *deps* folder. Use the [Library Manager](https://www.cypress.com/ModusToolboxLibraryManager) (`make modlibs` command) to select and download a different BSP file, if required. If the selected kit does not have the required resources or is not [supported](#supported-kits-make-variable-target), the application may not work.

3. Import the required libraries by executing the `make getlibs` command.

Various CLI tools include a `-h` option that prints help information to the terminal screen about that tool. For more details, see the [ModusToolbox&trade; User Guide](https://www.cypress.com/ModusToolboxUserGuide) (locally available at *{ModusToolbox install directory}/docs_{version}/mtb_user_guide.pdf*).

</details>

<details><summary><b>In Third-party IDEs</b></summary>

1. Follow the instructions from the **In Command-line Interface (CLI)** section to create the application, and import the libraries using the `make getlibs` command.

2. Export the application to a supported IDE using the `make <ide>` command.

    For a list of supported IDEs and more details, see the "Exporting to IDEs" section of the [ModusToolbox&trade; User Guide](https://www.cypress.com/ModusToolboxUserGuide) (locally available at *{ModusToolbox install directory}/docs_{version}/mtb_user_guide.pdf*.

3. Follow the instructions displayed in the terminal to create or import the application as an IDE project.
</details>

## Setting up the local MQTT mosquitto broker

The root directory of the OTA application is referred to as *\<OTA Application>* in this document.

This code example uses the locally installable mosquitto that runs on your computer as the default broker. You can also use one of the other public MQTT Brokers listed at [https://github.com/mqtt/mqtt.github.io/wiki/public_brokers](https://github.com/mqtt/mqtt.github.io/wiki/public_brokers).

1. Download the executable setup from [mosquitto downloads](https://mosquitto.org/download/) site.

2. Run the setup to install the software. During installation uncheck the **Service** component. Also, note down the installation directory.

3. Once the installation is complete, add the installation directory to the system **PATH**.

4. Open a CLI terminal.

   On Linux and macOS, you can use any terminal application. On Windows, open the **modus-shell** app from the Start menu

5. Navigate to the *\<OTA Application>/scripts/* folder.

6. Execute the following command to generate self-signed SSL certificates and keys. On Linux and macOS, you can get your device local IP address by running the `ifconfig` command on any terminal application. On Windows, run the `ipconfig` command on a command prompt.


   ```
   sh generate_ssl_cert.sh <local-ip-address-of-your-pc>
   ```

   Example:
   ```
   sh generate_ssl_cert.sh 192.168.0.10
   ```

   This step will generate the following files in the same *\<OTA Application>/scripts/* directory:

   1. mosquitto_ca.crt - Root CA certificate
   2. mosquitto_ca.key - Root CA private key
   3. mosquitto_server.crt - Server certificate
   4. mosquitto_server.key - Server private key
   5. mosquitto_client.crt - Client certificate
   6. mosquitto_client.key - Client private key

7. The *\<OTA Application>/scripts/mosquitto.conf* file is pre-configured for starting the mosquitto server for this code example. You can edit the file if you wish to make other changes to the broker settings.

8. Starting the mosquitto MQTT server:

   - **Using the Code Example in TLS Mode (default):**

      1. Execute the following command:

         ```
         mosquitto -v -c mosquitto.conf
         ```
   
   - **Using the Code Example in Non-TLS Mode:**

      1. Edit the *\<OTA Application>/scripts/mosquitto.conf* file and change the value of `require_certificate` parameter to `false`.

      2. Execute the following command:

         ```
         mosquitto -v -c mosquitto.conf
         ```

## Setting up the MQTT publisher script

1. Open a CLI terminal.

   On Linux and macOS, you can use any terminal application. On Windows, open the **modus-shell** app from the Start menu.

2. Navigate to the *\<OTA Application>/scripts/* folder.

3. Run the following command to ensure that the required Python modules are installed or already present ("Requirement already satisfied:" is printed).

      ```
      pip install -r requirements.txt
      ```

4. Edit the *\<OTA Application>/scripts/publisher.py* file and change the value of the variable `MOSQUITTO_BROKER_LOCAL_ADDRESS` to the local IP address of your PC.

5. Run the *publisher.py* python script.

   The scripts takes arguments such as kit name, broker URL, and file path. For details on the supported arguments and their usage, execute the following command.

   ```
   python publisher.py --help
   ```

   To start the publisher script for the default settings of this example, execute the following command:

   ```
   python publisher.py tls
   ```

## Operation

1. Connect the board to your PC using the provided USB cable through the KitProg3 USB connector.

2. Open a terminal program and select the KitProg3 COM port. Set the serial port parameters to 8N1 and 115200 baud.

3. Edit the *\<OTA Application>/source/ota_app_config.h* file to configure your OTA application:

   1. Modify the connection configuration such as `WIFI_SSID`, `WIFI_PASSWORD`, and `WIFI_SECURITY` to match the settings of your Wi-Fi network. Make sure the device running the MQTT broker and the kit are connected to the same network.

   2. Modify the value of `MQTT_BROKER_URL` to the local IP address of your MQTT broker.

   3. By default, this code example works in TLS mode. To use the example in non-TLS mode, modify `ENABLE_TLS` to `false` and skip the next step of adding the certificate.

   4. Add the certificates and key:

      1. Open a CLI terminal.

          On Linux and macOS, you can use any terminal application. On Windows, open the **modus-shell** app from the Start menu.

      2. Navigate the terminal to *\<OTA Application>/scripts/* directory.

      3. Run the *format_cert_key.py* Python script to generate the string format of the certificate and key files that can be added as a macro. Pass the name of the certificate or key with the extension as an argument to the Python script:

         ```
         python format_cert_key.py <one-or-more-file-name-of-certificate-or-key-with-extension>
         ```
         
         Example:
         ```
         python format_cert_key.py mosquitto_ca.crt mosquitto_client.crt mosquitto_client.key
         ```
      4. Copy the generated strings and add it to the `ROOT_CA_CERTIFICATE`, `CLIENT_CERTIFICATE` and `CLIENT_KEY` macros per the sample shown.

4. Edit the Job document (*\<OTA Application>/scripts/ota_update.json*):

   1. Modify the value of `Broker` to match the IP address of your MQTT broker.

   2. Modify the value of `Board` to match the kit you are using.

   3. In Step 3, if the code example has been configured to work in non-TLS mode: Set the value of `Port` to `1883`.

5. Program the board.

   <details open><summary><b>Using Eclipse IDE for ModusToolbox</b></summary>

      1. Select the application project in the Project Explorer.

      2. In the **Quick Panel**, scroll down, and click **\<Application Name> Program (KitProg3_MiniProg4)**.
   </details>

   <details open><summary><b>Using CLI</b></summary>

     From the terminal, execute the `make program` command to build and program the application using the default toolchain to the default target. You can specify a target and toolchain manually:
      ```
      make program TARGET=<BSP> TOOLCHAIN=<toolchain>
      ```

      Example:
      ```
      make program TARGET=CY8CPROTO-062-4343W TOOLCHAIN=GCC_ARM
      ```
   </details>

   At this point, the primary slot is programmed. The CM4 CPU starts running the image from the primary slot on reset. Observe the messages on the UART terminal and wait for the device to make the required connections as shown in Figure 2. Observe that the user LED blinks at 1 Hz.

   **Figure 2. Connection to the MQTT Broker**

   ![](images/connection_mqtt_broker.png)

6. The Job document placed in the *\<OTA Application>/scripts/* folder has a value of `Version` as `1.0.0`. Because the OTA application version and the available update version are the same, the update will not happen.

7. Modify the value of the `BLINKY_DELAY_MS` macro to `(100)` in the *\<OTA Application>/source/led_task.c* file and change the app version in the *\<OTA Application>/Makefile* by setting `APP_VERSION_MINOR` to '1'.

8. Build the app (**DO NOT** program it to the kit). This new image will be published to the MQTT Broker in the following steps to demonstrate the OTA update.

   <details open><summary><b>Using Eclipse IDE for ModusToolbox</b></summary>

      1. Select the application project in the Project Explorer.

      2. In the **Quick Panel**, scroll down, and click **Build \<OTA Application> Application**.
   </details>

   <details open><summary><b>Using CLI</b></summary>

      1. From the terminal, execute the `make build` command to build the application using the default toolchain to the default target. You can specify a target and toolchain manually:
         ```
         make build TARGET=<BSP> TOOLCHAIN=<toolchain>
         ```
         Example:
         ```
         make build TARGET=CY8CPROTO-062-4343W TOOLCHAIN=GCC_ARM
         ```
         </details>


9. After a successful build, edit the *\<OTA Application>/scripts/ota_update.json* file to modify the value of `Version` to `1.1.0`.

10. The OTA application now finds the updated Job document, downloads the new image, and places it in the secondary slot. Once the download is complete, a soft reset is issued. The MCUboot bootloader starts the image upgrade process.

    **Figure 3. Image Download**

    ![](images/downloading_new_image.png)

11. After the image upgrade is successfully completed, observe that the user LED is now blinking at 10 Hz.

12. To test the revert feature of MCUBoot, we can send a bad image as v1.2.0 OTA update. The bad image used in this example is an infinite loop. The watchdog timer will reset the bad image and upon reboot, MCUboot will revert the primary image back to v1.1.0 good image. Edit *\<OTA Application>/Makefile* and add `TEST_REVERT` to the `Defines` variable as shown:

      ```
      DEFINES+=CY_RTOS_AWARE HTTP_DO_NOT_USE_CUSTOM_CONFIG TEST_REVERT
      ```

13. Edit the app version in the *\<OTA Application>/Makefile* by setting `APP_VERSION_MINOR` to '2'.

14. Build the application per step 8.

15. After a successful build, edit the *\<OTA Application>/scripts/ota_update.json* file to modify the value of `Version` to `1.2.0`.

16. The OTA application will now find this new v1.2.0 image and update to it. After the update, within a few seconds, the watchdog timer resets the devices. Upon reset, MCUBoot reverts to the v1.1.0 good image.

## Debugging

You can debug the example to step through the code. In the IDE, use the **\<OTA Application> Debug (KitProg3_MiniProg4)** configuration in the **Quick Panel**. For more details, see the "Program and Debug" section in the [Eclipse IDE for ModusToolbox&trade; User Guide](https://www.cypress.com/MTBEclipseIDEUserGuide).

**Note:** **(Only while debugging)** On the CM4 CPU, some codes in `main()` may execute before the debugger halts at the beginning of `main()`. This means that some codes execute twice - once before the debugger stops execution, and again after the debugger resets the program counter to the beginning of `main()`. See [KBA231071](https://community.cypress.com/docs/DOC-21143) to learn about this and for the workaround.

## Design and implementation

This example implements two RTOS tasks: OTA client and LED blink. Both these tasks are independent and do not communicate with each other. The OTA client task initializes the dependent middleware and starts the OTA agent. The LED task blinks the user LED at a specified delay.

All the source files related to the two tasks are placed under the *\<OTA Application>/source/* directory:

| File | Description |
|:-----|:------|
|*ota_task.c*| Contains the task and functions related to the OTA client.|
|*ota_task.h* | Contains the public interfaces for the OTA client task.|
|*led_task.c* | Contains the task and functions related to LED blinking.|
|*led_task.h* | Contains the public interfaces for the LED blink task.|
|*main.c* | Initializes the BSP and the retarget-io library, and creates the OTA client and LED blink tasks.|
|*ota_app_config.h* | Contains the OTA and Wi-Fi configuration macros such has SSID, password, MQTT Broker details, certificates, and key.|

All the scripts and configurations needed for this example are placed under the *\<OTA Application>/scripts/* directory:

| File | Description |
|:-----|:------|
|*generate_ssl_cert.sh*| Shell script to generate the required self-signed CA, server and client certificates.|
|*publisher.py* | Python script to communicate with the client and to publish the OTA images. |
|*mosquitto.conf* | Configuration file for the mosquitto server. |
|*ota_update.json* | OTA job document. |
|*format_cert_key.py* | Python script to convert certificate/key to string format. |

The *\<OTA Application>/configs/* folder contains other configurations related to the OTA middleware, FreeRTOS, and MBEDTLS.

Figure 4 shows the flow of the OTA update process using MQTT. The application which needs OTA updates should run the OTA Agent. The OTA Agent spawns threads to receive OTA updates when available, without intervening with the application's core functionality.

The initial application resides in the primary slot of the flash memory. When the OTA Agent receives an update, the new image is placed in the secondary slot of the flash memory. On the next reboot, MCUboot copies the image from the secondary slot into the primary slot and then CM4 will boot the upgraded image from the primary slot.

**Figure 4. Overview of OTA Update Using MQTT**

![](images/ota_mqtt_update_flow.png)

For more details on the features and configurations offered by the [anycloud-ota](https://github.com/cypresssemiconductorco/anycloud-ota) library, see its [README](https://github.com/cypresssemiconductorco/anycloud-ota/blob/master/README.md).

Both MCUboot and the application must have an identical understanding of the memory layout. Otherwise, the bootloader may consider an authentic image as invalid. For more details on the features and configurations of MCUboot-based bootloader, see the [README](https://github.com/cypresssemiconductorco/mtb-example-psoc6-mcuboot-basic/blob/master/README.md) of the [mtb-example-psoc6-mcuboot-basic](https://github.com/cypresssemiconductorco/mtb-example-psoc6-mcuboot-basic) code example.

### Resources and settings

**Table 1. Application Resources**

| Resource  |  Alias/Object     |    Purpose     |
| :-------  | :------------     | :------------  |
| UART (HAL)|cy_retarget_io_uart_obj| UART HAL object used by Retarget-IO for Debug UART port  |
| GPIO (HAL)| CYBSP_USER_LED    | User LED       |

## Related resources

| Application Notes                                            |                                                              |
| :----------------------------------------------------------- | :----------------------------------------------------------- |
| [AN228571](https://www.cypress.com/AN228571) – Getting Started with PSoC&trade; 6 MCU on ModusToolbox&trade; | Describes PSoC&trade; 6 MCU devices and how to build your first application with ModusToolbox&trade; |
| [AN221774](https://www.cypress.com/AN221774) – Getting Started with PSoC&trade; 6 MCU on PSoC Creator&trade; | Describes PSoC&trade; 6 MCU devices and how to build your first application with PSoC Creator&trade; |
| [AN210781](https://www.cypress.com/AN210781) – Getting Started with PSoC&trade; 6 MCU with Bluetooth Low Energy (BLE) Connectivity on PSoC Creator&trade; | Describes PSoC&trade; 6 MCU with BLE Connectivity devices and how to build your first application with PSoC Creator&trade; |
| [AN215656](https://www.cypress.com/AN215656) – PSoC&trade; 6 MCU: Dual-CPU System Design | Describes the dual-CPU architecture in PSoC&trade; 6 MCU, and shows how to build a simple dual-CPU design |
| **Code Examples**                                            |                                                              |
| [Using ModusToolbox&trade;](https://github.com/cypresssemiconductorco/Code-Examples-for-ModusToolbox-Software) | [Using PSoC Creato&trade;](https://www.cypress.com/documentation/code-examples/psoc-6-mcu-code-examples) |
| **Device Documentation**                                     |                                                              |
| [PSoC&trade; 6 MCU Datasheets](https://www.cypress.com/search/all?f[0]=meta_type%3Atechnical_documents&f[1]=resource_meta_type%3A575&f[2]=field_related_products%3A114026) | [PSoC&trade; 6 Technical Reference Manuals](https://www.cypress.com/search/all/PSoC%206%20Technical%20Reference%20Manual?f[0]=meta_type%3Atechnical_documents&f[1]=resource_meta_type%3A583) |
| **Development Kits**                                         | Buy at www.cypress.com                                       |
| [CY8CKIT-062-BLE](https://www.cypress.com/CY8CKIT-062-BLE) PSoC&trade; 6-BLE Pioneer Kit | [CY8CKIT-062-WiFi-BT](https://www.cypress.com/CY8CKIT-062-WiFi-BT) PSoC&trade; 6 WiFi-BT Pioneer Kit |
| [CY8CPROTO-063-BLE](https://www.cypress.com/CY8CPROTO-063-BLE) PSoC&trade; 6-BLE Prototyping Kit | [CY8CPROTO-062-4343W](https://www.cypress.com/CY8CPROTO-062-4343W) PSoC&trade; 6 Wi-Fi BT Prototyping Kit |
| [CY8CKIT-062S2-43012](https://www.cypress.com/CY8CKIT-062S2-43012) PSoC&trade; 62S2 Wi-Fi BT Pioneer Kit | [CY8CPROTO-062S3-4343W](https://www.cypress.com/CY8CPROTO-062S3-4343W) PSoC&trade; 62S3 Wi-Fi BT Prototyping Kit |
| [CYW9P62S1-43438EVB-01](https://www.cypress.com/CYW9P62S1-43438EVB-01) PSoC&trade; 62S1 Wi-Fi BT Pioneer Kit | [CYW9P62S1-43012EVB-01](https://www.cypress.com/CYW9P62S1-43012EVB-01) PSoC&trade; 62S1 Wi-Fi BT Pioneer Kit |
| [CY8CKIT-064B0S2-4343W](http://www.cypress.com/CY8CKIT-064B0S2-4343W) PSoC&trade; 64 Secure Boot Wi-Fi BT Pioneer Kit | CYSBSYSKIT-01 Rapid IoT Connect Platform RP01 Feather Kit |
| CYSBSYSKIT-DEV-01 Rapid IoT Connect Developer Kit |
| **Libraries**                                                |                                                              |
| PSoC&trade; 6 Peripheral Driver Library (PDL) and docs  | [mtb-pdl-cat1](https://github.com/cypresssemiconductorco/mtb-pdl-cat1) on GitHub |
| Cypress Hardware Abstraction Layer (HAL) Library and docs    | [mtb-hal-cat1](https://github.com/cypresssemiconductorco/mtb-hal-cat1) on GitHub |
| Retarget IO - A utility library to retarget the standard input/output (STDIO) messages to a UART port | [retarget-io](https://github.com/cypresssemiconductorco/retarget-io) on GitHub |
| **Middleware**                                               |                                                              ||                                                              |
| AnyCloud OTA library and docs                                | [anycloud-ota](https://github.com/cypresssemiconductorco/anycloud-ota) on GitHub |
| Wi-Fi Middleware Core library and docs                       | [wifi-mw-core](https://github.com/cypresssemiconductorco/wifi-mw-core) on GitHub |
| CapSense® library and docs                                    | [capsense](https://github.com/cypresssemiconductorco/capsense) on GitHub |
| Links to all PSoC&trade; 6 MCU Middleware                           | [psoc6-middleware](https://github.com/cypresssemiconductorco/psoc6-middleware) on GitHub |
| **Tools**                                                    |                                                              |
| [Eclipse IDE for ModusToolbox&trade;](https://www.cypress.com/modustoolbox) | The cross-platform, Eclipse-based IDE for IoT designers that supports application configuration and development targeting converged MCU and wireless systems. |
| [PSoC Creator™](https://www.cypress.com/products/psoc-creator-integrated-design-environment-ide) | The Cypress IDE for PSoC and FM0+ MCU development. |

## Other resources

Cypress provides a wealth of data at www.cypress.com to help you select the right device, and quickly and effectively integrate it into your design.

For PSoC&trade; 6 MCU devices, see [How to Design with PSoC&trade; 6 MCU - KBA223067](https://community.cypress.com/docs/DOC-14644) in the Cypress community.

## Document History

Document Title: *CE230031* - *AnyCloud: Over-the-Air Firmware Update Using MQTT*

| Version | Description of Change                                        |
| ------- | ------------------------------------------------------------ |
| 1.0.0   | New code example.                                            |
| 1.1.0   | Minor Makefile updates to sync with BSP changes.             |
| 1.2.0   | Updated the *.cyignore* file to support new build system changes. |
| 2.0.0   | Updated to support AnyCloud OTA v2.x and ModusToolbox v2.2. <br> This version is not backward compatible with ModusToolbox&trade; software v2.1. |
| 2.1.0   | Minor update to README - Added steps to install required Python modules. |
| 2.2.0   | Updated the configuration file to support MbedTLS v2.22.0    |
| 3.0.0   | Update to:<br>1. Support anycloud-ota v4.X library. <br>2. Use locally installed mosquitto broker. <br>3. Support swap upgrade with MCUboot |
------

All other trademarks or registered trademarks referenced herein are the property of their respective owners.

![banner](images/ifx-cy-banner.png)

-------------------------------------------------------------------------------

© Cypress Semiconductor Corporation (An Infineon Technologies Company), 2020-2021. This document is the property of Cypress Semiconductor Corporation and its subsidiaries ("Cypress"). This document, including any software or firmware included or referenced in this document ("Software"), is owned by Cypress under the intellectual property laws and treaties of the United States and other countries worldwide. Cypress reserves all rights under such laws and treaties and does not, except as specifically stated in this paragraph, grant any license under its patents, copyrights, trademarks, or other intellectual property rights. If the Software is not accompanied by a license agreement and you do not otherwise have a written agreement with Cypress governing the use of the Software, then Cypress hereby grants you a personal, non-exclusive, nontransferable license (without the right to sublicense) (1) under its copyright rights in the Software (a) for Software provided in source code form, to modify and reproduce the Software solely for use with Cypress hardware products, only internally within your organization, and (b) to distribute the Software in binary code form externally to end users (either directly or indirectly through resellers and distributors), solely for use on Cypress hardware product units, and (2) under those claims of Cypress's patents that are infringed by the Software (as provided by Cypress, unmodified) to make, use, distribute, and import the Software solely for use with Cypress hardware products. Any other use, reproduction, modification, translation, or compilation of the Software is prohibited.<br />
TO THE EXTENT PERMITTED BY APPLICABLE LAW, CYPRESS MAKES NO WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, WITH REGARD TO THIS DOCUMENT OR ANY SOFTWARE OR ACCOMPANYING HARDWARE, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. No computing device can be absolutely secure. Therefore, despite security measures implemented in Cypress hardware or software products, Cypress shall have no liability arising out of any security breach, such as unauthorized access to or use of a Cypress product. CYPRESS DOES NOT REPRESENT, WARRANT, OR GUARANTEE THAT CYPRESS PRODUCTS, OR SYSTEMS CREATED USING CYPRESS PRODUCTS, WILL BE FREE FROM CORRUPTION, ATTACK, VIRUSES, INTERFERENCE, HACKING, DATA LOSS OR THEFT, OR OTHER SECURITY INTRUSION (collectively, "Security Breach"). Cypress disclaims any liability relating to any Security Breach, and you shall and hereby do release Cypress from any claim, damage, or other liability arising from any Security Breach. In addition, the products described in these materials may contain design defects or errors known as errata which may cause the product to deviate from published specifications. To the extent permitted by applicable law, Cypress reserves the right to make changes to this document without further notice. Cypress does not assume any liability arising out of the application or use of any product or circuit described in this document. Any information provided in this document, including any sample design information or programming code, is provided only for reference purposes. It is the responsibility of the user of this document to properly design, program, and test the functionality and safety of any application made of this information and any resulting product. "High-Risk Device" means any device or system whose failure could cause personal injury, death, or property damage. Examples of High-Risk Devices are weapons, nuclear installations, surgical implants, and other medical devices. "Critical Component" means any component of a High-Risk Device whose failure to perform can be reasonably expected to cause, directly or indirectly, the failure of the High-Risk Device, or to affect its safety or effectiveness. Cypress is not liable, in whole or in part, and you shall and hereby do release Cypress from any claim, damage, or other liability arising from any use of a Cypress product as a Critical Component in a High-Risk Device. You shall indemnify and hold Cypress, its directors, officers, employees, agents, affiliates, distributors, and assigns harmless from and against all claims, costs, damages, and expenses, arising out of any claim, including claims for product liability, personal injury or death, or property damage arising from any use of a Cypress product as a Critical Component in a High-Risk Device. Cypress products are not intended or authorized for use as a Critical Component in any High-Risk Device except to the limited extent that (i) Cypress's published data sheet for the product explicitly states Cypress has qualified the product for use in a specific High-Risk Device, or (ii) Cypress has given you advance written authorization to use the product as a Critical Component in the specific High-Risk Device and you have signed a separate indemnification agreement.<br />
Cypress, the Cypress logo, Spansion, the Spansion logo, and combinations thereof, WICED, PSoC, CapSense, EZ-USB, F-RAM, and Traveo are trademarks or registered trademarks of Cypress in the United States and other countries. For a more complete list of Cypress trademarks, visit cypress.com. Other names and brands may be claimed as property of their respective owners.