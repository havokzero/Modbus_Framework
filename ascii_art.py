import os
import time
import sys
import threading
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

ascii_art = Fore.CYAN + """
███╗░░░███╗░█████╗░██████╗░██████╗░██╗░░░██╗░██████╗
████╗░████║██╔══██╗██╔══██╗██╔══██╗██║░░░██║██╔════╝
██╔████╔██║██║░░██║██║░░██║██████╦╝██║░░░██║╚█████╗░
██║╚██╔╝██║██║░░██║██║░░██║██╔══██╗██║░░░██║░╚═══██╗
██║░╚═╝░██║╚█████╔╝██████╔╝██████╦╝╚██████╔╝██████╔╝
╚═╝░░░░░╚═╝░╚════╝░╚═════╝░╚═════╝░░╚═════╝░╚═════╝░

███████╗██████╗░░█████╗░███╗░░░███╗███████╗░██╗░░░░░░░██╗░█████╗░██████╗░██╗░░██╗
██╔════╝██╔══██╗██╔══██╗████╗░████║██╔════╝░██║░░██╗░░██║██╔══██╗██╔══██╗██║░██╔╝
█████╗░░██████╔╝███████║██╔████╔██║█████╗░░░╚██╗████╗██╔╝██║░░██║██████╔╝█████═╝░
██╔══╝░░██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝░░░░████╔═████║░██║░░██║██╔══██╗██╔═██╗░
██║░░░░░██║░░██║██║░░██║██║░╚═╝░██║███████╗░░╚██╔╝░╚██╔╝░╚█████╔╝██║░░██║██║░╚██╗
╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝╚══════╝░░░╚═╝░░░╚═╝░░░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝
""" + Fore.RESET

def display_ascii_art():
    print(ascii_art)
    date_text = Fore.MAGENTA + " " * ((len(ascii_art.split('\n')[0]) - len("2024")) // 2) + "2024" + Fore.RESET
    print(date_text)

def get_terminal_size():
    try:
        columns, _ = os.get_terminal_size(0)
    except OSError:
        columns = 80  # Default to 80 if terminal size cannot be determined
    return columns

def display_moving_text(stop_event):
    text = "Made by Havok"
    width = get_terminal_size()
    while not stop_event.is_set():
        for i in range(width + len(text)):
            if stop_event.is_set():
                break
            spaces = " " * (i % (width + len(text)))
            sys.stdout.write(Fore.GREEN + "\r" + spaces + text + Fore.RESET)
            sys.stdout.flush()
            time.sleep(0.1)
        time.sleep(1)

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

if __name__ == "__main__":
    display_ascii_art()
    stop_event = threading.Event()
    t = threading.Thread(target=display_moving_text, args=(stop_event,))
    t.start()
    try:
        input()  # Wait for user to press Enter without printing prompt
    except KeyboardInterrupt:
        pass
    stop_event.set()
    t.join()
    clear_screen()
