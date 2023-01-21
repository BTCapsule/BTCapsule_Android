This repository is to use BTCapsule for Android, and is recommended over the original BTCapsule for reasons discussed below. To learn more about BTCapsule and how to use it, please visit https://github.com/BTCapsule/BTCapsule.

BTCapsule creates a P2SH address that is timelocked to 500,000,001 (the earliest timestamp recognized by the Bitcoin network) at the script level. The sender wallet contains a raw transaction that is timelocked to 500,000,001 at the transaction level and allows you, the original holder, to redeem your Bitcoin at any time. The receiver wallet contains a raw transaction that is locked at whatever date you choose, which is then converted to a unix timestamp.

BTCapsule for Android is simple to set up, and adds additional safety features including:

1. An Android device can be secured with a pin number

2. So long as the Android device is never exposed to the internet, it can be used as a cheap and portable offline wallet

3. Much easier to set up. There is no need to dual-boot a Linux distro and there is only one command that needs to be ran in the provided terminal

**IMPORTANT**

Once BTCapsule is set up, it is very important that you disable internet access and never allow internet on the Android device again. BTCapsule can run on practically any Android device, so it is recommended that you purchase the cheapest phone you can find. 

BTCapsule is not a hot wallet. It creates a "paper wallet" and is for serious HODLers only. Once Bitcoin is sent to the P2SH address, you must redeem the entire amount (minus miner fees). Any amount that is not redeemed will go to the miners, so quadruple check before you redeem.

**How to use BTCapsule on Android**

First you need to install four apps from the Play Store:

1. Pydroid 3

2. Pydroid repository plugin

3. Pydroid permissions plugin

4. Microsoft Word

Copy the code for install_dependencies.py and paste it into Microsoft Word. Select all the text in Microsoft Word, copy, and paste it into Pydroid. I don't know why you have to use Microsoft Word, but if you try to paste the code directly, it will not add the line breaks and whitespace. Microsoft Word is the only app I have found that will let you copy and paste the working program.

Hit the Play button to install the dependencies.

Now copy the BTCapsule code, and paste it into Microsoft Word. Select all the text in Microsoft Word, copy, and paste it into Pydroid.

That is it! Now you can hit the Play button, and BTCapsule will run in your Android. Make sure to save the program and name it BTCapsule.py (or BTCapsule_testnet.py for the testnet version).

BTCapsule was not developed for touchscreen devices, so I have added some unique functionality.

To copy, double tap on a string within a form, and choose Copy.

To paste, tap on any other form. If there are recent words in your clipboard, they will be pasted into the first form you tap. You may have to delete these, but it will only happen once.
