import asyncio
from pymodbus.client import ModbusTcpClient
from colorama import Fore
from prettytable import PrettyTable
from utils import get_modbus_client

async def scan_id(client, unit_id, semaphore):
    async with semaphore:
        try:
            response = client.read_coils(0, 1, unit=unit_id)
            if not response.isError():
                return unit_id
        except Exception as e:
            pass
    return None

async def scan_unit_ids_async(ip, port):
    client = get_modbus_client(ip, port)
    client.connect()
    semaphore = asyncio.Semaphore(10000)  # Adjust concurrency limit as needed
    tasks = [scan_id(client, unit_id, semaphore) for unit_id in range(1, 256)]
    results = await asyncio.gather(*tasks)
    client.close()
    return [unit_id for unit_id in results if unit_id is not None]

def scan_unit_ids(ip, port):
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
