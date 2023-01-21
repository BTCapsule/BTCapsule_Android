import sys 
import subprocess 

subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'bitcoin-utils', 'pypng', 'pyqrcode', 'Pillow==9.1.0'])