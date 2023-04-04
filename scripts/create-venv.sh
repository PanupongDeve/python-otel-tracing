rm -rf venv

sudo apt install python3.10-venv
mkdir venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt