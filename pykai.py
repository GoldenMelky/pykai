import pexpect
import dump_converter
import sys
import os

currentdir = "/home/username/pykai/"

# Arguments checker
try:
    file = sys.argv[1]
except IndexError:
    print("missing argument: .mikai file path")
    quit()

try:
    mode = sys.argv[2]
except IndexError:
    print("missing argument: mode (add,reset,...)")
    quit()

if mode == "add":
    try:
        credit = sys.argv[3]
    except IndexError:
        print("missing argument: credit")
        quit()

# Flipper to Mikai convert
dump_converter.flipper2mikai(file, currentdir+"input.bin")

# Start Mikai and import dump
p = pexpect.spawn (currentdir+"mikai.AppImage")
p.expect("MIKAI MENU")
p.sendline("1")
p.sendline(currentdir+"input.bin")
if p.expect(["MIKAI MENU", "ERROR"]) == 1:
    p.expect("\n")
    print(p.before.decode('utf-8'))
    quit()
p.sendline("2")
p.expect(":")
p.expect("\\[MIKAI MENU")
print(p.before.decode("utf-8"))
p.expect(":")


if mode == "add":
    p.sendline("3")
    p.expect(":")
    p.sendline(credit)

if mode == "reset":
    p.sendline("5")

p.expect("\\[MIKAI MENU")
output = p.before.decode("utf-8")
if "successfully" not in p.before.decode("utf-8"):
    print(output)
    quit()
p.sendline("10")
p.expect(":")
p.sendline(currentdir+"output.bin")
p.expect("\\[MIKAI MENU")
output = p.before.decode("utf-8")
if "successfully" not in p.before.decode("utf-8"):
    print(output)
    quit()
p.close()


dump_converter.mikai2flipper(currentdir+"output.bin", currentdir+"output.mikai")

os.remove(currentdir+"input.bin")
os.remove(currentdir+"output.bin")
os.remove(currentdir+"input.mikai")