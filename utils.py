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


def get_modbus_client(ip_address, port):
    """
    Returns a ModbusTcpClient instance.

    :param ip_address: IP address of the Modbus device
    :param port: Port number of the Modbus device
    :return: ModbusTcpClient instance
    """
    return ModbusTcpClient(ip_address, port=port)


def validate_register_type(register_type, action):
    """
    Validates the register type based on the action.

    :param register_type: Type of the register
    :param action: Action to be performed (read/write)
    :raises ValueError: If the register type is invalid
    """
    register_types = ['coils', 'discrete_inputs', 'input_registers', 'holding_registers', 'all']
    if action == 'read':
        if register_type not in register_types:
            raise ValueError(
                "Invalid register type. Must be one of: coils, discrete_inputs, input_registers, holding_registers, all")
    elif action == 'write':
        if register_type not in ['coils', 'holding_registers']:
            raise ValueError("Invalid register type. Must be one of: coils, holding_registers")


def validate_positive_integer(value, field_name):
    """
    Validates if the given value is a positive integer.

    :param value: Value to be validated
    :param field_name: Name of the field (for error message)
    :return: Integer value
    :raises ValueError: If the value is not a positive integer
    """
    try:
        ivalue = int(value)
        if ivalue < 0:
            raise ValueError
    except ValueError:
        raise ValueError(f"Invalid {field_name}. Must be a positive integer.")
    return ivalue


def prompt_for_operation_args():
    """
    Prompts the user for operation arguments and returns them.

    :return: Dictionary of operation arguments
    """
    while True:
        action = input(
            Fore.YELLOW + "Do you want to read, write, scan for unit IDs, brute force function codes, or exit? (read/write/scan/bruteforce/exit): ").strip().lower()
        if action in ['read', 'write', 'scan', 'bruteforce', 'exit']:
            break
        print(Fore.RED + "Invalid option. Please enter 'read', 'write', 'scan', 'bruteforce', or 'exit'.")

    if action == 'exit':
        return None
    elif action == 'read':
        return handle_read_action()
    elif action == 'write':
        return handle_write_action()
    elif action == 'scan':
        return {'action': action}
    elif action == 'bruteforce':
        return {'action': action}


def handle_read_action():
    """
    Handles the read action arguments.

    :return: Dictionary of read action arguments
    """
    print(Fore.GREEN + "Recommended register types: coils, discrete_inputs, input_registers, holding_registers, all")
    while True:
        try:
            register_type = input(Fore.YELLOW + "Enter register type: ").strip().lower()
            validate_register_type(register_type, 'read')
            break
        except ValueError as e:
            print(Fore.RED + str(e))

    if register_type != "all":
        read_all = input(
            Fore.YELLOW + "Do you want to read all addresses and number of registers? (yes/no): ").strip().lower()
        if read_all == 'yes':
            return {'action': 'read', 'type': register_type, 'read_all': True}
        else:
            return get_read_address_and_count(register_type)
    else:
        return {'action': 'read', 'type': register_type}


def get_read_address_and_count(register_type):
    """
    Gets the read address and count from the user.

    :param register_type: Type of the register
    :return: Dictionary of address and count
    """
    while True:
        try:
            address = validate_positive_integer(input(Fore.YELLOW + "Enter the starting address (default 0): ") or 0,
                                                "address")
            break
        except ValueError as e:
            print(Fore.RED + str(e))

    while True:
        try:
            count = validate_positive_integer(
                input(Fore.YELLOW + "Enter the number of registers to read (default 1): ") or 1, "count")
            break
        except ValueError as e:
            print(Fore.RED + str(e))

    return {'action': 'read', 'type': register_type, 'address': address, 'count': count}


def handle_write_action():
    """
    Handles the write action arguments.

    :return: Dictionary of write action arguments
    """
    print(Fore.GREEN + "Recommended register types: coils, holding_registers")
    while True:
        try:
            register_type = input(Fore.YELLOW + "Enter register type: ").strip().lower()
            validate_register_type(register_type, 'write')
            break
        except ValueError as e:
            print(Fore.RED + str(e))

    write_all = input(
        Fore.YELLOW + "Do you want to write to all addresses and number of registers? (yes/no): ").strip().lower()
    if write_all == 'yes':
        return get_write_data(register_type, True)
    else:
        return get_write_address_and_data(register_type)


