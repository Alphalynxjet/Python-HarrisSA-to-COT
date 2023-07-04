

## Python CoT Sender

This Python script is designed to listen for HarrisSA UDP packets, parse them, and send Cursor-on-Target (CoT) messages to a specified server or localhost ATAK client. It provides the functionality to create a loop of CoT messages with a configurable time interval. ( This is useful so if a ATAK user is not online when a radio sends its PLI, it will be looped. So the user that come online will receive the latest information of the radio locations. ) The script also adds the original time of report in the COTs remarks using your specified timezone.

**Dependencies**

**colorama:** Terminal text colorization library. Install it using the command: 

    pip install colorama

**pytz:** Time zone manipulation library. Install it using the command: 

    pip install pytz

## Usage

Make sure the required dependencies are installed.

**Update the following configuration variables according to your needs:**

    nano script.py

**LISTENING_PORT:** The port on which the script listens for UDP packets.
**SERVER_IP:** The IP address of the destination server to which CoT messages will be sent.
**DESTINATION_PORT:** The destination port on the server for receiving CoT messages.
**COT_TYPE:** The type of CoT message to be sent.
**TIMEZONE:** The desired timezone for timestamping the CoT messages.
**LOOP_TIME:** The time interval (in seconds) between consecutive loops of CoT messages.
**LOOP_ENABLED:** Set to True to enable the loop functionality or False to disable it.

Run the script using the following command: 

    python script.py

The script will start listening for UDP packets on the specified LISTENING_PORT. When a packet is received, it will be parsed to extract the callsign, latitude, and longitude information.

A CoT message will be constructed using the extracted information, along with the current time and other details.

The constructed CoT message will be sent to the specified server (SERVER_IP and DESTINATION_PORT).

If the loop functionality is enabled (LOOP_ENABLED is set to True), the script will maintain a dictionary (cot_loop) to store the CoT messages for each unique callsign.

If a new packet with a callsign is received and it is not already present in the cot_loop dictionary, the CoT message will be added to the dictionary and scheduled for repeated transmission every LOOP_TIME seconds.

If a packet with the same callsign is received and it is already present in the cot_loop dictionary, the old CoT message will be replaced with the new one.

To stop the script, you can terminate it using the appropriate method for your operating system (e.g., pressing Ctrl+C in the terminal).
