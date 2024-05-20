import argparse
from modbus_read import read_registers, read_all_data, read_messages, grab_banner, probe_device
from modbus_write import write_registers
from modbus_exploits import run_exploits
from modbus_scan import scan_unit_ids
from modbus_bruteforce import brute_force_function_codes
from colorama import init, Fore
from utils import get_modbus_client
import os

# Initialize colorama
init(autoreset=True)

# Use pyreadline3 on Windows
if os.name == 'nt':
    import pyreadline3 as readline
else:
    import readline

def completer(text, state):
    options = [i for i in ['read', 'write', 'scan', 'bruteforce', 'exploit', 'exit', 'registers', 'all', 'messages', 'banner'] if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

if os.name == 'nt':
    readline.Readline().set_completer(completer)
else:
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

def main():
    parser = argparse.ArgumentParser(description="Modbus Client Script")
    parser.add_argument('--ip', type=str, help="Modbus device IP address")
    parser.add_argument('--port', type=int, help="Modbus device port (default: 502)")
    parser.add_argument('--unit', type=int, help="Modbus device unit ID (default: 1)")
    args = parser.parse_args()

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

    address_ranges = probe_device(client, args.unit)
    client.close()

    while True:
        operation = input("Do you want to read, write, scan for unit IDs, brute force function codes, or run exploits? (read/write/scan/bruteforce/exploit/exit): ").strip().lower()
        if operation == 'exit':
            print("Exiting program.")
            break
        elif operation == 'read':
            read_option = input("Do you want to read registers, all data, or messages? (registers/all/messages/banner): ").strip().lower()
            client = get_modbus_client(args.ip, args.port)
            if not client.connect():
                print(Fore.RED + "Failed to connect to Modbus server.")
                continue
            if read_option == 'registers':
                read_registers(client, args.unit, address_ranges)
            elif read_option == 'all':
                read_all_data(client, args.unit, args.ip)
            elif read_option == 'messages':
                read_messages(client, args.unit, args.ip)
            elif read_option == 'banner':
                grab_banner(client, args.unit, args.ip)
            client.close()
        elif operation == 'write':
            client = get_modbus_client(args.ip, args.port)
            if not client.connect():
                print(Fore.RED + "Failed to connect to Modbus server.")
                continue
            write_registers(client, args.unit)
            client.close()
        elif operation == 'scan':
            scan_unit_ids(args.ip, args.port)
        elif operation == 'bruteforce':
            brute_force_function_codes(args.ip, args.port, args.unit)
        elif operation == 'exploit':
            run_exploits(args.ip, args.port, args.unit)
        else:
            print(Fore.RED + "Invalid option. Please choose a valid action.")

if __name__ == "__main__":
    main()
