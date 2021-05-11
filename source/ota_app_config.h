/******************************************************************************
* File Name: ota_app_config.h
*
* Description: Contains all the configurations required for the OTA App.
*
********************************************************************************
* Copyright 2020-2021, Cypress Semiconductor Corporation (an Infineon company) or
* an affiliate of Cypress Semiconductor Corporation.  All rights reserved.
*
* This software, including source code, documentation and related
* materials ("Software") is owned by Cypress Semiconductor Corporation
* or one of its affiliates ("Cypress") and is protected by and subject to
* worldwide patent protection (United States and foreign),
* United States copyright laws and international treaty provisions.
* Therefore, you may use this Software only as provided in the license
* agreement accompanying the software package from which you
* obtained this Software ("EULA").
* If no EULA applies, Cypress hereby grants you a personal, non-exclusive,
* non-transferable license to copy, modify, and compile the Software
* source code solely for use in connection with Cypress's
* integrated circuit products.  Any reproduction, modification, translation,
* compilation, or representation of this Software except as specified
* above is prohibited without the express written permission of Cypress.
*
* Disclaimer: THIS SOFTWARE IS PROVIDED AS-IS, WITH NO WARRANTY OF ANY KIND,
* EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, NONINFRINGEMENT, IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. Cypress
* reserves the right to make changes to the Software without notice. Cypress
* does not assume any liability arising out of the application or use of the
* Software or any product or circuit described in the Software. Cypress does
* not authorize its products for use in any products where a malfunction or
* failure of the Cypress product may reasonably be expected to result in
* significant property damage, injury or death ("High Risk Product"). By
* including Cypress's product in a High Risk Product, the manufacturer
* of such system or application assumes all risk of such use and in doing
* so agrees to indemnify Cypress against all liability.
*******************************************************************************/

#ifndef SOURCE_OTA_APP_CONFIG_H_
#define SOURCE_OTA_APP_CONFIG_H_

#include "cy_ota_config.h"

/***********************************************
 * Connection configuration
 **********************************************/
/* Name of the Wi-Fi network */
#define WIFI_SSID           "WIFI_SSID"

/* Password for the Wi-Fi network */
#define WIFI_PASSWORD       "WIFI_PASSWORD"

/* Security type of the Wi-Fi access point. See 'cy_wcm_security_t' structure
 * in "cy_wcm.h" for more details.
 */
#define WIFI_SECURITY       (CY_WCM_SECURITY_WPA2_AES_PSK)

/* MQTT Broker endpoint */
#define MQTT_BROKER_URL     "test.mosquitto.org"

/* MQTT Server Port */
/************************************************************
 * Server Port for https://test.mosquitto.org/
 * MQTT:        1883 un-encrypted
 * secure MQTT: 8883 encrypted
 * secure MQTT: 8884 encrypted, client certificate required
 ************************************************************/
#define MQTT_SERVER_PORT    (1883)

/* Macro to enable/disable TLS */
#define ENABLE_TLS          (false)

/* MQTT identifier - less than 17 characters*/
#define OTA_MQTT_ID         "CY_IOT_DEVICE"

/* Number of MQTT topic filters */
#define MQTT_TOPIC_FILTER_NUM   (1)

/* MQTT topics */
const char * my_topics[ MQTT_TOPIC_FILTER_NUM ] =
{
        COMPANY_TOPIC_PREPEND "/" CY_TARGET_BOARD_STRING "/" PUBLISHER_DIRECT_TOPIC
};

/*
 * AWS IoT MQTT Mode - This parameter must be 1 when using the AWS IoT MQTT
 *                     server, 0 otherwise.
 */
#define AWS_IOT_MQTT_MODE   (0)

/**********************************************
 * Certificates and Keys - TLS Mode only
 *********************************************/
/* Root CA Certificate -
   Must include the PEM header and footer:

        "-----BEGIN CERTIFICATE-----\n" \
        ".........base64 data.......\n" \
        "-----END CERTIFICATE-------\n"
*/
#define ROOT_CA_CERTIFICATE     ""

/* Client Certificate
   Must include the PEM header and footer:

        "-----BEGIN CERTIFICATE-----\n" \
        ".........base64 data.......\n" \
        "-----END CERTIFICATE-------\n"
*/
#define CLIENT_CERTIFICATE      ""


/* Private Key
   Must include the PEM header and footer:

        "-----BEGIN RSA PRIVATE KEY-----\n" \
        "...........base64 data.........\n" \
        "-----END RSA PRIVATE KEY-------\n"
*/
#define CLIENT_KEY              ""

#endif /* SOURCE_OTA_APP_CONFIG_H_ */
