from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from colorama import Fore
from prettytable import PrettyTable
from utils import get_modbus_client

def brute_force_function_codes(ip, port, unit_id):
    """
    Attempt to brute-force Modbus function codes on the specified device.

    :param ip: IP address of the Modbus device
    :param port: Port of the Modbus device
    :param unit_id: Unit ID of the Modbus device
    """
    client = get_modbus_client(ip, port)
    if not client.connect():
        print(Fore.RED + "Failed to connect to Modbus server.")
        return

    table = PrettyTable(["Function Code", "Status"])

    function_codes = {
        1: lambda: client.read_coils(0, 1, unit=unit_id),
        2: lambda: client.read_discrete_inputs(0, 1, unit=unit_id),
        3: lambda: client.read_holding_registers(0, 1, unit=unit_id),
        4: lambda: client.read_input_registers(0, 1, unit=unit_id),
        5: lambda: client.write_coil(0, True, unit=unit_id),
        6: lambda: client.write_register(0, 1, unit=unit_id),
        15: lambda: client.write_coils(0, [True] * 8, unit=unit_id),
        16: lambda: client.write_registers(0, [1] * 8, unit=unit_id),
        43: lambda: client.read_device_information(unit=unit_id)
    }

    for function_code in range(1, 256):
        try:
            if function_code in function_codes:
                response = function_codes[function_code]()
                status = "Success" if not response.isError() else "Error"
                table.add_row([function_code, Fore.GREEN + status if status == "Success" else Fore.RED + status])
            else:
                table.add_row([function_code, Fore.YELLOW + "Not Implemented"])
        except ModbusException as e:
            table.add_row([function_code, Fore.RED + f"ModbusException: {str(e)}"])
        except Exception as e:
            table.add_row([function_code, Fore.RED + f"Failed: {str(e)}"])

    client.close()
    print(Fore.CYAN + table.get_string())
