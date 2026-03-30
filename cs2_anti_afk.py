import uinput
import time

# Define the virtual keyboard/mouse
device = uinput.UInput()

# Example function that uses the uinput device

def move_mouse_and_type():
    # Move mouse to (100, 100)
    device.emit(uinput.EV_REL, uinput.REL_X, 100)
    device.emit(uinput.EV_REL, uinput.REL_Y, 100)
    device.emit(uinput.EV_KEY, uinput.KEY_A, 1)  # Press 'A'
    device.emit(uinput.EV_KEY, uinput.KEY_A, 0)  # Release 'A'

# Main loop
def main():
    while True:
        move_mouse_and_type()
        time.sleep(1)

if __name__ == '__main__':
    main()