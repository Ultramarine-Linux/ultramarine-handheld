#!/usr/bin/env python3
"""Pack a TG5050 BSP Image into the Android p3 and vendor boot package."""
from __future__ import annotations

import argparse
import shlex
import struct
import subprocess
import tempfile
from pathlib import Path

STAMP = 0x5F0A6C39
CHECKSUM_OFFSET = 0x14
VALID_LEN_OFFSET = 0x24
ITEMS_OFFSET = 0x3C
ITEM_SIZE = 0x170


def package_checksum(blob: bytes | bytearray) -> int:
    valid_len = struct.unpack_from("<I", blob, VALID_LEN_OFFSET)[0]
    total = STAMP
    for (word,) in struct.iter_unpack("<I", blob[:valid_len]):
        total = (total + word) & 0xFFFFFFFF
    return total


def replace_package_dtb(source: Path, dtb: Path, output: Path) -> None:
    blob = bytearray(source.read_bytes())
    if blob[:13] != b"sunxi-package":
        raise ValueError(f"{source} is not a sunxi-package")

    old_checksum = struct.unpack_from("<I", blob, CHECKSUM_OFFSET)[0]
    struct.pack_into("<I", blob, CHECKSUM_OFFSET, 0)
    if package_checksum(blob) != old_checksum:
        raise ValueError(f"{source} has an invalid sunxi-package checksum")

    new_dtb = dtb.read_bytes()
    items = struct.unpack_from("<I", blob, 0x20)[0]
    for index in range(items):
        start = ITEMS_OFFSET + index * ITEM_SIZE
        name = bytes(blob[start + 4:start + 68]).split(b"\0", 1)[0]
        if name != b"dtb":
            continue
        data_offset, data_len = struct.unpack_from("<II", blob, start + 0x44)
        if len(new_dtb) > data_len:
            raise ValueError(f"DTB is {len(new_dtb)} bytes; slot is {data_len}")
        blob[data_offset:data_offset + data_len] = new_dtb.ljust(data_len, b"\0")
        struct.pack_into("<I", blob, CHECKSUM_OFFSET, 0)
        struct.pack_into("<I", blob, CHECKSUM_OFFSET, package_checksum(blob))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(blob)
        return
    raise ValueError("sunxi-package has no dtb item")


def replace_p3_kernel(source: Path, kernel: Path, output: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="tg5050-p3-") as temporary:
        unpack = Path(temporary)
        args_text = subprocess.check_output(
            ["unpack_bootimg", "--boot_img", str(source), "--out", str(unpack), "--format=mkbootimg"],
            text=True,
        )
        args = shlex.split(args_text)
        for index, value in enumerate(args):
            if value == "--kernel":
                args[index + 1] = str(kernel)
            elif value == "--ramdisk":
                args[index + 1] = "/dev/null"
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["mkbootimg", *args, "-o", str(output)], check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-p3", type=Path, required=True)
    parser.add_argument("--kernel", type=Path, required=True)
    parser.add_argument("--source-boot-package", type=Path, required=True)
    parser.add_argument("--dtb", type=Path, required=True)
    parser.add_argument("--output-p3", type=Path, required=True)
    parser.add_argument("--output-boot-package", type=Path, required=True)
    args = parser.parse_args()

    replace_p3_kernel(args.source_p3, args.kernel, args.output_p3)
    replace_package_dtb(args.source_boot_package, args.dtb, args.output_boot_package)
    print(args.output_p3)
    print(args.output_boot_package)


if __name__ == "__main__":
    main()
