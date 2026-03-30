import uinput
import time

# Define the events you want to simulate
events = [
    uinput.KEY_A,
    uinput.KEY_B,
    uinput.KEY_C,
]

# Start uinput device
with uinput.UInput() as device:
    try:
        while True:
            for event in events:
                device.emit(event, 1)  # Press the key
                time.sleep(0.1)         # Wait for 100 ms
                device.emit(event, 0)  # Release the key
                time.sleep(2)           # Wait for 2 seconds before the next key
    except KeyboardInterrupt:
        print("Exiting...")