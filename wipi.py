#Run this script to connect to the Raspberry Pi Zero and configure its WiFi! 
import os
import paramiko 

dirname = os.path.dirname(__file__)

#Pi 
hostname = "raspberrypi.local"
username = "pi"
password = "raspberry"

#Takes in a paramiko client and a list of commands 
def run_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    return stdout.readlines()

def print_results(results):
    for result in results:
        print(result)

def wfile(f,text):
  f.write(text+"\n")

def create_wpa_supplicant(wifi_ssid, wifi_password):
    f = open("wpa_supplicant.conf","w+")
    wfile(f,"ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev")
    wfile(f,"update_config=1")
    wfile(f,"country=GB")
    wfile(f,"")
    wfile(f,"network={")
    wfile(f,"     ssid=\"%s\"" % wifi_ssid)
    wfile(f,"     psk=\"%s\"" % wifi_password)
    wfile(f,"}")
    wfile(f,"")
    f.close()

def get_file_path(filename):
    return str(os.path.join(dirname, filename))

def main():
    #Connect to Raspberry Pi Zero
    print("Connecting to Pi...")
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    client.connect(hostname=hostname, port=22, username=username, password=password)
    print("...connected!")

    #Pi commands 
    #List WiFi networks 
    print("WiFi networks found: ")
    command = "sudo iwlist wlan0 scan | awk -F \':\' \'/ESSID:/ {print $2;}\'"
    results = run_command(client, command)
    count = 1 
    for item in results: 
        print(str(count) + ". %s" % item.replace("\"", "").replace("\n", ""))
        count += 1

    #Let the user choose a network and password
    print("Choose the number of your WiFi Network from the list:")
    wifi_ssid_number = input("Network: ")
    wifi_ssid = results[int(wifi_ssid_number)-1].replace("\"", "").replace("\n", "")
    print("You have chosen: %s" % wifi_ssid)
    wifi_password = input("Password (WPA-PSK): ")
    
    #Create the supplicant file
    create_wpa_supplicant(wifi_ssid,wifi_password)

    #SCP wpa_supplicant to Pi and move to correct location
    ftp_client = client.open_sftp()
    wpa_file = get_file_path("wpa_supplicant.conf")
    ftp_client.put(wpa_file, "wpa_supplicant.conf")
    ftp_client.close()

    commands = ['sudo mv wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf','sudo wpa_cli -i wlan0 reconfigure', 'ifconfig wlan0']
    for command in commands:
        print_results(run_command(client, command))

    client.close()

if __name__ == '__main__':main()