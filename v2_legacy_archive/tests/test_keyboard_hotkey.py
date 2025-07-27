import keyboard
import time

print("Testing keyboard hotkey functionality...")
print("Press F4 to trigger test, Ctrl+C to quit")

def on_f4():
    print("F4 PRESSED! Hotkey is working!")

keyboard.add_hotkey('f4', on_f4)
print("Hotkey registered. Waiting for F4...")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nExiting...")