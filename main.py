import argparse
import signal
import time
import os
from threading import Thread, Event
from modbus_read import read_registers, read_all_data, read_messages, grab_banner
from modbus_write import write_registers, set_random_unit_id, set_custom_banner
from modbus_exploits import run_exploits
from modbus_scan import scan_unit_ids
from modbus_bruteforce import brute_force_function_codes
from colorama import init, Fore
from utils import get_modbus_client
from ascii_art import display_ascii_art, display_moving_text, clear_screen

# Initialize colorama
init(autoreset=True)

# Use pyreadline3 on Windows
if os.name == 'nt':
    import pyreadline3 as readline
else:
    import readline

def completer(text, state):
    options = [i for i in ['read', 'write', 'scan', 'bruteforce', 'exploit', 'exit', 'registers', 'all', 'messages', 'banner', 'random_unit_id', 'custom_banner', 'motd'] if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

if os.name == 'nt':
    readline.Readline().set_completer(completer)
else:
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

def signal_handler(signal, frame):
    print(Fore.YELLOW + "\nInterrupt received. Returning to main menu.")
    return_to_main_menu()

def return_to_main_menu():
    global stop_event, moving_text_thread
    stop_event.set()
    moving_text_thread.join()  # Ensure the thread has stopped
    operation = input("\nDo you want to read, write, scan for unit IDs, brute force function codes, run exploits, set random unit ID, set custom banner, or view MOTD? (read/write/scan/bruteforce/exploit/random_unit_id/custom_banner/motd/exit): ").strip().lower()
    if operation == 'exit':
        print("Exiting program.")
        exit(0)
    elif operation == 'motd':
        display_ascii_art()
    else:
        client = get_modbus_client(args.ip, args.port)
        if not client.connect():
            print(Fore.RED + "Failed to connect to Modbus server.")
            return
        if operation == 'read':
            read_option = input("Do you want to read registers, all data, messages, or banner? (registers/all/messages/banner): ").strip().lower()
            if read_option == 'registers':
                read_registers(client, args.unit)
            elif read_option == 'all':
                read_all_data(client, args.unit, args.ip)
            elif read_option == 'messages':
                read_messages(client, args.unit, args.ip)
            elif read_option == 'banner':
                grab_banner(client, args.unit, args.ip)
        elif operation == 'write':
            write_registers(client, args.unit)
        elif operation == 'scan':
            scan_unit_ids(args.ip, args.port)
        elif operation == 'bruteforce':
            brute_force_function_codes(args.ip, args.port, args.unit)
        elif operation == 'exploit':
            run_exploits(args.ip, args.port, args.unit)
        elif operation == 'random_unit_id':
            set_random_unit_id(client)
        elif operation == 'custom_banner':
            set_custom_banner(client, args.unit)
        client.close()
    start_moving_text()

def start_moving_text():
    global stop_event, moving_text_thread
    stop_event = Event()
    moving_text_thread = Thread(target=display_moving_text, args=(stop_event,))
    moving_text_thread.start()

def main():
    global args, stop_event, moving_text_thread
    parser = argparse.ArgumentParser(description="Modbus Client Script")
    parser.add_argument('--ip', type=str, help="Modbus device IP address")
    parser.add_argument('--port', type=int, help="Modbus device port (default: 502)")
    parser.add_argument('--unit', type=int, help="Modbus device unit ID (default: 1)")
    args = parser.parse_args()

    display_ascii_art()
    start_moving_text()

    input()  # Wait for user to press Enter without printing prompt
    stop_event.set()
    moving_text_thread.join()
    clear_screen()  # Clear the screen after pressing Enter

    if not args.ip:
        args.ip = input("Enter the Modbus device IP address: ")

    if not args.port:
        args.port = int(input("Enter the Modbus device port (default 502): ") or 502)

    if not args.unit:
        args.unit = int(input("Enter the Modbus device unit ID (default 1): ") or 1)

    client = get_modbus_client(args.ip, args.port)
    if not client.connect():
        print(Fore.RED + "Failed to connect to Modbus server.")
        return

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        return_to_main_menu()

if __name__ == "__main__":
    main()
