# Modbus Framework
   allows for easy enumeration and 
   attack of a modbus device.
# Modbus Client Project

This project is a comprehensive Modbus client written in Python. It includes functionalities for reading, writing, scanning, and exploiting Modbus devices. The client supports both synchronous and asynchronous operations and can be used for testing and interaction with Modbus servers.

## Features

- **Read**: Read coils, discrete inputs, input registers, and holding registers.
- **Write**: Write to coils and holding registers.
- **Scan**: Scan for valid unit IDs on the Modbus network.
- **Brute Force**: Brute force function codes to test server responses.
- **Exploits**: Execute various Modbus-related exploits for testing purposes.
- **Banner Grabbing**: Retrieve the banner information from the Modbus device.

## Requirements

- Python 3.7+
- `pymodbus`
- `colorama`
- `prettytable`
- `pyreadline3`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/havokzero/modbus_probe.git
    cd modbus-client-project
    ```

2. Create a virtual environment:
    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:
    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

4. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Running the Modbus Client

To run the Modbus client, execute the `main.py` script:

```bash
python main.py
```


You will be prompted to enter the Modbus device IP address, port, and unit ID. The client then connects to the Modbus server and provides a menu for various operations:

    Read: Read data from the Modbus device.
    Write: Write data to the Modbus device.
    Scan: Scan for unit IDs on the Modbus network.
    Brute Force: Brute force function codes to test server responses.
    Exploit: Run various Modbus-related exploits.
    Exit: Exit the client.

## Example
```
Enter the Modbus device IP address: 192.168.0.10
Enter the Modbus device port (default 502): 
Enter the Modbus device unit ID (default 1): 
```

Project Structure

    main.py: The main entry point for the Modbus client.
    modbus_read.py: Contains functions for reading data from Modbus devices.
    modbus_write.py: Contains functions for writing data to Modbus devices.
    modbus_exploits.py: Contains various Modbus-related exploits.
    modbus_scan.py: Contains functions for scanning unit IDs.
    modbus_bruteforce.py: Contains functions for brute-forcing Modbus function codes.
    utils.py: Utility functions for the project.
    requirements.txt: Lists the Python dependencies.


Acknowledgments

    pymodbus: A comprehensive library for Modbus in Python.
    colorama: A library for colored terminal text.
    prettytable: A simple Python library for displaying tabular data.
    pyreadline3: A Python library for GNU readline functionality on Windows.
