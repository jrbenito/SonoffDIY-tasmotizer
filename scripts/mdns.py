import hashlib
import json
import time
import sys
import requests
from zeroconf import ServiceBrowser, Zeroconf


class MyListener(object):
    """
    This class is used for the mDNS browsing discovery device, including calling the remove_service and add_service
    properties to ServiceBrowser, and also contains broadcasts for querying and updating existing devices.
        Dictionary
        all_info_dict:Qualified device information in the current network     [keys:info.name，val:info]
    """

    def __init__(self):
        self.all_del_sub = []
        self.all_info_dict = {}
        self.all_sub_num = 0
        self.new_sub = False

    def remove_service(self, zeroconf, type, name):
        """
        This function is called for ServiceBrowser.
        This function is triggered when ServiceBrowser discovers that some device has logged out
        """
        print("inter remove_service()")
        if name not in self.all_info_dict:
            return
        self.all_sub_num -= 1
        del self.all_info_dict[name]
        self.all_del_sub.append(name)
        print("self.all_info_dict[name]", self.all_info_dict)
        print("Service %s removed" % (name))

    def add_service(self, zeroconf, type, name):
        """
        This function is called for ServiceBrowser.This function is triggered when ServiceBrowser finds a new device
        When a subdevice is found, the device information is stored into the all_info_dict
        """
        self.new_sub = True
        self.all_sub_num += 1
        info = zeroconf.get_service_info(type, name)
        if info.properties[b'type'] == b'diy_plug':
            self.all_info_dict[name] = info
            if name in self.all_del_sub:
                self.all_del_sub.remove(name)
                print("Service %s added, service info: %s" % (name, info))

    def flash_all_sub_info(self,):
        """
        Update all found subdevice information
        """
        info_list = list(self.all_info_dict.keys())
        for x in info_list:
            current_info = all_info_dict[x]
            name = current_info["name"]
            type = current_info["type"]
            info = zeroconf.get_service_info(type=type, name=name)
            current_info["info"] = info
            self.all_info_dict[x] = current_info["info"]


def main():
    # ToDo: test for arguments (out of bounds)
    firmFile = sys.argv[1]
    sha256_hash = hashlib.sha256()
    with open("/root/files/" + firmFile, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    fHash = sha256_hash.hexdigest()
    ota_data = {
        'downloadUrl': 'http://192.168.254.1/files/' + firmFile,
        'sha256sum': fHash}

    zeroconf = Zeroconf()
    listener = MyListener()
    browser = ServiceBrowser(zeroconf, "_ewelink._tcp.local.",listener= listener)
    print("Waiting for device (mDNS...)")
    while True:
            if listener.all_sub_num>0:
                dict=listener.all_info_dict.copy()
                for x in dict.keys():
                    info=dict[x]
                    info=zeroconf.get_service_info(info.type,x)
                    if info!= None:
                        nodeId = x[8:18]
                        ipAddr = parseAddress(info.address)
                        port = str(info.port)
                        #startFlash(nodeId, ipAddr, port)
                break
            time.sleep(0.5)

    print("Tasmotizing: ", nodeId)
    baseURL = "http://" + ipAddr + ":" + port + "/zeroconf"
    data = {"deviceid": nodeId, "data":{}}
    print(" Turn on switch")
    url = baseURL + "/switch"
    datasw = {"deviceid": nodeId, "data":{"switch":"on"}}
    r = requests.post(url = url, json = datasw)
    ## check info to know about OTA status
    url = baseURL + "/info"
    print(" Check OTA: ", url)
    r = requests.post(url = url, json = data)
    rJ = json.loads(r.json()['data'])
    if rJ['otaUnlock']:
        print("  OTA already unlocked")
    else:
        url = baseURL + "/ota_unlock"
        print("  Unlocking OTA ", url)
        r = requests.post(url = url, json = data)
        ## need to verify return here.
    
    print(" Sending binary URL: ", ota_data)
    otaD = data
    otaD['data'] = ota_data
    url = baseURL + "/ota_flash"
    r = requests.post(url = url, json = otaD)
    print("  r = ", r.json())




def parseAddress(address):
        add_list = []
        for i in range(4):
            add_list.append(int(address.hex()[(i*2):(i+1)*2], 16))
        add_str = str(add_list[0]) + "." + str(add_list[1]) + "." + str(add_list[2])+ "." + str(add_list[3])
        return add_str


if __name__ == "__main__":
    main()