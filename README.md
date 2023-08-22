This repository is to use BTCapsule for Android, and is recommended over the original BTCapsule for reasons discussed below. To learn more about BTCapsule and how to use it, please visit https://github.com/BTCapsule/BTCapsule. The Android version looks different, but works the exact same way.

BTCapsule creates a P2SH address that is timelocked to 500,000,001 (the earliest timestamp recognized by the Bitcoin network) at the script level. The sender wallet contains a raw transaction that is timelocked to 500,000,001 at the transaction level and allows you, the original holder, to redeem your Bitcoin at any time. The receiver wallet contains a raw transaction that is locked at whatever date you choose, which is then converted to a unix timestamp.

BTCapsule for Android is simple to set up, and adds additional safety features including:

1. An Android device can be secured with a pin number

2. So long as the Android device is never exposed to the internet, it can be used as a cheap and portable offline wallet

3. Much easier to set up. There is no need to dual-boot a Linux distro and there is only one command that needs to be ran in the provided terminal

**IMPORTANT**

Once BTCapsule is set up, it is very important that you disable internet access and never allow internet on the Android device again. BTCapsule can run on practically any Android device, so it is recommended that you purchase the cheapest phone you can find. 

BTCapsule is not a hot wallet. It creates a "paper wallet" and is for serious HODLers only. Once Bitcoin is sent to the P2SH address, you must redeem the entire amount (minus miner fees). Any amount that is not redeemed will go to the miners, so quadruple check before you redeem.

**How to use BTCapsule on Android**

First you need to install three apps from the Play Store:

1. Pydroid 3

2. Pydroid repository plugin

3. Pydroid permissions plugin

Copy the code below and paste it into Pydroid:

```
import os
import requests
import subprocess

required_packages = ['bitcoin-utils', 'pypng', 'pyqrcode', 'Pillow==9.1.0']

missing_packages = [package for package in required_packages if not any(package in line.decode() for line in subprocess.Popen(["pip", "list"], stdout=subprocess.PIPE).stdout.readlines())]

if missing_packages:
 
    try:
        subprocess.check_call(["pip", "install"] + missing_packages, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Installed missing packages:", ", ".join(missing_packages))
    except subprocess.CalledProcessError as e:
        print("Error installing packages:", e)

raw_url = "https://raw.githubusercontent.com/BTCapsule/BTCapsule_Android/main/BTCapsule_testnet.py"

response = requests.get(raw_url)

if response.status_code == 200:

    raw_code = response.content
    
    directory_name = "BTCapsule"
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    
    local_file_path = os.path.join(directory_name, "BTCapsule_testnet.py")
    
    with open(local_file_path, "wb") as file:
        file.write(raw_code)
    
    print("File saved successfully.")
```
Press the Play button and wait for BTCapsule to build. Tap the back button at the top.

**TURN OFF THE INTERNET!!!**

Tap the folder icon and open BTCapsule.py inside the BTCapsule folder from Internal Storage.

That is it! Now you can hit the Play button, and BTCapsule will run in your Android. Make sure to save the program and name it BTCapsule.py (or BTCapsule_testnet.py for the testnet version).

Hint:

The Android device you use for BTCapsule should remain offline at all times. To easily copy the tx id from another device, install a QR code creator on the other device. Paste the tx id into the QR creator, and use your Android's camera to scan and copy it.
