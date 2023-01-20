import os
import os.path
import shutil
from tkinter import *
from tkinter import ttk
from os.path import exists
import datetime
import dateutil.parser as dp
import time
from decimal import Decimal
from stat import S_IREAD
from itertools import islice


import pyqrcode
import png
from pyqrcode import QRCode
from PIL import ImageTk, Image

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Locktime, Sequence
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey, P2wpkhAddress
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK


root = Tk()
setup("testnet")


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

    redeem_file.close()

    os.chmod("redeem.txt", S_IREAD)


def main():

    sender_exists = exists("sender_wallet_testnet.txt")
    rec_exists = exists("receiver_wallet_testnet.txt")
    btc_exists = exists("BTCapsule.exe")

    seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, 500000001)

    entry_y = 200

    canvas1 = Canvas(root, width=1440, height=2960, bg="white", highlightthickness=0)

    canvas1.pack()

    canvas1.create_text(
        720, entry_y - 75, fill="black", font="Arial 5 bold", text="CREATE TIMELOCK"
    )

    canvas1.create_text(
        720, entry_y - 25, fill="black", font="Arial 5", text="Generate a P2SH address"
    )

    p2sh = Entry(root, width=42, relief=SOLID)
    canvas1.create_window(720, entry_y +50, window=p2sh)

    canvas1.create_text(
        720, entry_y + 325, fill="black", font="Arial 5", text="Sender's Wallet"
    )

    canvas1.create_text(60, entry_y + 400, fill="black", font="Arial 5", text="Priv")

    canvas1.create_text(100, entry_y + 500, fill="black", font="Arial 5", text="Addr")

    sk = Entry(root, width=55, relief=SOLID)
    canvas1.create_window(765, entry_y + 400, window=sk)

    sa = Entry(root, width=50, relief=SOLID)
    canvas1.create_window(760, entry_y + 500, window=sa)

    rk = Entry(root, width=42, relief=SOLID)
    canvas1.create_window(3000, entry_y + 400, window=rk)

    ra = Entry(root, width=42, relief=SOLID)
    canvas1.create_window(3000, entry_y + 500, window=ra)

    rec_create_priv = PrivateKey()
    rec_privk = rec_create_priv.to_wif(compressed=True)

    rec_pub = rec_create_priv.get_public_key()

    rec_address = rec_pub.get_address()

    rec_pubk = rec_address.to_string()

    rk.insert(END, f"{rec_privk}")
    rk.bind("<FocusIn>", lambda args: rk.insert(END, ""))

    ra.insert(END, f"{rec_pubk}")
    ra.bind("<FocusIn>", lambda args: ra.insert(END, ""))

    def generate_wallet():

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

        p2sh.delete(0, END)
        p2sh.insert(END, f"{p2sh_addr}")
        p2sh.bind("<FocusIn>", lambda args: p2sh.insert(END, ""))

        sk.delete(0, END)
        sk.insert(END, f"{sender_privk}")
        sk.bind("<FocusIn>", lambda args: sk.insert(END, ""))

        sa.delete(0, END)
        sa.insert(END, f"{sender_pubk}")
        sa.bind("<FocusIn>", lambda args: sa.insert(END, ""))

        canvas1.create_text(
            720,
            entry_y + 120,
            fill="black",
            font="Arial 5",
            text="Add funds to address",
        )

        qr_p2sh = pyqrcode.create(p2sh_addr)

        qr_p2sh.png("timelock_qr.png", scale=6)
        qr_p2sh.png("timelock_qr_copy.png", scale=6)

        image1 = Image.open("timelock_qr.png")

        resized_image = image1.resize((200, 200), Image.Resampling.LANCZOS)
        test = ImageTk.PhotoImage(resized_image)
        label1 = Label(image=test)
        label1.image = test
        label1.place(x=1000, y=entry_y +130)

    generate_private = Button(text="Generate", command=generate_wallet)

    generate_private.pack()
    canvas1.create_window(720, entry_y + 225, window=generate_private)

    root.bind("<Return>", lambda x: generate_private_key)

    canvas1.create_text(
        720, entry_y + 600, fill="black", font="Arial 5", text="Enter date: MM-DD-YYYY"
    )

    def timestamp_color():
        global timestamp

    timestamp = Entry(root, fg="black", relief=SOLID)

    canvas1.create_window(720, entry_y + 700, window=timestamp)

    txid_input = Entry(root, width=60, relief=SOLID)

    canvas1.create_window(720, entry_y + 900, window=txid_input)

    canvas1.create_text(
        720,
        entry_y + 800,
        fill="black",
        font="Arial 5",
        text="Paste txid/hash from transaction above",
    )

    vout_enter = Entry(root, relief=SOLID, width=5)

    canvas1.create_window(500, entry_y + 1075, window=vout_enter)

    canvas1.create_text(500, entry_y + 1000, fill="black", font="Arial 5", text="VOUT")
    
    amount = Entry(root, relief=SOLID, width=20)

    canvas1.create_window(1020, entry_y + 1075, window=amount)

    canvas1.create_text(1020, entry_y + 1000, fill="black", font="Arial 5", text="BTC")

    def complete():

        if (
            timestamp.get() != ""
            and txid_input.get() != ""
            and amount.get() != ""
            and p2sh.get() != ""
            and sk.get() != ""
            and sa.get() != ""
        ):

   
            


            txid = txid_input.get()
            satoshis = Decimal(amount.get())

            sender_privk = sk.get()
            sender_pubk = sa.get()

            rec_privk = rk.get()
            rec_pubk = ra.get()

            iso = timestamp.get()
            pubk = p2sh.get()
            vout = int(vout_enter.get())

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
				
				
				
