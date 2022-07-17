# dBmonster - Track WiFi devices with their signal strength in dBm
# by 90N45 - github.com/90N45-d3v
# Mostly not testet at linux, but works stable on MacOS and should work on Linux too

import os
from sys import platform
from itertools import count
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.animation import FuncAnimation

x_values = []
y_values = []
index = count() # x axis is count of dBm values

fig = plt.gcf()

### functions

def banner():
	print("\033[38;5;27m" + "\n _(`-')    <-.(`-')  <-. (`-')             <-. (`-')_  (`-').-> (`-')       (`-')  _    (`-')  \n( (OO ).->  __( OO)     \\(OO )_      .->      \\( OO) ) ( OO)_   ( OO).->    ( OO).-/ <-.(OO )  \n\\    .'_  '-'---.\\  ,--./  ,-.)(`-')----. ,--./ ,--/ (_)--\\_)  /    '._   (,------. ,------,) \n'`'-..__) | .-. (/  |   `.'   |( OO).-.  '|   \\ |  | /    _ /  |'--...__)  |  .---' |   /`. ' \n|  |  ' | | '-' `.) |  |'.'|  |( _) | |  ||  . '|  |)\\_..`--.  `--.  .--' (|  '--.  |  |_.' | \n|  |  / : | /`'.  | |  |   |  | \\|  |)|  ||  |\\    | .-._)   \\    |  |     |  .--'  |  .   .' \n|  '-'  / | '--'  / |  |   |  |  '  '-'  '|  | \\   | \\       /    |  |     |  `---. |  |\\  \\  \n`------'  `------'  `--'   `--'   `-----' `--'  `--'  `-----'     `--'     `------' `--' '--'" + "\033[38;5;172m" + "\nby github.com/90N45-d3v" + "\033[39m")

def set_channel(): # Change channel on your WiFi card
	if platform == "linux": # Linux
			os.popen("iwconfig " + interface + " channel " + channel)

	elif platform == "darwin": # MacOS
		os.popen("airport " + interface + " -c" + channel)

	else:
		exit()

def interface_check():
	if platform == "linux": # On linux, your WiFi card needs to be set in monitor mode by yourself
		mon_check = os.popen("iwconfig " + interface + " | grep Monitor -c").read()

		if mon_check == "0\n": # If interface isn't in monitor mode:
			print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Setting " + interface + " in monitor mode...")
			os.system("ip link set " + interface + " down")
			os.system("iw " + interface + " set type monitor")
			os.system("ip link set " + interface + " up")

	if platform == "darwin": # On MacOS you only need to enable WiFi
		os.popen("airport " + interface + " -z") # Disconnect from WiFi network if connected

def root_check():
	user = os.popen("whoami") # Get current user who runs dBmonster

	if user.read() != "root\n":
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " This tool needs root privileges (try: sudo)\n")
		exit()

def sound_message():
	# Play sound if found...
	if platform == "linux": # Linux
		dBm_signal = os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal ether src " + device + " > /dev/null 2> /dev/null").read()
	elif platform == "darwin": # MacOS
		dBm_signal = os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal ether src " + device + " > /dev/null 2> /dev/null").read()
	print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " STARTING TRACKING...")
	print("\a\a")


def mode1_update(i): # Track MAC address

	if platform == "linux": # Linux
		dBm_signal = int(os.popen("tshark -i " + interface + " -c 1 -T fields -e radiotap.dbm_antsignal ether src " + device + " 2> /dev/null | cut -d , -f 2-").read())
	elif platform == "darwin": # MacOS
		dBm_signal = int(os.popen("tshark -i " + interface + " -I -c 1 -T fields -e radiotap.dbm_antsignal ether src " + device + " 2> /dev/null | cut -d , -f 2-").read())

	if dBm_signal < 0: # If recieved dBm is normal, use it
		global dBm_fallback
		dBm_fallback = dBm_signal # Save current signal for line 50
		x_values.append(next(index))
		y_values.append(dBm_signal)
		plt.cla()
		plt.plot(x_values, y_values)
		plt.pause(0.003)
	else: # If recieved dBm signal is broken, use last known dBm value (dBm_fallback)
		x_values.append(next(index))
		y_values.append(dBm_fallback)
		plt.cla()
		plt.plot(x_values, y_values)
		plt.pause(0.003)

def mode2_recon(): # Scan for WiFi devices... On MacOS only Networks
	if platform == "linux": # Linux
		print("\n")
		os.system("airodump-ng " + interface)

	elif platform == "darwin": # MacOS
		print("\n")
		os.system("airport " + interface + " scan")

	else:
		exit()

### workflow

while True:
	os.system("clear")
	banner()
	root_check()

	if platform == "win32": # Windows
		print("\033[48;5;9m" + " [?] WTF!?\n*** ONLY LINUX OR MAC ***" + "\033[39m")
		exit()

	if platform == "linux": # Linux
		print("\033[38;1;231m" + "\n\n  --- WiFi INTERFACES ---" + "\033[0m") # List WiFi INTERFACES on linux
		os.system("airmon-ng")

	mode = input("\033[38;1;231m" + "\n\n  --- OPTIONS ---\n\n[1]" + "\033[0m" + "\tTrack MAC address\n" + "\033[38;1;231m" + "[2]" + "\033[0m" + "\tRecon\n" + "\033[38;1;231m" + "[0]" + "\033[0m" + "\tEXIT" + "\033[38;5;172m" + "\n\n  [*]" + "\033[0m" + " Choose option: ")

	if mode == "1": # Track MAC address
		interface = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Your WiFi interface: ")
		device = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " MAC address to track: ")
		channel = input("\033[38;5;172m" + "  [*]" + "\033[39m" + " WiFi channel from MAC address to track: ")
		interface_check()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Setting WiFi interface to channel " + channel + "...")
		set_channel()
		print("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Searching for " + device + " on channel " + channel + "...")
		sound_message()
		fig.canvas.manager.set_window_title("dBmonster: " + device) # Window title
		animation = FuncAnimation(fig, mode1_update, 2000)
		plt.show()
		exit()

	if mode == "2": # Recon
		interface = input("\033[38;5;172m" + "\n  [*]" + "\033[39m" + " Your WiFi interface: ")
		os.system("clear")
		mode2_recon()
		input("\033[38;5;206m" + "\n [!]" + "\033[39m" + " Press the enter key to continue... (For tracking, remind the MAC address and channel your target has!)")
		continue

	if mode == "0": # EXIT
		print("\033[38;1;231m" + "\nGOOD BYE!\n" + "\033[0m")
		exit()
