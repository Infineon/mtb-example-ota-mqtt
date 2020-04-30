import paho.mqtt.publish as publish
import os
import struct
import traceback
import time

KIT = "CY8CPROTO-062-4343W"
BROKER_ADDRESS = "test.mosquitto.org"
TLS_ENABLED = False
BROKER_PORT = 1883  # For Mosquitto: Port = 8884 when TLS is enabled; Port = 1883 otherwise
MQTT_CLIENT_ID = "OTAPublisher"
PUBLISH_TOPIC = "anycloud/test/ota/image"
PUBLISH_QOS = 1     # AWS broker does not support QOS of 2

# Can take "Multiple" and "Single" as values. 
# Single - Publish a single message to a broker, then disconnect cleanly. That is, the script will disconnect and reconnect for publishing every chunk.
# Multiple - Publish multiple messages to a broker, then disconnect cleanly. That is, the script will publish all messages at once and then disconnect.
PUBLISH_TYPE = "Multiple"

# Full file path to the firmware image
FW_IMAGE_FILE = "../build/" + KIT + "/Debug/mtb-example-anycloud-ota-mqtt.bin"

# Paho MQTT client settings
MQTT_KEEP_ALIVE = 60 # in seconds
CHUNK_SIZE = (4 * 1024)

# OTA header information
HEADER_SIZE = 32 # in bytes
HEADER_MAGIC = "OTAImage"
IMAGE_TYPE = 0
VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_BUILD = 0

def do_chunking(image_file): 
    image_size = os.path.getsize(image_file)
    total_payloads = image_size//CHUNK_SIZE

    if ((image_size % CHUNK_SIZE) != 0):
        total_payloads += 1

    print("Image Size: " + str(image_size) + ", Total Payloads: " + str(total_payloads))

    with open(image_file, 'rb') as image:
        offset = 0
        payload_index = 0
        mqtt_msgs = []

        while True:
            chunk = image.read(CHUNK_SIZE)
            if chunk:
                chunk_size = len(chunk)
                packet = bytearray(HEADER_SIZE)
                
                # MQTT payload (chunk) header format is defined in anycloud-ota/source/cy_ota_mqtt.c
                # typedef struct cy_ota_mqtt_chunk_payload_header_s {
                #     const char      magic[8];                          /* "OTAImage"                                            */
                #     const uint16_t  offset_to_data;                    /* Offset within this payload to start of data           */
                #     const uint16_t  ota_image_type;                    /* 0 = single application OTA Image                      */
                #     const uint16_t  update_version_major;              /* Major version number                                  */
                #     const uint16_t  update_version_minor;              /* Minor version number                                  */
                #     const uint16_t  update_version_build;              /* Build version number                                  */
                #     const uint32_t  total_size;                        /* Total size of OTA Image                               */
                #     const uint32_t  image_offset;                      /* Offset within the final OTA Image of THIS chunk data  */
                #     const uint16_t  data_size;                         /* Size of chunk data in THIS payload                    */
                #     const uint16_t  total_num_payloads;                /* Total number of payloads                              */
                #     const uint16_t  this_payload_index;                /* THIS payload index                                    */
                # } cy_ota_mqtt_chunk_payload_header_t;

                # s - 1 byte character, H - 2 bytes integer, I - 4 bytes integer
                struct.pack_into('<8s5H2I3H', packet, 0, HEADER_MAGIC.encode('ascii'), 
                                  HEADER_SIZE, IMAGE_TYPE, VERSION_MAJOR, VERSION_MINOR, 
                                  VERSION_BUILD, image_size, offset, chunk_size, total_payloads, 
                                  payload_index)

                packet += chunk
                if PUBLISH_TYPE == "Single":
                    mqtt_msgs.append(packet)
                else:
                    current_msg = {'topic':PUBLISH_TOPIC, 'payload':packet, 'qos':PUBLISH_QOS}
                    mqtt_msgs.append(current_msg)

                offset += chunk_size
                payload_index += 1
            else:
                break

        return mqtt_msgs

tls_dict = None
if TLS_ENABLED:
    tls_dict = {'ca_certs':"mosquitto.org.crt", 'certfile':"client.crt", 'keyfile':"client.key"}
    print("Connecting using TLS to " + BROKER_ADDRESS + ":" + str(BROKER_PORT) + os.linesep)
else:
    print("Unencrypted connection to \"" + BROKER_ADDRESS + ":" + str(BROKER_PORT) + "\"" + os.linesep)

try:
    mqtt_msgs = do_chunking(FW_IMAGE_FILE)
    chunk_count = 0
    print("Publishing Begins...")
    if PUBLISH_TYPE == "Single":
        for msg in mqtt_msgs:
            publish.single(PUBLISH_TOPIC, msg, PUBLISH_QOS, hostname=BROKER_ADDRESS, port=BROKER_PORT, client_id=MQTT_CLIENT_ID, keepalive=MQTT_KEEP_ALIVE, tls=tls_dict)
            chunk_count = chunk_count + 1
            print("Published Chunk %d" %(chunk_count))
    else:
        publish.multiple(mqtt_msgs, hostname=BROKER_ADDRESS, port=BROKER_PORT, client_id=MQTT_CLIENT_ID, keepalive=MQTT_KEEP_ALIVE, tls=tls_dict)
    print("Publishing Ends...")
except Exception as e:
    print("Exception Occurred... Exiting...")
    print(str(e) + os.linesep)
    traceback.print_exc()
    exit()