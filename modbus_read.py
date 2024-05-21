import asyncio
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from colorama import Fore
from utils import format_data, translate_hex_values, translate_modbus_response, save_data_to_csv, save_data_to_json, generate_filename, truncate_data
from prettytable import PrettyTable

def probe_device(client, unit_id):
    address_ranges = {
        'coils': 0,
        'discrete_inputs': 0,
        'input_registers': 0,
        'holding_registers': 0
    }

    try:
        coils_response = client.read_coils(0, 1, unit=unit_id)
        if not coils_response.isError():
            address_ranges['coils'] = len(coils_response.bits)

        discrete_inputs_response = client.read_discrete_inputs(0, 1, unit=unit_id)
        if not discrete_inputs_response.isError():
            address_ranges['discrete_inputs'] = len(discrete_inputs_response.bits)

        input_registers_response = client.read_input_registers(0, 1, unit=unit_id)
        if not input_registers_response.isError():
            address_ranges['input_registers'] = len(input_registers_response.registers)

        holding_registers_response = client.read_holding_registers(0, 1, unit=unit_id)
        if not holding_registers_response.isError():
            address_ranges['holding_registers'] = len(holding_registers_response.registers)

    except ModbusException as e:
        print(Fore.RED + f"Probing failed: {e}")

    return address_ranges

async def scan_unit_id(client, unit_id):
    try:
        response = client.read_holding_registers(0, 1, unit=unit_id)
        if not response.isError():
            return unit_id
    except Exception:
        return None

async def scan_unit_ids(client):
    print(Fore.YELLOW + "Scanning for unit IDs...")
    tasks = []
    semaphore = asyncio.Semaphore(100)

    async def limited_scan(unit_id):
        async with semaphore:
            return await scan_unit_id(client, unit_id)

    for unit_id in range(1, 248):
        tasks.append(limited_scan(unit_id))

    results = await asyncio.gather(*tasks)
    valid_ids = [result for result in results if result is not None]

    table = PrettyTable(["Unit ID"])
    table.align["Unit ID"] = "l"
    for unit_id in valid_ids:
        table.add_row([unit_id])

    print(Fore.CYAN + table.get_string())

def read_registers(client, unit_id):
    register_type = input("Enter the register type (coils/discrete_inputs/input_registers/holding_registers/all): ").strip().lower()
    address = input(f"Enter the address to read (default 0): ").strip()
    count = input(f"Enter the number of registers to read (default 1): ").strip()

    address = int(address) if address else 0
    count = int(count) if count else 1

    response = None
    if register_type == "coils":
        response = client.read_coils(address, count, unit=unit_id)
    elif register_type == "discrete_inputs":
        response = client.read_discrete_inputs(address, count, unit=unit_id)
    elif register_type == "input_registers":
        response = client.read_input_registers(address, count, unit=unit_id)
    elif register_type == "holding_registers":
        response = client.read_holding_registers(address, count, unit=unit_id)
    elif register_type == "all":
        read_all_data(client, unit_id, client.host)
        return
    else:
        print(Fore.RED + "Invalid register type")
        return

    if not response.isError():
        table = PrettyTable(["Address", "Value"])
        for i, value in enumerate(response.bits if register_type in ['coils', 'discrete_inputs'] else response.registers):
            table.add_row([address + i, value])
        print(Fore.CYAN + table.get_string())
    else:
        print(Fore.RED + f"Failed to read {register_type}. Error: {response}")

def read_all_data(client, unit_id, ip_address):
    print(Fore.YELLOW + "Reading all data from Modbus device...")
    try:
        # Read Coils
        coils_response = client.read_coils(0, 2000, unit=unit_id)
        coils_data = format_data('coils', coils_response.bits if not coils_response.isError() else "Error reading coils")

        # Read Discrete Inputs
        discrete_inputs_response = client.read_discrete_inputs(0, 2000, unit=unit_id)
        discrete_inputs_data = format_data('discrete_inputs', discrete_inputs_response.bits if not discrete_inputs_response.isError() else "Error reading discrete inputs")

        # Read Input Registers
        input_registers_response = client.read_input_registers(0, 125, unit=unit_id)
        input_registers_data = format_data('input_registers', input_registers_response.registers if not input_registers_response.isError() else "Error reading input registers")

        # Read Holding Registers
        holding_registers_response = client.read_holding_registers(0, 125, unit=unit_id)
        holding_registers_data = format_data('holding_registers', holding_registers_response.registers if not holding_registers_response.isError() else "Error reading holding registers")

        # Display data in human-readable format
        table = PrettyTable(["Register Type", "Data"])
        table.align["Register Type"] = "l"
        table.align["Data"] = "l"
        table.max_width = {"Data": 1000}
        table.add_row(["Coils", truncate_data(coils_data, 1000)])
        table.add_row(["Discrete Inputs", truncate_data(discrete_inputs_data, 1000)])
        table.add_row(["Input Registers", truncate_data(input_registers_data, 1000)])
        table.add_row(["Holding Registers", truncate_data(holding_registers_data, 1000)])

        print(Fore.CYAN + table.get_string())

        # Save data to CSV and JSON
        data = [
            ["Coils", coils_data],
            ["Discrete Inputs", discrete_inputs_data],
            ["Input Registers", input_registers_data],
            ["Holding Registers", holding_registers_data]
        ]

        csv_filename = generate_filename(ip_address, 'read_all', 'csv')
        json_filename = generate_filename(ip_address, 'read_all', 'json')

        save_data_to_csv(csv_filename, data)
        save_data_to_json(json_filename, data)

        # Translate hex values to English values
        translated_data = translate_hex_values(data)
        table = PrettyTable(["Register Type", "Translated Data"])
        table.align["Register Type"] = "l"
        table.align["Translated Data"] = "l"
        table.max_width = {"Translated Data": 1000}
        for item in translated_data:
            table.add_row([item[0], truncate_data(item[1], 1000)])

        print(Fore.CYAN + "Translated Data:")
        print(table)

        translated_json_filename = generate_filename(ip_address, 'read_all_translated', 'json')
        save_data_to_json(translated_json_filename, translated_data)

    except ModbusException as e:
        print(Fore.RED + f"Failed to read all data: {e}")

