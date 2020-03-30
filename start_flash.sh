#!/bin/bash
#bold=$(tput bold)
#normal=$(tput sgr0)
true ${GATEWAY:=192.168.254.1}
setup () {
	echo "sonoffa-convert"
	pushd scripts >/dev/null || exit
	screen_minor=$(screen --version | cut -d . -f 2)
	if [ "$screen_minor" -gt 5 ]; then
		screen_with_log="screen -L -Logfile"
	elif [ "$screen_minor" -eq 5 ]; then
		screen_with_log="screen -L"
	else
		screen_with_log="screen -L -t"
	fi
	echo "======================================================"
	echo -n "  Starting AP in a screen"
	$screen_with_log smarthack-wifi.log -S smarthack-wifi -m -d /bin/wlanstart.sh
	while ! ping -c 1 -W 1 -n "$GATEWAY" &> /dev/null; do
		printf .
	done
	echo
	echo
	sleep 1
	echo "  Starting web server in a screen"
	$screen_with_log smarthack-web.log -S smarthack-web -m -d ./http-server.py
	echo
}

cleanup () {
	echo "======================================================"
	echo "Cleaning up..."
	sudo screen -S smarthack-web          -X stuff '^C'
	echo "Closing AP"
	sudo pkill hostapd
	echo "Firwall down"
	sudo ./firewall.sh down
	echo "Exiting..."
	popd >/dev/null || exit
}

trap cleanup EXIT
setup

while true; do
	echo "======================================================"
	echo
	echo "IMPORTANT"
	echo "1. Connect DIY jumper as per Sonoff DIY instructions and power it on to connect to the WIFI $AP"
	echo "2. Press ${bold}ENTER${normal} to continue"
	read -r
	echo
	echo "======================================================"

	timestamp=$(date +%Y%m%d_%H%M%S)
		
	echo "======================================================"
	echo "Ready to flash third party firmware!"
	echo
	echo "For your convenience, the following firmware images are already included in this repository:"
	echo "  Tasmota v8.1.0.2 (wifiman)"
	echo "  ESPurna 1.13.5 (base)"
	echo
	echo "You can also provide your own image by placing it in the /files directory"
	echo "Please ensure the firmware fits the device and includes the bootloader"
	echo "MAXIMUM SIZE IS 508KB"

	./firmware_picker.sh

	echo "======================================================"
	read -p "Do you want to flash another device? [y/N] " -n 1 -r
	echo
	[[ "$REPLY" =~ ^[Yy]$ ]] || break
done

