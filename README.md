# Docker container stack: hostap + dhcp server + python scripts to flash Tasmota

This container starts wireless access point (hostap) and dhcp server in docker
container. SSID will be `sonoffDiy` with default password of `20170618sn` necessary 
for sonoffs in DIY mode to connect.

After start, container will spin up a simple HTTP server in order to serve firmwares `.bin` files
to the sonoff device. A python script will browser for device using Zeroconf mdns library and issue
HTTP requests to put device on OTA Flash mode and point it to local HTTP server.

## Requirements

Your machine **needs two network adapters**, the first is the one connected to internet; it can be ethernet or
wireless. The second, is a wireless adapter capable of AP mode, this will be used by container to bring up
wireless SSID needed by sonoffs. Variables `INTERFACE` shall be wireless interface (the second) and `OUTGOINGS`
shall be internet interface.

On the host system install required wifi drivers, then make sure your wifi adapter
supports AP mode:

```
# iw list
...
        Supported interface modes:
                 * IBSS
                 * managed
                 * AP
                 * AP/VLAN
                 * WDS
                 * monitor
                 * mesh point
...
```

## Build / run

* Using host networking:

```
sudo docker run -i -t -e INTERFACE=wlan1 -e OUTGOINGS=wlan0 --net host --privileged jrbenito/sonoff-tasmotizer
```

* Using network interface reattaching:

```
sudo docker run -d -t -e INTERFACE=wlan0 -v /var/run/docker.sock:/var/run/docker.sock --privileged jrbenito/sonoff-tasmotizer
```

This mode requires access to docker socket, so it can run a short lived
container that reattaches network interface to network namespace of this
container. It also renames wifi interface to **wlan0**, so you get
deterministic networking environment. This mode can be usefull for example for
pentesting, where can you use docker compose to run other wifi hacking tools
and have deterministic environment with wifi interface.

## Environment variables

* **INTERFACE**: name of the interface to use for wifi access point (default: wlan0)
* **OUTGOINGS**: outgoing network interface (default: eth0)

## License

MIT

## Author

Josenivaldo Benito Junior https://benito.com.br

## Based on work of

Inspired by Michel Deslierres https://www.sigmdel.ca/michel/ha/sonoff/sonoff_mini_en.html

Contains code or ideas from:

Docker-ap image from: https://github.com/won0-kim/docker-ap
Tuya-Convert from: https://github.com/ct-Open-Source/tuya-convert
Itead Sonoff python tool: https://github.com/itead/Sonoff_Devices_DIY_Tools