def read_messages(client, unit_id, ip_address):
    print(Fore.YELLOW + "Reading messages from Modbus device...")
    try:
        response = client.read_holding_registers(0, 125, unit=unit_id)
        if not response.isError():
            table = PrettyTable(["Register Type", "Value"])
            table.add_row(["Holding Registers", translate_modbus_response(response)])
            print(Fore.CYAN + table.get_string())
            print(Fore.CYAN + "----------------------------------------")
            print(Fore.CYAN + f"Hex data: {response}")
        else:
            print(Fore.RED + f"Error reading messages: {response}")
    except ModbusException as e:
        print(Fore.RED + f"Failed to read messages: {e}")

def grab_banner(client, unit_id, ip_address):
    print(Fore.YELLOW + "Grabbing banner from Modbus device...")
    try:
        packet = b"\x00\x00\x00\x00\x00\x06\xff\x2b\x0e\x03\x00"
        client.socket.send(packet)
        data = client.socket.recv(1024)

        if data:
            print(Fore.CYAN + "Banner data received:")
            if len(data) > 13:  # Check if data length is sufficient
                parse_banner(data)
                banner_filename = generate_filename(ip_address, 'banner', 'txt')
                with open(banner_filename, 'w') as file:
                    file.write(data.decode('utf-8', errors='ignore'))
                print(Fore.GREEN + f"Banner saved to {banner_filename}")
            else:
                print(Fore.RED + "Received banner data is too short to be valid.")
        else:
            print(Fore.RED + "No banner data received.")
    except ModbusException as e:
        print(Fore.RED + f"Failed to grab banner: {e}")
    except Exception as e:
        print(Fore.RED + f"Unexpected error occurred: {e}")

def parse_banner(data):
    object_name = {
        0: 'VendorName',
        1: 'ProductCode',
        2: 'Revision',
        3: 'VendorUrl',
        4: 'ProductName',
        5: 'ModelName',
        6: 'UserAppName',
        128: 'PrivateObjects',
        255: 'PrivateObjects'
    }

    try:
        num_objects = data[13]
        print(f"Number of Objects: {num_objects}")

        object_start = 14
        for _ in range(num_objects):
            object_id = data[object_start]
            object_len = data[object_start + 1]
            object_str_value = data[object_start + 2:object_start + 2 + object_len].decode('utf-8', errors='ignore')
            object_name_str = object_name.get(object_id, 'Unknown')
            print(f"{object_name_str}: {object_str_value}")
            object_start += 2 + object_len
    except IndexError:
        print(Fore.RED + "Banner data is not in the expected format.")
    except Exception as e:
        print(Fore.RED + f"Error parsing banner: {e}")

def read_coils(client, unit_id):
    """
    Function to read coils from a Modbus device.

    :param client: ModbusTcpClient object
    :param unit_id: Unit ID of the Modbus device
    """
    try:
        address = int(input("Enter the address to read coils (default 0): ").strip() or 0)
        count = int(input("Enter the number of coils to read (default 1): ").strip() or 1)

        response = client.read_coils(address, count, unit=unit_id)
        if not response.isError():
            table = PrettyTable(["Address", "Value"])
            for i, value in enumerate(response.bits):
                table.add_row([address + i, value])
            print(Fore.CYAN + table.get_string())
        else:
            print(Fore.RED + f"Failed to read coils. Error: {response}")

    except ValueError:
        print(Fore.RED + "Invalid input. Please enter a valid address and number of coils.")
    except ModbusException as e:
        print(Fore.RED + f"Error reading coils: {e}")
