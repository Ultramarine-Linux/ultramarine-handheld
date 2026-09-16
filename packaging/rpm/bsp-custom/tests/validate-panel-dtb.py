#!/usr/bin/env python3
"""Compare a compiled TG5050 BSP panel contract with the pinned stock DTB.

Usage: python3 validate-panel-dtb.py BUILT.dtb STOCK.dtb
Requires dtc's fdtget. This is an offline regression check, not a scanout test.
"""

import argparse
import hashlib
from pathlib import Path
import subprocess


STOCK_SHA256 = "8226f3805d991cc3dda31e621190844b4e338fb6bb28402ecd17b97524af5f9f"
PANEL = "/panel_0@0"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prop(dtb, node, name, kind="bx"):
    result = subprocess.run(
        ["fdtget", "-t", kind, str(dtb), node, name],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if kind == "s":
        return result
    return bytes(int(value, 16) for value in result.split())


def cells(value):
    require(len(value) % 4 == 0, "Invalid cell array")
    return [int.from_bytes(value[i:i + 4], "big") for i in range(0, len(value), 4)]


def resolve(dtb, phandle, node="/"):
    names = subprocess.run(
        ["fdtget", "-p", str(dtb), node],
        check=True, capture_output=True, text=True,
    ).stdout.split()
    if "phandle" in names and cells(prop(dtb, node, "phandle")) == [phandle]:
        return node
    children = subprocess.run(
        ["fdtget", "-l", str(dtb), node],
        check=True, capture_output=True, text=True,
    ).stdout.split()
    for child in children:
        result = resolve(dtb, phandle, node.rstrip("/") + "/" + child)
        if result is not None:
            return result
    return None


def packets(data):
    count = 0
    offset = 0
    while offset < len(data):
        require(len(data) - offset >= 3, "Truncated command header")
        kind, delay, length = data[offset:offset + 3]
        require(kind in (0x05, 0x15, 0x39), "Unexpected DCS packet type")
        require(length > 0, "Empty DCS payload")
        offset += 3 + length
        require(offset <= len(data), "Truncated DCS payload")
        count += 1
    return count


def validate(built, stock):
    require(hashlib.sha256(stock.read_bytes()).hexdigest() == STOCK_SHA256,
            "Stock oracle hash mismatch")
    for name in ("reset-num", "reset-delay-ms", "panel-init-sequence",
                 "panel-exit-sequence", "dsi,flags", "dsi,lanes", "dsi,format"):
        require(prop(built, PANEL, name) == prop(stock, PANEL, name),
                f"Panel property differs from stock: {name}")
    data = prop(built, PANEL, "panel-init-sequence")
    require(packets(data) == 28 and len(data) == 317, "Incomplete initialization")
    require(packets(prop(built, PANEL, "panel-exit-sequence")) == 2,
            "Incomplete shutdown sequence")
    for dtb in (built, stock):
        reset = cells(prop(dtb, PANEL, "reset-gpios"))
        require(reset[1:] == [3, 22, 0], "Expected PD22 with physical low/high semantics")
        controller = resolve(dtb, reset[0])
        require(controller == "/soc@3000000/pinctrl@2000000", "Wrong reset controller")
        require(cells(prop(dtb, controller, "#gpio-cells")) == [3],
                "Not a kernel GPIO specifier")
        for name, expected in (("power0-supply", "axp2202-cldo4"),
                               ("power1-supply", "axp2202-cldo1")):
            regulator = resolve(dtb, cells(prop(dtb, PANEL, name))[0])
            require(regulator is not None, f"Unresolved supply: {name}")
            require(prop(dtb, regulator, "regulator-name", "s") == expected,
                    f"Wrong panel supply: {name}")
    timing = PANEL + "/display-timings/timing0"
    for name in ("clock-frequency", "hactive", "vactive", "hback-porch",
                 "hfront-porch", "hsync-len", "vback-porch", "vfront-porch", "vsync-len"):
        require(prop(built, timing, name) == prop(stock, timing, name),
                f"Timing differs from stock: {name}")
    print("PASS: stock-matched reset, 28 init commands (317 bytes), exit, supplies and timings")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("built", type=Path)
    parser.add_argument("stock", type=Path)
    args = parser.parse_args()
    validate(args.built, args.stock)
