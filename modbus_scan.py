import asyncio
from pymodbus.client import ModbusTcpClient
from colorama import Fore
from prettytable import PrettyTable
from utils import get_modbus_client


async def scan_id(client, unit_id, semaphore):
    """
    Scan a single unit ID to check if it is valid.

    :param client: ModbusTcpClient instance
    :param unit_id: Unit ID to scan
    :param semaphore: Semaphore for limiting concurrency
    :return: Unit ID if valid, else None
    """
    async with semaphore:
        try:
            response = client.read_coils(0, 1, unit=unit_id)
            if not response.isError():
                return unit_id
        except Exception:
            pass
    return None


async def scan_unit_ids_async(ip, port, max_unit_id=248):   #original value 247
    """
    Asynchronously scan for valid unit IDs on the Modbus device.

    :param ip: IP address of the Modbus device
    :param port: Port of the Modbus device
    :param max_unit_id: Maximum unit ID to scan
    :return: List of valid unit IDs
    """
    client = get_modbus_client(ip, port)
    if not client.connect():
        print(Fore.RED + "Failed to connect to Modbus server.")
        return []

    semaphore = asyncio.Semaphore(1000)  # Adjust concurrency limit as needed
    tasks = [scan_id(client, unit_id, semaphore) for unit_id in range(1, max_unit_id + 1)]
    results = await asyncio.gather(*tasks)
    client.close()
    return [unit_id for unit_id in results if unit_id is not None]


def scan_unit_ids(ip, port):
    """
    Scan for valid unit IDs on the Modbus device and display them.

    :param ip: IP address of the Modbus device
    :param port: Port of the Modbus device
    """
    print(Fore.YELLOW + "Scanning for unit IDs...")
    loop = asyncio.get_event_loop()
    unit_ids = loop.run_until_complete(scan_unit_ids_async(ip, port))

    if unit_ids:
        table = PrettyTable(["Unit ID"])
        for unit_id in unit_ids:
            table.add_row([unit_id])
        print(Fore.CYAN + table.get_string())
    else:
        print(Fore.RED + "No unit IDs found.")