def get_write_data(register_type, write_all):
    """
    Gets the write data from the user.

    :param register_type: Type of the register
    :param write_all: Boolean indicating if writing to all addresses
    :return: Dictionary of write data
    """
    data = input(
        Fore.YELLOW + "Enter the data to write (comma-separated for coils or space-separated for holding registers): ")
    if register_type == 'coils':
        try:
            values = [bool(int(val)) for val in data.split(',')]
        except ValueError:
            print(Fore.RED + "Invalid data for coils. Enter comma-separated 0 or 1 values.")
            return prompt_for_operation_args()
    else:
        values = [ord(char) for char in ' '.join(data.split())]
    return {'action': 'write', 'type': register_type, 'write_all': write_all, 'values': values}


def get_write_address_and_data(register_type):
    """
    Gets the write address and data from the user.

    :param register_type: Type of the register
    :return: Dictionary of address and data
    """
    while True:
        try:
            address = validate_positive_integer(input(Fore.YELLOW + "Enter the starting address (default 0): ") or 0,
                                                "address")
            break
        except ValueError as e:
            print(Fore.RED + str(e))

    data = input(
        Fore.YELLOW + "Enter the data to write (comma-separated for coils or space-separated for holding registers): ")
    if register_type == 'coils':
        try:
            values = [bool(int(val)) for val in data.split(',')]
        except ValueError:
            print(Fore.RED + "Invalid data for coils. Enter comma-separated 0 or 1 values.")
            return prompt_for_operation_args()
    else:
        values = [ord(char) for char in ' '.join(data.split())]
    return {'action': 'write', 'type': register_type, 'address': address, 'values': values}


def format_data(register_type, data):
    """
    Formats the data based on the register type.

    :param register_type: Type of the register
    :param data: Data to be formatted
    :return: Formatted data
    """
    if register_type in ["coils", "discrete_inputs"]:
        return [bool(bit) for bit in data]
    elif register_type in ["input_registers", "holding_registers"]:
        return data if isinstance(data, list) else [data]
    return data


def truncate_data(data, length=100):
    """
    Truncates the data to the specified length.

    :param data: Data to be truncated
    :param length: Length to truncate to
    :return: Truncated data
    """
    data_str = str(data)
    if len(data_str) > length:
        return data_str[:length] + '...'
    return data_str


def generate_filename(ip_address, command, extension):
    """
    Generates a unique filename.

    :param ip_address: IP address of the Modbus device
    :param command: Command being executed
    :param extension: File extension
    :return: Unique filename
    """
    base_filename = f"{ip_address}_{command}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    counter = 1
    directory = 'output_files'
    filename = f"{base_filename}.{extension}"
    while os.path.exists(os.path.join(directory, filename)):
        counter += 1
        filename = f"{base_filename}_{counter:02d}.{extension}"
    return os.path.join(directory, filename)


def save_data_to_csv(filename, data):
    """
    Saves data to a CSV file.

    :param filename: Name of the file
    :param data: Data to be saved
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Register Type", "Data"])
        for row in data:
            writer.writerow(row)
    print(Fore.GREEN + f"Data saved to {filename}")


def save_data_to_json(filename, data):
    """
    Saves data to a JSON file.

    :param filename: Name of the file
    :param data: Data to be saved
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    print(Fore.GREEN + f"Data saved to {filename}")


def translate_hex_values(data):
    """
    Translates hex values to ASCII characters.

    :param data: Data to be translated
    :return: Translated data
    """
    translated_data = []
    for item in data:
        register_type = item[0]
        if register_type in ['Coils', 'Discrete Inputs']:
            translated_data.append([register_type, [bool(bit) for bit in item[1]]])
        elif register_type in ['Input Registers', 'Holding Registers']:
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


def translate_modbus_response(response):
    """
    Translates Modbus response to a readable format.

    :param response: Modbus response
    :return: Translated response
    """
    if response.isError():
        return f"Error: {response}"
    if hasattr(response, 'registers'):
        return f"Register values: {response.registers}"
    elif hasattr(response, 'bits'):
        return f"Bit values: {response.bits}"
    return "No data found in response."


def decode_hex_response(hex_data):
    """
    Decodes hex data to ASCII characters.

    :param hex_data: Hex data to be decoded
    :return: Decoded data
    """
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
    """
    Prints the transaction log in a tabular format.

    :param transaction_log: Transaction log to be printed
    """
    table = PrettyTable(["Transaction", "State", "Details"])
    for log in transaction_log:
        table.add_row([log['transaction'], log['state'], log['details']])
    print(Fore.CYAN + table.get_string())
