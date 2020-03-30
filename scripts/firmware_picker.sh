#!/bin/bash

MAGIC=$(printf "\xe9")

while true; do
	echo
	echo "Available options:"
	index=0
	for file in ../files/*.bin; do
		# skip null glob
		[[ -e $file ]] || continue
		# get short name
		filename=$(basename "$file")
		# skip files too large or too small
		filesize=$(stat -c%s "$file")
		[[ "$filesize" -gt 0x1000 && "$filesize" -le 0x80000 ]] || continue
		# skip files without magic byte
		[[ $(head -c 1 "$file") == "$MAGIC" ]] || continue
		echo "  $((++index))) flash $filename"
		options[$index]="$filename"
		# only show first 9 options, accessible with a single keypress
		if (( index == 9 )); then
			break
		fi
	done
	echo "  q) quit; do nothing"
	echo -n "Please select 1-$index: "
	while true; do
		read -n 1 -r
		echo
		if [[ "$REPLY" =~ ^[1-9]$ && "$REPLY" -ge 0 && "$REPLY" -le $index ]]; then
			break
		fi
		if [[ "$REPLY" =~ ^[Qq]$ ]]; then
			echo "Leaving device as is..."
			exit
		fi
		echo -n "Invalid selection, please select 1-$index: "
	done

	selection="${options[$REPLY]}"
	read -p "Are you sure you want to flash $selection? This is the point of no return [y/N] " -n 1 -r
	echo
	[[ "$REPLY" =~ ^[Yy]$ ]] || continue

	echo "Attempting to flash $selection, this may take a few seconds..."
	python3 mdns.py "$selection"
	
	
	if [[ "$selection" == "tasmota.bin" ]]; then
		echo "Look for a tasmota-xxxx SSID to which you can connect and configure"
		echo "Be sure to configure your device for proper function!"
	elif [[ "$selection" == "espurna.bin" ]]; then
		echo "Look for an ESPURNA-XXXXXX SSID to which you can connect and configure"
		echo "Default password is \"fibonacci\""
		echo "Be sure to upgrade to your device specific firmware for proper function!"
	fi
	echo
	echo "Wait 3 minutes for Sonoff to download the firmware, you can check logs if the SSID does not show up"
	sleep 2m
	echo
	echo "HAVE FUN!"
	break

done

