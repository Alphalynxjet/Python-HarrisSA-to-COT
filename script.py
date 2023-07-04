import socket
import re
import datetime
import pytz
import colorama
import threading
import time

colorama.init()

cot_loop = {}

# Define the listening port
LISTENING_PORT = 10011

# Define the server IP and destination port
SERVER_IP = "127.0.0.1"
DESTINATION_PORT = 4242

# Define the CoT type
COT_TYPE = "a-f-G-U-C-I"

# Define the desired timezone here
TIMEZONE = "ETC/GMT-3"

# Define the loop time in seconds
LOOP_TIME = 30

# Enable or disable the loop, True or False
LOOP_ENABLED = True

"""
The pytz library uses the opposite sign convention for the Etc/GMT time zones.
In the case of Etc/GMT+3, it actually represents a time zone that is 3 hours behind GMT (UTC).
So if you need GMT+3 you need to use GMT-3 as the timezone.

Example timezones:

Etc/GMT0
Etc/GMT+1
Etc/GMT+2
Etc/GMT+3
Etc/GMT+4
Etc/GMT+5
Etc/GMT+6
Etc/GMT+7
Etc/GMT+8
Etc/GMT+9
Etc/GMT+10
Etc/GMT+11
Etc/GMT+12
Etc/GMT-1
Etc/GMT-2
Etc/GMT-3
Etc/GMT-4
Etc/GMT-5
Etc/GMT-6
Etc/GMT-7
Etc/GMT-8
Etc/GMT-9
Etc/GMT-10
Etc/GMT-11
Etc/GMT-12
Etc/GMT-13
Etc/GMT-14

"""

def parse_packet(payload):
    # Remove non-printable characters
    payload = re.sub(r'[^\x20-\x7E]', '', payload)

    # Find the repeated callsign
    callsign = re.findall(r'([a-zA-Z0-9]+).*\1$', payload)
    if callsign:
        callsign = callsign[0]
    else:
        callsign = "Callsign not found"

    # Extract latitude and convert to decimal format
    lat_index_start = payload.index(",A,") + 3
    lat_index_end = payload.index(",N,")
    lat_dms = payload[lat_index_start:lat_index_end]
    lat_parts = lat_dms.split(".")
    lat_degrees = lat_parts[0][:2]
    lat_minutes = lat_parts[0][2:] + "." + lat_parts[1]
    lat_decimal = float(lat_degrees) + float(lat_minutes) / 60

    # Extract longitude and convert to decimal format
    lon_index_start = payload.index(",N,") + 3
    lon_index_end = payload.index(",E,")
    lon_dms = payload[lon_index_start:lon_index_end]
    lon_parts = lon_dms.split(".")
    lon_degrees = lon_parts[0][:3]
    lon_minutes = lon_parts[0][3:] + "." + lon_parts[1]
    lon_decimal = float(lon_degrees) + float(lon_minutes) / 60

    # Calculate stale time (1 hour from now)
    stale_time = (datetime.datetime.now(pytz.timezone(TIMEZONE)) + datetime.timedelta(hours=1)).isoformat()

    # Get the current date and time in the desired timezone
    current_date = datetime.datetime.now(pytz.timezone(TIMEZONE))
    current_date_time = current_date.isoformat()

    # Construct CoT message in XML format
    cot_message = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
        f'<event version="2.0" uid="{callsign}" type="{COT_TYPE}" how="m-g" time="{current_date_time}" start="{current_date_time}" stale="{stale_time}">' \
        f'<point lat="{lat_decimal}" lon="{lon_decimal}" hae="0.0" ce="9999999.0" le="9999999.0"/>' \
        f'<detail>' \
        f'<contact callsign="{callsign}"/>' \
        f'<remarks>LAST SA REPORT FROM RADIO: {current_date.strftime("%H:%M:%S")} </remarks>' \
        f'<track course="0.0" speed="0.0"/>' \
        f'<source type="dataFeed" name="NODE-RED" uid="node-red-123456789"/>' \
        f'</detail>' \
        f'</event>'

    return cot_message, callsign

def send_cot_message(cot_message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.sendto(cot_message.encode("utf-8"), (SERVER_IP, DESTINATION_PORT))

def repeat(callsign):
    cot_message = cot_loop[callsign]
    cot_count = len(cot_loop)
    print(colorama.Fore.GREEN + "Outgoing packet:", cot_message + colorama.Style.RESET_ALL)
    print(colorama.Fore.YELLOW + f"Number of COTs in loop: {cot_count}" + colorama.Style.RESET_ALL)
    print(colorama.Fore.CYAN + f"Next loop in {LOOP_TIME} seconds" + colorama.Style.RESET_ALL)
    send_cot_message(cot_message)
    if LOOP_ENABLED:
        threading.Timer(LOOP_TIME, repeat, args=[callsign]).start()

def main():
    print(colorama.Fore.BLUE + "Waiting for packets..." + colorama.Style.RESET_ALL)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(("localhost", LISTENING_PORT))

        while True:
            try:
                data, addr = udp_socket.recvfrom(1024)
                packet = data.decode("utf-8")

                print(colorama.Fore.YELLOW + "Incoming packet:", packet + colorama.Style.RESET_ALL)

                cot_message, callsign = parse_packet(packet)

                print(colorama.Fore.GREEN + "Outgoing packet:", cot_message + colorama.Style.RESET_ALL)

                send_cot_message(cot_message)

                if callsign not in cot_loop:
                    cot_loop[callsign] = cot_message
                    if LOOP_ENABLED:
                        repeat(callsign)
                else:
                    print(colorama.Fore.YELLOW + "Packet with the same callsign already in loop. Dropping the old COT." + colorama.Style.RESET_ALL)
                    cot_loop[callsign] = cot_message

            except ConnectionResetError:
                print(colorama.Fore.RED + "Error: No one is listening for the message." + colorama.Style.RESET_ALL)

if __name__ == "__main__":
    main()
