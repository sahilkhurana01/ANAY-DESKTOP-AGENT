import pyautogui
import time

def get_mouse_position():
    print("--- MOUSE POSITION TRACKER ---")
    print("Move your mouse to the target element.")
    print("Recording starts in 3 seconds...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    
    x, y = pyautogui.position()
    print(f"\nSUCCESS! Coordinates:")
    print(f"X: {x}, Y: {y}")
    print(f"\nYou can now tell ANAY: 'Click at {x}, {y}'")

if __name__ == "__main__":
    get_mouse_position()
