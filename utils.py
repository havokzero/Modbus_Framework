import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from colorama import init, Fore, Style
import os
import csv
import json
from datetime import datetime
from prettytable import PrettyTable

# Initialize colorama
init(autoreset=True)

# Custom logging handler for colorized output
class ColorizingStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            message = self.format(record)
            if "RECV:" in message or "Processing:" in message:
                message = Fore.GREEN + message + Style.RESET_ALL
            elif "Changing transaction state" in message or "TRANSACTION_COMPLETE" in message or "Factory Response" in message:
                message = Fore.CYAN + message + Style.RESET_ALL
            elif "Frame check, no more data!" in message:
                message = Fore.RED + message + Style.RESET_ALL
            else:
                message = message
            self.stream.write(message + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = ColorizingStreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Get Modbus client
def get_modbus_client(ip_address, port):
    return ModbusTcpClient(ip_address, port=port)

# Validate register type
def validate_register_type(register_type, action):
    register_types = ['coils', 'discrete_inputs', 'input_registers', 'holding_registers', 'all']
    if action == 'read':
        if register_type not in register_types:
            raise ValueError("Invalid register type. Must be one of: coils, discrete_inputs, input_registers, holding_registers, all")
    elif action == 'write':
        if register_type not in ['coils', 'holding_registers']:
            raise ValueError("Invalid register type. Must be one of: coils, holding_registers")

# Validate positive integer
def validate_positive_integer(value, field_name):
    try:
        ivalue = int(value)
        if ivalue < 0:
            raise ValueError
    except ValueError:
        raise ValueError(f"Invalid {field_name}. Must be a positive integer.")
    return ivalue

# Prompt for operation arguments
def prompt_for_operation_args():
    while True:
        action = input(Fore.YELLOW + "Do you want to read, write, scan for unit IDs, brute force function codes, or exit? (read/write/scan/bruteforce/exit): ").strip().lower()
        if action in ['read', 'write', 'scan', 'bruteforce', 'exit']:
            break
        print(Fore.RED + "Invalid option. Please enter 'read', 'write', 'scan', 'bruteforce', or 'exit'.")

    if action == 'exit':
        return None
    elif action == 'read':
        print(Fore.GREEN + "Recommended register types: coils, discrete_inputs, input_registers, holding_registers, all")
        while True:
            try:
                register_type = input(Fore.YELLOW + "Enter register type: ").strip().lower()
                validate_register_type(register_type, action)
                break
            except ValueError as e:
                print(Fore.RED + str(e))

        if register_type != "all":
            read_all = input(Fore.YELLOW + "Do you want to read all addresses and number of registers? (yes/no): ").strip().lower()
            if read_all == 'yes':
                return {'action': action, 'type': register_type, 'read_all': True}
            else:
                while True:
                    try:
                        address = validate_positive_integer(input(Fore.YELLOW + "Enter the starting address (default 0): ") or 0, "address")
                        break
                    except ValueError as e:
                        print(Fore.RED + str(e))

                while True:
                    try:
                        count = validate_positive_integer(input(Fore.YELLOW + "Enter the number of registers to read (default 1): ") or 1, "count")
                        break
                    except ValueError as e:
                        print(Fore.RED + str(e))

                return {'action': action, 'type': register_type, 'address': address, 'count': count}
        else:
            return {'action': action, 'type': register_type}

    elif action == 'write':
        print(Fore.GREEN + "Recommended register types: coils, holding_registers")
        while True:
            try:
                register_type = input(Fore.YELLOW + "Enter register type: ").strip().lower()
                validate_register_type(register_type, action)
                break
            except ValueError as e:
                print(Fore.RED + str(e))

        write_all = input(Fore.YELLOW + "Do you want to write to all addresses and number of registers? (yes/no): ").strip().lower()
        if write_all == 'yes':
            data = input(Fore.YELLOW + "Enter the data to write (comma-separated for coils or space-separated for holding registers): ")
            if register_type == 'coils':
                try:
                    values = [bool(int(val)) for val in data.split(',')]
                except ValueError:
                    print(Fore.RED + "Invalid data for coils. Enter comma-separated 0 or 1 values.")
                    return prompt_for_operation_args()
            else:
                values = [ord(char) for char in ' '.join(data.split())]
            return {'action': action, 'type': register_type, 'write_all': True, 'values': values}
        else:
            while True:
                try:
                    address = validate_positive_integer(input(Fore.YELLOW + "Enter the starting address (default 0): ") or 0, "address")
                    break
                except ValueError as e:
                    print(Fore.RED + str(e))

            data = input(Fore.YELLOW + "Enter the data to write (comma-separated for coils or space-separated for holding registers): ")
            if register_type == 'coils':
                try:
                    values = [bool(int(val)) for val in data.split(',')]
                except ValueError:
                    print(Fore.RED + "Invalid data for coils. Enter comma-separated 0 or 1 values.")
                    return prompt_for_operation_args()
            else:
                values = [ord(char) for char in ' '.join(data.split())]

            return {'action': action, 'type': register_type, 'address': address, 'values': values}

    elif action == 'scan':
        return {'action': action}

    elif action == 'bruteforce':
        return {'action': action}

# Format data
def format_data(register_type, data):
    if register_type == "coils" or register_type == "discrete_inputs":
        return [bool(bit) for bit in data]
    elif register_type == "input_registers" or register_type == "holding_registers":
        if isinstance(data, list):
            return data
        return [data]
    return data

# Truncate data
def truncate_data(data, length=100):
    data_str = str(data)
    if len(data_str) > length:
        return data_str[:length] + '...'
    return data_str

# Generate filename
def generate_filename(ip_address, command, extension):
    base_filename = f"{ip_address}_{command}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    counter = 1
    directory = 'output_files'
    filename = f"{base_filename}.{extension}"
    while os.path.exists(os.path.join(directory, filename)):
        counter += 1
        filename = f"{base_filename}_{counter:02d}.{extension}"
    return os.path.join(directory, filename)

# Save data to CSV
def save_data_to_csv(filename, data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Register Type", "Data"])
        for row in data:
            writer.writerow(row)
    print(Fore.GREEN + f"Data saved to {filename}")

# Save data to JSON
def save_data_to_json(filename, data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    print(Fore.GREEN + f"Data saved to {filename}")

# Translate hex values
def translate_hex_values(data):
    translated_data = []
    for item in data:
        register_type = item[0]
        if register_type in ['Coils', 'Discrete Inputs']:
            translated_data.append([register_type, [bool(bit) for bit in item[1]]])
        elif register_type == 'Input Registers' or register_type == 'Holding Registers':
            translated_values = []
            for val in item[1]:
                if isinstance(val, int):
                    translated_values.append(chr(val))
                else:
                    try:
                        translated_values.append(decode_hex_response(val))
                    except ValueError:
                        translated_values.append(f"Invalid data: {val}")
            translated_data.append([register_type, translated_values])
    return translated_data

# Translate Modbus response
def translate_modbus_response(response):
    if response.isError():
        return f"Error: {response}"
    if hasattr(response, 'registers'):
        return f"Register values: {response.registers}"
    elif hasattr(response, 'bits'):
        return f"Bit values: {response.bits}"
    return "No data found in response."

# Decode hex response
def decode_hex_response(hex_data):
    if isinstance(hex_data, int):
        return chr(hex_data)
    if hex_data.startswith("0x"):
        hex_data = hex_data[2:]
    try:
        bytes_data = bytes.fromhex(hex_data)
        return bytes_data.decode('utf-8', errors='ignore')
    except ValueError as e:
        return f"Unable to decode hex data: {e}"

def print_transaction_log(transaction_log):
    table = PrettyTable(["Transaction", "State", "Details"])
    for log in transaction_log:
        table.add_row([log['transaction'], log['state'], log['details']])
    print(Fore.CYAN + table.get_string())
