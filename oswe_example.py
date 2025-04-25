import oswe
import time
import sys

def example_web():
    web = oswe.start_web_server('0.0.0.0', 80, './', use_https=False)

    # Exploit code 1 here
    while True:
        try:
            while len(oswe.top100) != 0:
                access_log = oswe.top100.pop()
                print(access_log)
                if 'itworked' in access_log:
                    print('Ok')
                    # Exploit code 2 here
            time.sleep(1)
        except KeyboardInterrupt as e:
            sys.exit(0)


def example_nc():
    nc_thread = oswe.start_netcat_thread(443)

    # Exploit code here

    try:
        nc_thread.join()
    except KeyboardInterrupt as e:
        print('exit')
        sys.exit(0)

def example_smb():
    # Requre Impacket
    oswe.start_smb_server_thread()

    # Exploit code here

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt as e:
            sys.exit(0)

if __name__ == '__main__':
    ip = oswe.get_ip_address('eth0') # Replace 'eth0' with your network interface
    print(f'[+] Current IP: {ip}')
    example_web()
    # example_nc()
    # example_smb()
