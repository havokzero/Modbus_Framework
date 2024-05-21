# modbus_write.py

from pymodbus.client.tcp import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException, ModbusException
from colorama import Fore
import random


def write_registers(client, unit_id):
    register_type = input("Enter the register type (coils/holding_registers): ").strip().lower()

    if register_type == "coils":
        try:
            address = int(input("Enter the address to write (default 0): ").strip() or 0)
            values = [bool(int(value)) for value in
                      input("Enter the values to write (comma-separated for coils, e.g., 1,0,1): ").strip().split(',')]
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a valid address and comma-separated 0 or 1 values for coils.")
            return

        try:
            result = client.write_coils(address, values, unit=unit_id)
            if not result.isError():
                print(Fore.GREEN + f"Successfully wrote to coils at address {address}")
            else:
                print(Fore.RED + f"Failed to write to coils at address {address}: {result}")
        except ModbusIOException as e:
            print(Fore.RED + f"Error writing to coils: {e}")

    elif register_type == "holding_registers":
        try:
            address = int(input("Enter the address to write (default 0): ").strip() or 0)
            values_input = input(
                "Enter the values to write (comma-separated for holding registers, e.g., 123,456 or text): ").strip()

            # Convert text input to ASCII integer values
            if any(c.isalpha() for c in values_input):
                values = [ord(char) for char in values_input]
            else:
                values = [int(value) for value in values_input.split(',')]

        except ValueError:
            print(
                Fore.RED + "Invalid input. Please enter a valid address and comma-separated integer values for holding registers.")
            return

        try:
            result = client.write_registers(address, values, unit=unit_id)
            if not result.isError():
                print(Fore.GREEN + f"Successfully wrote to holding registers at address {address}")
            else:
                print(Fore.RED + f"Failed to write to holding registers at address {address}: {result}")
        except ModbusIOException as e:
            print(Fore.RED + f"Error writing to holding registers: {e}")
        except ModbusException as e:
            print(Fore.RED + f"ModbusException: {e}")

    else:
        print(Fore.RED + "Invalid register type. Please choose either 'coils' or 'holding_registers'.")


def set_random_unit_id(client):
    try:
        unit_id = random.randint(1, 247)
        result = client.write_register(0, unit_id)
        if not result.isError():
            print(Fore.GREEN + f"Successfully set random unit ID to {unit_id}")
        else:
            print(Fore.RED + f"Failed to set random unit ID: {result}")
    except ModbusIOException as e:
        print(Fore.RED + f"Error setting random unit ID: {e}")


def set_custom_banner(client, unit_id):
    try:
        banner = input("Enter the custom banner to set: ")
        values = [ord(char) for char in banner]
        address = 0  # Define the appropriate address for banner
        result = client.write_registers(address, values, unit=unit_id)
        if not result.isError():
            print(Fore.GREEN + f"Successfully set custom banner for unit ID {unit_id}")
        else:
            print(Fore.RED + f"Failed to set custom banner: {result}")
    except ModbusIOException as e:
        print(Fore.RED + f"Error setting custom banner: {e}")
    except ModbusException as e:
        print(Fore.RED + f"ModbusException: {e}")


# Example usage
if __name__ == "__main__":
    client = ModbusTcpClient('127.0.0.1', port=502)
    if client.connect():
        set_random_unit_id(client)
        set_custom_banner(client, 1)
        client.close()
    else:
        print("Failed to connect to Modbus server.")
