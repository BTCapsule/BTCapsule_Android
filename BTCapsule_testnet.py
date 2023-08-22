import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image

import os
import os.path
import shutil

from os.path import exists
import datetime
import dateutil.parser as dp
import time
from decimal import Decimal
from stat import S_IREAD



import pyqrcode
import png
from pyqrcode import QRCode


from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Locktime, Sequence
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey, P2wpkhAddress
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK


setup("testnet")

sender_exists = exists("sender_wallet_testnet.txt")
rec_exists = exists("receiver_wallet_testnet.txt")


seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, 500000001)


def sweep_wallet(wa, t, s, prk, a):

    txin = TxInput(t, 0)

    if wa[0] == "m" or wa[0] == "n":
        addr = P2pkhAddress(wa)
        txout = TxOutput(
            to_satoshis(s),
            Script(
                [
                    "OP_DUP",
                    "OP_HASH160",
                    addr.to_hash160(),
                    "OP_EQUALVERIFY",
                    "OP_CHECKSIG",
                ]
            ),
        )

    if wa[0] == "2":
        addr = P2shAddress(wa)
        txout = TxOutput(
            to_satoshis(s),
            Script(
                [
                    "OP_DUP",
                    "OP_HASH160",
                    addr.to_hash160(),
                    "OP_EQUALVERIFY",
                    "OP_CHECKSIG",
                ]
            ),
        )

    if wa[0] == "t":
        addr = P2wpkhAddress(wa)
        txout = TxOutput(to_satoshis(s), Script([0, addr.to_hash()]))

    tx = Transaction([txin], [txout])

    sk = PrivateKey(prk)

    from_addr = P2pkhAddress(a)

    sig = sk.sign_input(
        tx,
        0,
        Script(
            [
                "OP_DUP",
                "OP_HASH160",
                from_addr.to_hash160(),
                "OP_EQUALVERIFY",
                "OP_CHECKSIG",
            ]
        ),
    )

    pk = sk.get_public_key().to_hex()
    txin.script_sig = Script([sig, pk])
    signed_tx = tx.serialize()

    redeem_file = open("redeem.txt", "w")

    redeem_file.write("Redeem script: " + f"{signed_tx}")
    
    redeem_qr = pyqrcode.create(signed_tx) 
            
    redeem_qr.png("redeem_qr.png", scale=6)
    redeem_qr.png("redeem_qr.png", scale=6)

               
                

    redeem_file.close()

    os.chmod("redeem.txt", S_IREAD)











class MyGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.cols = 1
        self.add_widget(Label(text="Generate a P2SH Address:"))
        self.p2sh = TextInput(multiline=False)
        self.add_widget(self.p2sh)

        self.generate_button = Button(text="Generate Wallet", font_size=50)
        self.generate_button.bind(on_press=self.generate_priv)
        self.add_widget(self.generate_button)

        self.add_widget(Label(text="Private Key"))
        self.sk = TextInput(multiline=False, font_size=45)
        self.add_widget(self.sk)

        self.add_widget(Label(text="Public Address"))
        self.sa = TextInput(multiline=False)
        self.add_widget(self.sa)
       
        
        self.rk = TextInput(multiline=False, size_hint = (0,0))
        self.add_widget(self.rk)
       
        self.ra = TextInput(multiline=False, size_hint = (0,0))
        self.add_widget(self.ra)

        rec_create_priv = PrivateKey()
        rec_privk = rec_create_priv.to_wif(compressed=True)
    
        rec_pub = rec_create_priv.get_public_key()
    
        rec_address = rec_pub.get_address()
    
        rec_pubk = rec_address.to_string()
        
        self.rk.text = f"{rec_privk}"
        self.ra.text = f"{rec_pubk}"




        self.add_widget(Label(text="Enter date: MM-DD-YYYY"))
        self.date = TextInput(multiline=False)
        self.add_widget(self.date)
       
        self.add_widget(Label(text="Paste tx from transaction above"))
        self.tx_id = TextInput(multiline=False, font_size=40)
        self.add_widget(self.tx_id)
       
        self.add_widget(Label(text="Vout"))
        self.vout = TextInput(multiline=False)
        self.add_widget(self.vout)
       
        self.add_widget(Label(text="BTC Amount Minus Miner Fees"))
        self.btc = TextInput(multiline=False)
        self.add_widget(self.btc)
  
        self.prompt = Label(text="")
        self.add_widget(self.prompt)
        self.qr_text = Label(text="")
        self.add_widget(self.qr_text)
        self.image1 = Image(size_hint_y=4)
        self.image1.color = (0,0,0,0)
        self.add_widget(self.image1)
        
        self.enter_button = Button(text="Enter", font_size=50)
        self.enter_button.bind(on_press=self.complete)
        self.add_widget(self.enter_button)
        
        for i in range(6):
            self.add_widget(Label(text=""))

                
       
        
        
        self.add_widget(Label(text=""))
        self.add_widget(Label(text=""))
        self.add_widget(Label(text=""))
        self.add_widget(Label(text=""))
        self.add_widget(Label(text=""))
        self.add_widget(Label(text=""))
            
    

    



    def generate_priv(self, instance): 
    

        sender_create_priv = PrivateKey()
        sender_privk = sender_create_priv.to_wif(compressed=True)

        sender_pub = sender_create_priv.get_public_key()

        sender_address = sender_pub.get_address()

        sender_pubk = sender_address.to_string()

        p2pkh_sk = PrivateKey(sender_privk)

        p2pkh_addr = p2pkh_sk.get_public_key().get_address()

        redeem_script = Script(
            [
                seq.for_script(),
                "OP_CHECKLOCKTIMEVERIFY",
                "OP_DROP",
                "OP_DUP",
                "OP_HASH160",
                p2pkh_addr.to_hash160(),
                "OP_EQUALVERIFY",
                "OP_CHECKSIG",
            ]
        )

        addr = P2shAddress.from_script(redeem_script)
        p2sh_addr = addr.to_string()

        
        self.p2sh.text = str(f"{p2sh_addr}")
        self.sk.text = str(f"{sender_privk}")
        self.sa.text = str(f"{sender_pubk}")
        
        
        
        qr_p2sh = pyqrcode.create(p2sh_addr)

        qr_p2sh.png("timelock_qr.png", scale=6)
        self.image1.color = (1,1,1,1)
        self.image1.source = 'timelock_qr.png'
        self.remove_widget(self.generate_button)
        self.qr_text.text = 'Add funds to P2SH Address'     





    def complete(self, instance):
        
        if (
            self.date.text != ""
            and self.tx_id.text != ""
            and self.btc.text != ""
            and self.p2sh.text != ""
            and self.sk.text != ""
            and self.sa.text != ""
        ):

   
            


            txid = self.tx_id.text
            satoshis = Decimal(self.btc.text)

            sender_privk = self.sk.text
            sender_pubk = self.sa.text

            rec_privk = self.rk.text
            rec_pubk = self.ra.text

            iso = self.date.text
            pubk = self.p2sh.text
            vout = int(self.vout.text)

            def validate(date_text):
                try:
                    datetime.datetime.strptime(date_text, "%m-%d-%Y")

                    return True
                except:

                    return False

            if validate(iso) == True:

                unix = dp.parse(iso)
                unix_dec = unix.timestamp()
                unix_time = int(unix_dec)

                # SENDER REDEEM

                sender_lock = Locktime(500000001)

                sender_txin = TxInput(txid, vout, sequence=seq.for_input_sequence())

                sender_p2pkh_sk = PrivateKey(sender_privk)
                sender_p2pkh_pk = sender_p2pkh_sk.get_public_key().to_hex()
                sender_p2pkh_addr = sender_p2pkh_sk.get_public_key().get_address()

                sender_redeem_script = Script(
                    [
                        seq.for_script(),
                        "OP_CHECKLOCKTIMEVERIFY",
                        "OP_DROP",
                        "OP_DUP",
                        "OP_HASH160",
                        sender_p2pkh_addr.to_hash160(),
                        "OP_EQUALVERIFY",
                        "OP_CHECKSIG",
                    ]
                )

                sender_addr = P2shAddress.from_script(sender_redeem_script)

                sender_to_addr = P2pkhAddress(sender_pubk)
                sender_txout = TxOutput(
                    to_satoshis(satoshis), sender_to_addr.to_script_pub_key()
                )

                sender_tx = Transaction(
                    [sender_txin], [sender_txout], sender_lock.for_transaction()
                )

                sender_sig = sender_p2pkh_sk.sign_input(
                    sender_tx, 0, sender_redeem_script
                )

                sender_txin.script_sig = Script(
                    [sender_sig, sender_p2pkh_pk, sender_redeem_script.to_hex()]
                )
                sender_signed_tx = sender_tx.serialize()

                sender_txid = sender_tx.get_txid()

                # RECEIVER REDEEM

                rec_lock = Locktime(unix_time)

                rec_txin = TxInput(txid, vout, sequence=seq.for_input_sequence())

                rec_p2pkh_sk = PrivateKey(sender_privk)
                rec_p2pkh_pk = rec_p2pkh_sk.get_public_key().to_hex()
                rec_p2pkh_addr = rec_p2pkh_sk.get_public_key().get_address()

                rec_redeem_script = Script(
                    [
                        seq.for_script(),
                        "OP_CHECKLOCKTIMEVERIFY",
                        "OP_DROP",
                        "OP_DUP",
                        "OP_HASH160",
                        rec_p2pkh_addr.to_hash160(),
                        "OP_EQUALVERIFY",
                        "OP_CHECKSIG",
                    ]
                )

                rec_addr = P2shAddress.from_script(rec_redeem_script)

                rec_to_addr = P2pkhAddress(rec_pubk)
                rec_txout = TxOutput(
                    to_satoshis(satoshis), rec_to_addr.to_script_pub_key()
                )

                rec_tx = Transaction(
                    [rec_txin], [rec_txout], rec_lock.for_transaction()
                )

                rec_sig = rec_p2pkh_sk.sign_input(rec_tx, 0, rec_redeem_script)

                rec_txin.script_sig = Script(
                    [rec_sig, rec_p2pkh_pk, rec_redeem_script.to_hex()]
                )
                rec_signed_tx = rec_tx.serialize()

                rec_txid = rec_tx.get_txid()

                sender_wallet_text = """
This is the sender's paper wallet. Please keep this file secure and offline. Anyone with access to this 
file can redeem your bitcoin.
				
You can use the redeem script to redeem your bitcoin at any time. To redeem, visit a block explorer 
(ex. https://www.blockchain.com/btc/pushtx) and paste the redeem script into the input field.
				
You can then open BTCapsule and use the Sweep Wallet feature. To sweep a wallet, make sure sender_wallet_testnet.txt is
in the same folder as BTCapsule. enter the address you wish to send your bitcoin to and the amount that was added 
to the timelock address (minus miner fees). This will create another file called redeem.txt that will contain 
another redeem script. Paste this into the block explorer to send the bitcoin to your wallet.
				
				
				
*IMPORTANT!* Sweeping this wallet will remove all bitcoin. You must input a smaller amount to pay for 
miner fees. The difference between the unspent amount and the input will go to the miners.
To give the timelocked wallet to another person, copy BTCapsule, receiver_wallet_testnet.txt, and timelock_qr_copy.png 
to a flash drive. DO NOT INCLUDE SENDER WALLET. Directions to redeem are included in their wallet.
				
				
				"""

                p2sh_addr = self.p2sh.text

                sender_wallet = open("sender_wallet_testnet.txt", "w")

                sender_wallet.write(
                    "TxId: "
                    + f"{sender_txid}"
                    + "\n\nPrivate key: "
                    + f"{sender_privk}"
                    + "\n\nPublic address: "
                    + f"{sender_pubk}"
                    + "\n\nTimelock address: "
                    + f"{p2sh_addr}"
                    + "\n\nRedeem date: "
                    + f"{iso}"
                    + "\n\nRedeem script: "
                    + f"{sender_signed_tx}"
                    + "\n\n"
                    + f"{sender_wallet_text}"
                )

                sender_wallet.close()

                os.chmod("sender_wallet_testnet.txt", S_IREAD)

                rec_wallet_text = """
This is a timelocked paper wallet. Please keep this file secure and offline. Anyone with access to this 
file can redeem your bitcoin.
				
You can use the redeem script to redeem your bitcoin after the redeem date. To redeem, visit a block explorer 
(ex. https://www.blockchain.com/btc/pushtx) and paste the redeem script into the input field.
				
You can then open BTCapsule and use the Sweep Wallet feature. To sweep a wallet, make sure receiver_wallet_testnet.txt is
in the same folder as BTCapsule. enter the address you wish to send your bitcoin to and the amount that was added 
to the timelock address (minus miner fees). This will create another file called redeem.txt that will contain 
another redeem script. Paste this into the block explorer to send the bitcoin to your wallet.
				
				
				
*IMPORTANT!* Sweeping this wallet will remove all bitcoin. You must input a smaller amount to pay for 
miner fees. The difference between the unspent amount and the input will go to the miners. 
The redeem time is set at 12:00AM on the redeem date. It may take several hours before the network will
accept your redeem script. If you get an error:
sendrawtransactiom RPC error: 
{"code":-26,"message":"non-final"}
this means the transaction is working as expected. Please wait a few hours and try again.

If the transaction is accepted, but after a few hours it is not confirmed, the orginal miner fees may be too
low. You can speed up the process by using a method called Child-Pays-For-Parent, but directions to do this
may change over time. Please use whatever resources you have to learn more. Everything needed to
use this method is included in this wallet.
				
				
				"""

                rec_wallet = open("receiver_wallet_testnet.txt", "w")

                rec_wallet.write(
                    "TxId: "
                    + f"{rec_txid}"
                    + "\n\nPrivate key: "
                    + f"{rec_privk}"
                    + "\n\nPublic address: "
                    + f"{rec_pubk}"
                    + "\n\nTimelock address: "
                    + f"{p2sh_addr}"
                    + "\n\nRedeem date: "
                    + f"{iso}"
                    + "\n\nRedeem script: "
                    + f"{rec_signed_tx}"
                    + "\n\n"
                    + f"{rec_wallet_text}"
                )

                rec_wallet.close()
                
                
                sender_qr = pyqrcode.create(sender_signed_tx)
                receiver_qr = pyqrcode.create(rec_signed_tx)

                sender_qr.png("sender_redeem.png", scale=6)
                sender_qr.png("sender_redeem.png", scale=6)
             
                
                receiver_qr.png("receiver_redeem.png", scale=6)
                receiver_qr.png("receiver_redeem.png", scale=6)
            
                

                os.chmod("receiver_wallet_testnet.txt", S_IREAD)
                 
                os.mkdir('receiver_files_testnet')
                rec_path = 'receiver_files_testnet/'

                
                os.mkdir('sender_files_testnet')
                send_files = 'sender_files_testnet/'
                shutil.copy('receiver_redeem.png', rec_path)
                shutil.copy('receiver_wallet_testnet.txt', rec_path)
                
                shutil.copy('BTCapsule_testnet.py', rec_path)


                sender_files = [f for f in os.listdir() if '.txt' in f.lower() or '.png' in f.lower()] 

                for files in sender_files: 

                    new_path = send_files + files 
                    shutil.move(files, new_path)

                
                shutil.copy('BTCapsule_testnet.py', send_files)

                
                self.prompt.text='Success'
            else:

                self.prompt.text='Enter date MM-DD-YYYY'

        else:

            self.prompt.text='Please Enter All Fields'
            