*IMPORTANT!* Sweeping this wallet will remove all bitcoin. You can choose to input a smaller amount to pay for 
miner fees. The difference between the unspent amount and the input will go to the miners. If you choose to input
the full amount, you must add some satoshis to the timelock address to cover the fees.
To give the timelocked wallet to another person, copy BTCapsule, receiver_wallet_testnet.txt, and timelock_qr_copy.png 
to a flash drive. DO NOT INCLUDE SENDER WALLET. Directions to redeem are included in their wallet.
				
				
				"""

                p2sh_addr = p2sh.get()

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
				
				
				
*IMPORTANT!* Sweeping this wallet will remove all bitcoin. You can choose to input a smaller amount to pay for 
miner fees. The difference between the unspent amount and the input will go to the miners. If you choose to input
the full amount, you must add some satoshis to the timelock address to cover the fees.
The redeem time is set at 12:00AM on the redeem date. It may take several hours before the network will
accept your redeem script. If you get an error:
sendrawtransactiom RPC error: 
{"code":-26,"message":"non-final"}
this means the transaction is working as expected. Please wait a few hours and try again.
				
				
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

                os.chmod("receiver_wallet_testnet.txt", S_IREAD)
                 
                os.mkdir('receiver_files_testnet')
                rec_path = 'receiver_files_testnet/'

                
                os.mkdir('sender_files_testnet')
                send_files = 'sender_files_testnet/'
             
                shutil.copy('timelock_qr_copy.png', rec_path)
                shutil.copy('receiver_wallet_testnet.txt', rec_path)
                
                shutil.copy('BTCapsule_testnet.py', rec_path)


                sender_files = [f for f in os.listdir() if '.txt' in f.lower() or '.png' in f.lower()] 

                for files in sender_files: 

                    new_path = send_files + files 
                    shutil.move(files, new_path)

                
                shutil.copy('BTCapsule_testnet.py', send_files)

                if btc_exists == True:
                    shutil.copy('BTCapsule.exe', send_files)
                    shutil.copy('BTCapsule.exe', rec_path)

                label1 = Label(
                    root,
                    bg="white",
                    text="                    Success!                      ",
                )
                canvas1.create_window(720, entry_y + 1350, window=label1)

            else:

                canvas1.create_text(
                    720,
                    entry_y + 1350,
                    fill="black",
                    font="Arial 5",
                    text="Enter a valid year: MM-DD-YYYY",
                )

        else:

            canvas1.create_text(
                720,
                entry_y + 1350,
                fill="black",
                font="Arial 5",
                text="Please enter all fields",
            )

    button1 = Button(text="Enter", command=complete)
    canvas1.create_window(720, entry_y + 1250, window=button1)

    # SWEEP WALLET

    canvas1.create_line(
        0, entry_y + 1400, entry_y + 1400, entry_y + 1400, fill="black", width=5
    )

    canvas1.create_text(
        720, entry_y + 1450, fill="black", font="Arial 5 bold", text="SWEEP WALLET"
    )

    canvas1.create_text(
        720,
        entry_y + 1550,
        fill="black",
        font="Arial 5",
        text="When raw transaction is successful, use \nthis field to send funds to your own wallet",
    )

    addr_enter = Entry(root, width=59, relief=SOLID)
    sat_enter = Entry(root, width=59, relief=SOLID)

    canvas1.create_text(
        720,
        entry_y + 1700,
        fill="black",
        font="Arial 5",
        text="Enter address to send funds",
    )

    canvas1.create_window(720, entry_y + 1800, window=addr_enter)

    canvas1.create_text(
        720, entry_y + 1900, fill="black", font="Arial 5", text="Enter BTC amount"
    )

    canvas1.create_window(720, entry_y + 2000, window=sat_enter)

    def redeem():

        if sat_enter.get() != "" and addr_enter.get() != "":

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

                satoshis = Decimal(sat_enter.get())
                which_addr = addr_enter.get()

                sweep_wallet(which_addr, txid, satoshis, private_key, address)

                label1 = Label(
                    root,
                    bg="white",
                    text="                 Success!                   ",
                )
                canvas1.create_window(723, entry_y + 2200, window=label1)

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

                satoshis = Decimal(sat_enter.get())

                which_addr = addr_enter.get()

                sweep_wallet(which_addr, txid, satoshis, private_key, address)

                label1 = Label(
                    root,
                    bg="white",
                    text="                 Success!                   ",
                )
                canvas1.create_window(723, entry_y + 2200, window=label1)

            if rec_exists == False and sender_exists == False:

                label1 = Label(
                    root,
                    bg="white",
                    text="Missing wallet. Move wallet to this \nfolder and restart BTCapsule",
                )
                canvas1.create_window(723, entry_y + 2220, window=label1)

    send = Button(text="Send", command=redeem)
    send.pack()

    canvas1.create_window(720, entry_y + 2100, window=send)

    root.title("Bitcoin Time Capsule")
    
    
    
    def copy_select(): 
    
    
         
        if p2sh.select_present():
            inp = p2sh.get() 
            root.clipboard_clear() 
            root.clipboard_append(inp)
            

         
        if sk.select_present():
            inp = sk.get() 
            root.clipboard_clear() 
            root.clipboard_append(inp)
            
    
        if sa.select_present():
            inp = sa.get() 
            root.clipboard_clear() 
            root.clipboard_append(inp)
            

         
        if timestamp.select_present():
            inp = timestamp.get() 
            root.clipboard_clear() 
            root.clipboard_append(inp)
            
         
        if txid_input.select_present():
            inp = txid_input.get() 
            root.clipboard_clear() 
            root.clipboard_append(inp)
            
            
         
        if vout_enter.select_present():
            inp = vout_enter.get() 
            root.clipboard_clear() 
            root.clipboard_append(inp)
            
            
         
        if amount.select_present():
            inp = amount.get() 
            root.clipboard_clear() 
            root.clipboard_append(inp)
         
        if addr_enter.select_present():
            inp = addr_enter.get() 
            root.clipboard_clear() 
            root.clipboard_append(inp)
            
    
        if sat_enter.select_present():
            inp = sat_enter.get() 
            root.clipboard_clear() 
            root.clipboard_append(inp)
    
    
    
    
    def paste(self): 
        
        
        posy = root.winfo_pointery()
        posx = root.winfo_pointerx()
        
        
        
        #def callback(event):
        
     #   if p2sh.select_present():
         
        
            
        if posy > 240 and posy <280:
            clipboard = root.clipboard_get()
            p2sh.insert('end',clipboard)
            root.clipboard_clear() 
        
    # Get the copied item from system clipboard
        if posy > 590 and posy < 650:
            clipboard = root.clipboard_get()
            sk.insert('end',clipboard)
            root.clipboard_clear() 
            
        if posy > 690 and posy < 750:
            clipboard = root.clipboard_get()
            sa.insert('end',clipboard)
            root.clipboard_clear() 
            
        if posy > 890 and posy < 950:
            clipboard = root.clipboard_get()
            timestamp.insert('end',clipboard)
            root.clipboard_clear() 
            
        if posy > 1090 and posy < 1150:
            clipboard = root.clipboard_get()
            txid_input.insert('end',clipboard)
            root.clipboard_clear() 
            
        if (posy > 1265 and posy < 1375) and (posx > 200 and posx < 700):
            clipboard = root.clipboard_get()
            vout_enter.insert('end',clipboard)
            root.clipboard_clear() 
           
          
        if (posy > 1265 and posy < 1375) and (posx > 520 and posx < 1320):
            clipboard = root.clipboard_get()
            amount.insert('end',clipboard)
            root.clipboard_clear()     
            
        if posy > 1990 and posy < 2100:
            clipboard = root.clipboard_get()
            addr_enter.insert('end',clipboard)
            root.clipboard_clear() 
            
        if posy > 2190 and posy < 2300:
            clipboard = root.clipboard_get()
            sat_enter.insert('end',clipboard)
            root.clipboard_clear() 
                     

    # Insert the item into the entry widget def 
                
             

    
    
    m = Menu(root, tearoff = 0) 

    
    m.add_command(label ="Copy", command=copy_select) 

    #m.add_command(label ="Paste", command=paste) 

    
    
    

    def do_popup(event): 

        try: 
        
            

                m.tk_popup(event.x_root, event.y_root-200) 
               
                
                        
            
                
        finally: 

            m.grab_release() 


    
    #p2sh.bind("Double-Button-1",do_popup)
    
   # addr_enter.bind("Double-Button-1",do_popup)
        
    
        
 
    root.bind_all("<Double-Button-1>", do_popup) 
    
    

    
    root.bind_all("<Button-1>", paste)
        
        
        
    
    
    

    root.mainloop()


if __name__ == "__main__":
    main()

