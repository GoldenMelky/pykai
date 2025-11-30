import subprocess
import dump_converter
import sys
import os
import re
from pyflipper import PyFlipper
import json
from datetime import datetime

#variables
currentdir = "/root/pykai/"
#currentdir = "/home/golden/pykai/"
input_bin = currentdir + "input.bin"
output_bin = currentdir + "output.bin"
output_mikai = currentdir + "output.mikai"
database = currentdir+"database.json"
host = "localhost:2323"
#host = "192.168.188.18:2323"
#rate = 5 # crediti per ogni centesimo

#private
isFlipper = False

#args
if len(sys.argv) < 3:
    print("usage: script.py <file.mikai> <mode> [credit]")
    sys.exit(1)

file = sys.argv[1]
mode = sys.argv[2]
credit = int(sys.argv[3]) if mode == "add" else None
prefix = sys.argv[4] if len(sys.argv) > 4 else ""

#download from flipper
if file == "flipper":
    isFlipper = True
    try:
        flipper = PyFlipper(tcp=host) #DA AGGIUNGERE PROTOCOLLO (tcp??) "tcp=localhost:port"
    except ConnectionRefusedError:
        print("Il server non è online")
        sys.exit(1)
    files = flipper.storage.list(path="/ext/mikai")
    for f in files["files"]:
        if re.search(r"\D*\d+\.mikai",f["name"]):
            file = flipper.storage.read("/ext/mikai/" + f["name"])
            credit = int(re.findall(r"\d+",f["name"])[0] + "00")
            prefix = re.findall(r"^\D*",f["name"])[0].lower()
            print("file trovato")
            break
    if file=="flipper":
        print("Nessun file trovato")
        sys.exit(1)


# Convert
dump_converter.flipper2mikai(file, input_bin)



# Build command script for mikai
cmds = []

cmds.append("1")              # load dump
cmds.append(input_bin)

cmds.append("2")              # print info (mikai requires this step)

if mode == "add" and prefix != "r":
    cmds.append("3")
    cmds.append(str(credit))

elif mode == "reset" or prefix == "r":
    cmds.append("5")

cmds.append("10")             # export
cmds.append(output_bin)

cmds.append("13")             # exit
cmds.append("y")              # confirm exit

payload = "\n".join(cmds) + "\n"

# Run mikai with direct piping
proc = subprocess.run(
    ["box64", currentdir + "mikai"],
#    [currentdir + "mikai"],
    input=payload.encode(),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Print mikai output to user if needed
blacklist = ["ERROR","isn't associated", "Unable","Invalid","Retry","break everything","Canceled"]
if any(err in proc.stdout.decode() for err in blacklist):
    print("ERROR")
    sys.exit(1)
print("perfect")
#print(proc.stdout.decode())

# Write final converted file
out = dump_converter.mikai2flipper(output_bin, output_mikai)
print("file convertito")
if isFlipper:
    try:
        flipper.storage.remove("/ext/mikai/output.mikai")
    except Exception as e:
        print(e)
    flipper.storage.remove("/ext/mikai/" + f["name"])
    flipper.storage.write.file(out,"/ext/mikai/output.mikai")
    flipper.power.reboot()
    #flipper.loader.open("Mikai")       #NON SI SA SE FUNZIONA

# update database
if not "l" in prefix:
    with open (database) as dbf:
        db = json.load(dbf)
    with open(output_bin,"rb") as bin:
        uid = bin.read()[28:32].hex()
    infos = {}
    now = datetime.now()
    infos["datetime"] = now.strftime("%Y-%m-%d %H:%M:%S")
    infos["import"] = credit
    #infos["payed"] = credit / rate if not "p" in prefix.lower() else 0
    infos["payed"] = True if not "p" in prefix else False
    if uid not in db["clients"]:
        db["clients"][uid] = {"history": []}

    db["clients"][uid]["history"].append(infos)

    with open (database, "w") as dbf:
        json.dump(db,dbf)



# Cleanup
for f in (input_bin, output_bin):
    if os.path.exists(f):
        os.remove(f)