class SweepWallet(GridLayout):
    
    def __init__(self, **kwargs):
        super(SweepWallet, self).__init__(**kwargs)
        self.cols = 1
        

        self.add_widget(Label(text="Address to Send Bitcoin"))
        addr_enter = TextInput(multiline=False)
        self.add_widget(addr_enter)
        
        self.add_widget(Label(text="BTC Amount Minus Miner Fees"))
        sat_enter = TextInput(multiline=False)
        self.add_widget(sat_enter)
        
        self.add_widget(Label(text=""))
        prompt = Label(text="")
        self.add_widget(prompt)
                  

  
    # SWEEP WALLET


        def redeem(self):
    
            if sat_enter.text != "" and addr_enter.text != "":
    
                if sender_exists == True:
    
                    with open("sender_wallet_testnet.txt", "r") as f:
    
                        f.seek(0)
                        lines = f.readlines()
    
                        t = lines[0]
                        txid = t[6:].rstrip()
    
                        p = lines[2]
                        private_key = p[13:].rstrip()
    
                        ad = lines[4]
                        address = ad[16:].rstrip()
    
                    satoshis = Decimal(sat_enter.text)
                    which_addr = addr_enter.text
    
                    sweep_wallet(which_addr, txid, satoshis, private_key, address)
    
                    prompt.text="Success"
                    
                if rec_exists == True and sender_exists == False:
    
                    with open("receiver_wallet_testnet.txt", "r") as f:
    
                        f.seek(0)
                        lines = f.readlines()
    
                        t = lines[0]
                        txid = t[6:].rstrip()
    
                        p = lines[2]
                        private_key = p[13:].rstrip()
    
                        ad = lines[4]
                        address = ad[16:].rstrip()
    
                    satoshis = Decimal(sat_enter.text)
    
                    which_addr = addr_enter.text
    
                    sweep_wallet(which_addr, txid, satoshis, private_key, address)
    
                    prompt.text="Success"
                    
                    
                if rec_exists == False and sender_exists == False:
    
                    prompt.text="Missing wallet. Move wallet to\nthis folder and restart BTCapsule.\nIf wallet exists, open BTCapsule from Pydroid."                        
        
     
        self.add_widget(Label(text=""))
        self.add_widget(Label(text=""))
        self.generate_button = Button(text="Enter", font_size=50)
        self.generate_button.bind(on_press=redeem)
        self.add_widget(self.generate_button)

        for i in range(20):
            self.add_widget(Label(text=""))

                
       
        
        
        self.add_widget(Label(text=""))
        self.add_widget(Label(text=""))
        self.add_widget(Label(text=""))
        self.add_widget(Label(text=""))
        self.add_widget(Label(text=""))
        self.add_widget(Label(text=""))
  
  



class TabbedPanelApp(App):
    def build(self):
        tabbed_panel = TabbedPanel(do_default_tab=False)
        tabbed_panel.background_color = (1, 1, 1, 1) 
        tabbed_panel.tab_height = 75

        tab1 = TabbedPanelHeader(text='BTCapsule', font_size = 36, size_hint=(None, None), height=75)
        tab2 = TabbedPanelHeader(text='Sweep Wallet', font_size =36, size_hint=(None, None), height=75)


        tab1.content = MyGrid()
        tab2.content = SweepWallet()

 
        tabbed_panel.add_widget(tab1)
        tabbed_panel.add_widget(tab2)

        return tabbed_panel

if __name__ == '__main__':
    TabbedPanelApp().run()
