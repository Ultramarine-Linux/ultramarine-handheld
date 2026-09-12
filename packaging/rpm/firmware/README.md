# TG5050 AIC8800D80 firmware

## Pinned source

All seven binary blobs and `aic_userconfig_8800d80.txt` come from KNULLI's
[A527 board overlay](https://github.com/knulli-cfw/knulli-linux/tree/0b1fd94415ba6e35e2715b72b7a7757efee41e81/board/allwinner/a527/fsoverlay/lib/firmware/aic8800d80),
at commit `0b1fd94415ba6e35e2715b72b7a7757efee41e81`.
The spec downloads each file using a commit-pinned raw URL. The userconfig
comes from that same directory, without a local override.

All eight files were downloaded and verified byte-for-byte against
`mkosi.profiles/tg5050/mkosi.extra/lib/firmware/aic8800d80/` at this project's
known-working manual-build commit
`30efb20218b29d7f170f5419ea6b7bd05c027455`.
`stock-firmware.sha256` records those identities, and `%prep` rejects a
mismatch in any file, including the user configuration.

This proves a public exact copy exists, not where the original local copies
were first obtained. It also does not prove the firmware change alone resolves
the hardware startup timeout; that requires device testing.

## Why not the generic AIC8800 collection?

The earlier RPM used Batocera's generic firmware collection at
`ccba7fffed8554fe861bd631ff6f852d2d6eec39`. Its `fmacfw`, Bluetooth patch,
and patch-table files differed from the working board overlay. Shared
filenames and chip family did not establish equivalence.

The RPM installs the exact eight-file board set as real files in both the
canonical `/usr/lib/firmware/aic8800D80/` directory and the driver-facing
`/usr/lib/firmware/aic8800_sdio/` directory. The legacy flat names
`fmacfw.bin`, `fmacfw_patch.bin`, `fmacfw_rf.bin`, `fmacfw_rf_usb.bin`, and
`fmacfw_usb.bin` are sibling symlinks into `aic8800_sdio/`, avoiding duplicate
flat payloads while preserving the old BSP lookup paths.

`Version: 2024.06.25` is retained for RPM upgrade ordering, not as a claim about
the board blobs' build date. Release `4.tg5050` preserves both board firmware
directories and adds the flat compatibility symlinks;
the package is architecture-independent (`noarch`).

## Build

From the repository root, install build dependencies with
`dnf builddep packaging/rpm/firmware/aic8800-firmware.spec`, then run
`anda build -rrpmbuild packaging/rpm/firmware`.
Andaman fetches the pinned sources and produces RPMs under `anda-build/`.
The optional mkosi firmware builder uses the same spec and fetches its remote
sources with `spectool` before invoking `rpmbuild`.
