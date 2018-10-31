#Run this script to connect to the Raspberry Pi Zero and configure its WiFi! 
import paramiko 

#Takes in a paramiko client and a list of commands 
def run_command(client, commands):
    for command in commands:
        stdin, stdout, stderr = client.exec_command(command)
        return stdout.readlines()

def print_results(results):
    for result in results:
        print(result)

def wfile(f,text):
  f.write(text+"\n")

def create_wpa_supplicant(wifi_ssid, wifi_password):
    f = open("wpa_supplicant.conf","w+")
    wfile(f,"country=GB")
    wfile(f,"trl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev")
    wfile(f,"update_config=1")
    wfile(f,"")
    wfile(f,"network={")
    wfile(f,"        ssid=\"%s\"" % wifi_ssid)
    wfile(f,"        psk=\"%s\"" % wifi_password)
    wfile(f,"}")
    f.close()

def main():
    #Pi 
    hostname = "raspberrypi.local"
    username = "pi"
    password = "raspberry"

    #Connect to Raspberry Pi Zero
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.connect(hostname=hostname, port=22, username=username, password=password)

    #Pi commands 
    #List WiFi networks 
    commands = ["sudo iwlist wlan0 scan | awk -F \':\' \'/ESSID:/ {print $2;}\'"]
    results = run_command(client, commands)

    count = 1 
    for item in results: 
        print(str(count) + ". %s" % item)

    print("Which network would you like?")
    wifi_ssid = input("SSID: ")
    wifi_password = input("Password: ")

    create_wpa_supplicant(wifi_ssid,wifi_password)

    #SCP wpa_supplicant to Pi and move to correct location

    commands = ['sudo wpa_cli -i wlan0 reconfigure', 'ifconfig wlan0']
    run_command(client, commands)

    client.close()

if __name__ == '__main__':main()