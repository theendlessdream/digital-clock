from datetime import datetime
import time
import spidev

# Initialize SPI
spi = spidev.SpiDev()
# wait because when the PI is starting it seems to take a while to be
# available
while True:
    try:
       spi.open(0, 0)  # Open SPI bus 0, device 0
       break
    except (FileNotFoundError, PermissionError):
       time.sleep(1)
spi.max_speed_hz = 50000  # Set SPI speed

# Define segment mappings for a 7-segment display
#  _a_
# f   b
# |_g_|
# e   c
# |_d_|
#
#          .bcdegfa
SEGMENTS = {
    '0': 0b01111011,
    '1': 0b01100000,
    '2': 0b01011101,
    '3': 0b01110101,
    '4': 0b01100110,
    '5': 0b00110111,
    '6': 0b00111111,
    '7': 0b01100001,
    '8': 0b01111111,
    '9': 0b01110111,
    ' ': 0b00000000,  # Blank
}

# Helper function to send data to the TPIC6C596 ICs
def send_data(data):
    spi.xfer2(data)

# Function to update the clock display
def update_display(hour, minute, colon_on):
    data = [0x00] * 4  # Four bytes, one for each driver

    # Hour tens and ones
    data[0] = SEGMENTS[hour[0]] if hour[0] != ' ' else 0x00
    data[1] = SEGMENTS[hour[1]] if hour[1] != ' ' else 0x00

    # Minute tens and ones
    data[2] = SEGMENTS[minute[0]]
    data[3] = SEGMENTS[minute[1]]

    # Control the colon using decimal points of the second and third drivers
    if colon_on:
        data[1] |= 0b10000000  # Set DP bit for driver 2
        data[2] |= 0b10000000  # Set DP bit for driver 3

    send_data(data[::-1])  # Send data in reverse order (last driver first)

# Main loop
def main():
    try:
        while True:
            now = datetime.now()
            hour = now.strftime("%H")
            minute = now.strftime("%M")
            current_microsecond = now.microsecond

            # Calculate sleep time until the next target (0 or 500,000 microseconds)
            if current_microsecond < 500_000:
                sleep_time = (500_000 - current_microsecond) / 1_000_000
                colon_on = True
            else:
                sleep_time = (1_000_000 - current_microsecond) / 1_000_000
                colon_on = False

            update_display(hour, minute, colon_on)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        spi.close()

if __name__ == "__main__":
    main()

