#!/usr/bin/env python3
"""Verify recovered TG5050 DE350 mode-2 table against the shipping Image.

Usage:
  python3 verify-vendor-de350.py --image PATH --elf PATH --source PATH

The ELF address and record layout come from the shipping 5.15.147 image, whose
SHA-256 is asserted below.  This deliberately validates only the two records
recovered from the opaque vendor tree; it is not a generic ELF parser.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
import subprocess
from pathlib import Path

VENDOR_IMAGE_SHA256 = "51b4b92047f82b7c52cf67e445618cc79e0863ee737359a5644b959d1dd9ec7b"
TABLE_VADDR = 0xFFFFFFC008D41A38
RECORD_SIZE = 88  # char name[32], u32 channel_cnt, u32 mode_id, ulong[6]

# blender, record offset, name, channel count, mode id, channel IDs
EXPECTED = (
    (0, 2, "v0v1u0u1u2", 5, 2, (1, 2, 0x10000, 0x20000, 0x40000, 0)),
    (1, 2, "v2u3", 2, 2, (4, 0x80000, 0, 0, 0, 0)),
)


def load_segment_for_address(elf: Path, address: int) -> tuple[int, int, int]:
    output = subprocess.check_output(["readelf", "-Wl", str(elf)], text=True)
    for line in output.splitlines():
        fields = line.split()
        if not fields or fields[0] != "LOAD":
            continue
        # ELF program-header columns: LOAD, offset, virtaddr, physaddr, filesz…
        offset, virtual, _, filesz = (int(fields[i], 16) for i in range(1, 5))
        if virtual <= address < virtual + filesz:
            return offset, virtual, filesz
    raise ValueError(f"no file-backed LOAD segment contains {address:#x}")


def vendor_records(elf: Path) -> tuple[list[tuple[str, int, int, tuple[int, ...]]], bytes]:
    elf_bytes = elf.read_bytes()
    offset, virtual, _ = load_segment_for_address(elf, TABLE_VADDR)
    start = offset + (TABLE_VADDR - virtual)
    records = []
    raw_table = b""
    for _ in range(8):  # two blender arrays, four shipping records each
        raw = elf_bytes[start : start + RECORD_SIZE]
        if len(raw) != RECORD_SIZE:
            raise ValueError("truncated vendor DE350 table")
        name = raw[:32].split(b"\0", 1)[0].decode("ascii")
        channel_count, mode_id = struct.unpack_from("<II", raw, 32)
        channels = struct.unpack_from("<6Q", raw, 40)
        records.append((name, channel_count, mode_id, channels))
        raw_table += raw
        start += RECORD_SIZE
    return records, raw_table


def require_source_record(source: str, name: str, count: int, mode: int,
                          channels: tuple[int, ...]) -> None:
    # Assert the semantic C initializer instead of relying on source formatting.
    required = [
        rf'\.name\s*=\s*"{re.escape(name)}"',
        rf'\.mode_id\s*=\s*{mode}',
        rf'\.channel_cnt\s*=\s*{count}',
    ]
    for index, value in enumerate(channels[:count]):
        if value < 0x10000:
            macro = rf"VIDEO_CHANNEL_ID\({value.bit_length() - 1}\)"
        else:
            macro = rf"UI_CHANNEL_ID\({(value >> 16).bit_length() - 1}\)"
        required.append(rf"\.channel_id\[{index}\]\s*=\s*{macro}")
    block_start = source.find(f'.name = "{name}"')
    if block_start < 0:
        raise AssertionError(f"source lacks {name} record")
    block = source[block_start : source.find("\n\t\t},", block_start) + 5]
    for pattern in required:
        if not re.search(pattern, block):
            raise AssertionError(f"{name} record does not contain {pattern}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()

    image = args.image.read_bytes()
    assert hashlib.sha256(image).hexdigest() == VENDOR_IMAGE_SHA256
    records, raw_table = vendor_records(args.elf)
    # vmlinux-to-elf adds ELF metadata and BSS representation. Bind its table
    # bytes back to the original compressed-image extraction before trusting it.
    image_offset = TABLE_VADDR - 0xFFFFFFC008000000
    assert image[image_offset : image_offset + len(raw_table)] == raw_table
    for blender, offset, name, count, mode, channels in EXPECTED:
        actual = records[blender * 4 + offset]
        assert actual == (name, count, mode, channels), (blender, actual)
        require_source_record(args.source.read_text(), name, count, mode, channels)
    print("PASS: shipping DE350 mode-2 records and recovered source agree")


if __name__ == "__main__":
    main()
