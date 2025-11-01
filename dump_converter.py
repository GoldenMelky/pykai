# dump_converter.py
# Convert between Flipper Mikai text dumps and Mikai raw dumps.
# Usage:
#   python dump_converter.py flipper2mikai input_flipper.txt output_mikai.bin
#   python dump_converter.py mikai2flipper input_mikai.bin output_flipper.txt

import argparse
import re
from pathlib import Path
import sys

HEX_BYTE = re.compile(r'^[0-9A-Fa-f]{2}$')

def parse_flipper_text(path):
    uid_bytes = None
    blocks = {}
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.upper().startswith('UID:'):
                parts = line.split(':',1)[1].strip().split()
                hex_tokens = [p for p in parts if HEX_BYTE.match(p)]
                if len(hex_tokens) >= 1:
                    uid_bytes = bytes(int(h,16) for h in hex_tokens)
                continue
            m = re.match(r'Block\s+(\d+)\s*:\s*(.*)', line, flags=re.IGNORECASE)
            if m:
                idx = int(m.group(1))
                rest = m.group(2).strip()
                tokens = [t for t in re.split(r'[\s,]+', rest) if t and HEX_BYTE.match(t)]
                if len(tokens) != 4:
                    parsed = [int(t,16) for t in tokens]
                    while len(parsed) < 4:
                        parsed.append(0xFF)
                    blocks[idx] = bytes(parsed[:4])
                else:
                    blocks[idx] = bytes(int(t,16) for t in tokens)
                continue
    if not blocks:
        raise ValueError("No block data found in Flipper file.")
    max_idx = max(blocks.keys())
    concatenated = bytearray()
    for i in range(max_idx+1):
        if i in blocks:
            concatenated.extend(blocks[i])
        else:
            concatenated.extend(b'\xFF\xFF\xFF\xFF')
    return bytes(concatenated), uid_bytes

def flipper2mikai(input_path, output_path):
    data, uid = parse_flipper_text(input_path)
    if uid is None:
        raise ValueError("UID line not found in Flipper file.")
    if len(uid) not in (4,8):
        raise ValueError(f"UID length looks wrong ({len(uid)}). Expected 8 bytes.")
    uid_reversed = uid[::-1]
    out = bytearray(data)
    out.extend(uid_reversed)
    with open(output_path, 'wb') as f:
        f.write(out)
    print(f"Wrote Mikai raw file: {output_path} ({len(out)} bytes). UID written reversed: {uid.hex().upper()} -> {uid_reversed.hex().upper()}")

def mikai2flipper(input_path, output_path):
    raw = Path(input_path).read_bytes()
    if len(raw) < 8:
        raise ValueError("Input raw file is too small.")
    uid_raw = raw[-8:]
    uid_display = uid_raw[::-1]
    blocks_data = raw[:-8]
    blocks = [blocks_data[i:i+4] for i in range(0, len(blocks_data), 4)]
    lines = []
    lines.append("Filetype: Flipper Mikai device")
    lines.append("Version: 1")
    lines.append("Device type: Dump")
    lines.append("UID: " + ' '.join(f"{b:02X}" for b in uid_display))
    lines.append("# Mikai dump data")
    lines.append("Data format version: 1")
    for idx, blk in enumerate(blocks):
        if len(blk) < 4:
            blk = blk + b'\xFF'*(4-len(blk))
        lines.append(f"Block {idx}: " + ' '.join(f"{b:02X}" for b in blk))
    text = '\n'.join(lines) + '\n'
    Path(output_path).write_text(text, encoding='utf-8')
    print(f"Wrote Flipper text file: {output_path}. Blocks: {len(blocks)}, UID: {uid_display.hex().upper()}")

def main():
    p = argparse.ArgumentParser(description="Convert between Flipper text dumps and Mikai raw dumps.")
    p.add_argument('mode', choices=['flipper2mikai','mikai2flipper'], help='Conversion direction')
    p.add_argument('input', help='Input file path')
    p.add_argument('output', help='Output file path')
    args = p.parse_args()
    try:
        if args.mode == 'flipper2mikai':
            flipper2mikai(args.input, args.output)
        else:
            mikai2flipper(args.input, args.output)
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()
