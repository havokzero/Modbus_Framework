from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
from colorama import Fore

def write_registers(client, unit_id):
    register_type = input("Enter the register type (coils/holding_registers): ").strip().lower()

    if register_type == "coils":
        address = int(input("Enter the address to write (default 0): ").strip() or 0)
        values = input("Enter the values to write (comma-separated for coils, e.g., 1,0,1): ").strip().split(',')
        try:
            values = [bool(int(value)) for value in values]
            result = client.write_coils(address, values, unit=unit_id)
            if not result.isError():
                print(Fore.GREEN + f"Successfully wrote to coils at address {address}")
            else:
                print(Fore.RED + f"Failed to write to coils at address {address}: {result}")
        except (ValueError, ModbusIOException) as e:
            print(Fore.RED + f"Error writing to coils: {e}")

    elif register_type == "holding_registers":
        address = int(input("Enter the address to write (default 0): ").strip() or 0)
        values = input(
            "Enter the values to write (comma-separated for holding registers, e.g., 123,456): ").strip().split(',')
        try:
            values = [int(value) for value in values]
            result = client.write_registers(address, values, unit=unit_id)
            if not result.isError():
                print(Fore.GREEN + f"Successfully wrote to holding registers at address {address}")
            else:
                print(Fore.RED + f"Failed to write to holding registers at address {address}: {result}")
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter only integer values for holding registers.")
        except ModbusIOException as e:
            print(Fore.RED + f"Error writing to holding registers: {e}")

    else:
        print(Fore.RED + "Invalid register type. Please choose either 'coils' or 'holding_registers'.")

def grab_banner(client, unit_id):
    try:
        result = client.read_device_information(unit=unit_id)
        if not result.isError():
            print(Fore.GREEN + "Device Information:")
            for key, value in result.information.items():
                print(Fore.GREEN + f"{key}: {value}")
        else:
            print(Fore.RED + f"Failed to read device information: {result}")
    except ModbusIOException as e:
        print(Fore.RED + f"Error reading device information: {e}")
