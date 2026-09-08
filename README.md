# Ultramarine for TrimUI Smart Pro S

Ultramarine Linux for the TrimUI Smart Pro S (TG5050 / Allwinner A523). The
working mainline path uses pinned U-Boot and TG5050 kernel integration sources,
a mkosi-built systemd initrd, and an ARM64 Fedora/Ultramarine root filesystem.

## boot chain

- BootROM loads mainline SPL from LBA 256.
- SPL loads the U-Boot FIT from LBA 512 and hands off through the A523 TF-A BL31.
- U-Boot reads extlinux from p1 and loads `Image`, the board DTB, and the
  mkosi-built systemd initrd.
- The initrd discovers, checks, and mounts p4 before switching to the real
  systemd installation.
- p1 is the 1 GiB `/efi` ESP, p2 is the 1 GiB `/boot` filesystem, and p3
  is the direct root.

The vendor boot inputs remain available for reference/recovery, but the
mainline path does not boot the vendor boot package or Android ramdisk.

## Source inputs vs. build outputs

Board-owned vendor inputs and profile-local overlays live under
`mkosi.profiles/tg5050/`:

```text
boot-resource/             minimal vendor/update resources for p1
partitions/boot0.img       vendor boot0/SPL source
partitions/boot_package.fex vendor U-Boot/boot-package source
partitions/vendor-boot.img padded 96 MiB vendor p3 boot-image source
boot-artifacts/            extracted vendor kernel and DTB research artifacts
```

## Build

Requirements include `mkosi`, `systemd-repart`, `sfdisk`, `mkenvimage`, an
AArch64 cross compiler, `e2fsprogs`, and standard loop-device support. Clone
submodules first. The legacy Linux integration submodule remains pinned at the
exact v7.2-rc3 commit (`a13c140cc289`) for provenance, while the active RPM
build consumes the stable 7.2.0 archive from kernel.org. The matching TG5050
integration submodule remains pinned separately. The
build creates and recreates a disposable kernel worktree under `build/`; it
does not modify the pinned Linux checkout.

```bash
git submodule update --init --recursive
just --justfile mkosi.profiles/tg5050/justfile mainline-image
```

The mkosi configuration is composed from a shared board profile and a boot
stack overlay. Use `--profile=tg5050,mainline` for the mainline kernel,
systemd-boot ESP, and matching modules, or `--profile=tg5050,bsp` for the
vendor BSP module tree.

This applies the pinned TG5050 patchset, validates required built-in drivers,
builds the kernel and modules, builds the three out-of-tree AIC8800 modules,
stages the stock firmware in the driver's flat runtime layout, builds both the
systemd and BusyBox rescue initrds, assembles the four-partition image, and
verifies the generated filesystems and raw bootloader slots.

Inspect a completed image:

```bash
sha256sum build/ultramarine-trimui-mainline-6g.raw
sudo sfdisk -d build/ultramarine-trimui-mainline-6g.raw
sudo sfdisk --verify build/ultramarine-trimui-mainline-6g.raw
```

## Flash and first boot test

Use the 32 GiB target card, not the preserved known-working 8 GiB template.
Confirm the target device carefully before writing:

```bash
lsblk -o NAME,PATH,SIZE,MODEL,TRAN,RM
sudo dd if=build/ultramarine-trimui-mainline-6g.raw \
  of=/dev/sdX \
  bs=16M status=progress conv=fsync
sync
```

For iterative development, update only the verified boot payloads or rootfs:

```bash
just --justfile mkosi.profiles/tg5050/justfile flash-mainline /dev/sdX
just --justfile mkosi.profiles/tg5050/justfile flash-rootfs /dev/sdX
```

The first recipe preserves GPT and p2-p4. The second rewrites only p4 and
performs a complete source/target comparison after writing.

The compact image occupies roughly the first 6.8 GiB of a larger card. Its
final p3 partition is the direct Ultramarine system root; there is no p4/p5
bootstrap or secondary root partition.

The default extlinux entry uses the mkosi-built systemd initrd. A second entry
keeps the static BusyBox initramfs as a pre-switch-root rescue environment.

## AIC8800 Wi-Fi

The pinned kernel integration includes the AIC8800 SDIO build recipe. The
profile stages `aic8800_bsp`, `aic8800_fdrv`, and `aic8800_btlpm` against the
exact kernel release, generates `depmod` metadata, and flattens the stock D80/DC
firmware into `/lib/firmware/aic8800_sdio/`. On tested hardware the two SDIO
functions enumerate as `c8a1:0082` and `c8a1:0182`, bind to `aicwf_sdio` and
`aicbsp_sdio`, and expose `wlan0` to NetworkManager.

## Hardware I/O

The verified input, rumble, fan, power-button, display, USB, serial, and
battery details are documented in:

[`mkosi.profiles/tg5050/board/IO.md`](mkosi.profiles/tg5050/board/IO.md)

## usb gadget mode

The p4 rootfs enables an early ConfigFS RNDIS gadget on the bottom USB-C
gadget port. It assigns the device `192.168.42.1/24`; this is the preferred
bring-up path for SSH and logs. The top USB-C port is host-only.

A serial getty is also enabled on `ttyAS0`, but physical UART access requires
the debug header. good luck opening up the console

## custom configs

For local development, add ignored configs under
`mkosi.profiles/tg5050/mkosi.extra/etc/NetworkManager/system-connections/`
and `mkosi.profiles/tg5050/mkosi.extra/root/.ssh/`.


## Compositor bring-up

The TrimUI Smart Pro S uses the vendor Mali G57 userspace from Knulli rather
than Mesa/Panfrost. The Vulkan loader needs the board ICD manifest:

```text
/usr/share/vulkan/icd.d/mali_icd.json
```

The vendor stack is otherwise provided by the TG5050 profile prepare hook and
`mkosi.extra`: `libmali.so`, vendor GBM/EGL/GLES, `mali_kbase.ko`, and CSF firmware.
Without the ICD manifest, `vulkaninfo` reports `Found no drivers`; with it,
`vkcube` works.

The compositor tests were performed on the live device using a PAM/logind
session bound to tty1 and the DRM backend:

| Compositor | Result | Notes |
|---|---:|---|
| Cage | works | Initializes sunxi-drm, ARM EGL, Mali-G57 GLES, and DSI-1; kiosk model is a poor fit for OSDs/layer-shell UI. |
| Sway | works | Best current base for a riced handheld shell; use custom config and launch UI/OSD components instead of swaybar. |
| Labwc | works | Reached DRM successfully; needs a proper config/startup command, but is a good lightweight layer-shell-capable alternative. |
| Gamescope | fails | Vulkan ICD is found, but Gamescope rejects the Mali physical device in its DRM backend. The ICD lacks `VK_EXT_physical_device_drm`. |
| Miriway | fails | Mir's graphics modules require GBM/EGL symbols absent from the vendor blob: `gbm_surface_create_with_modifiers2` and `eglCreatePlatformWindowSurface`. |

Cage and Labwc were tested with the vendor GBM/EGL/GLES path. Cage can run a
startup command such as `swaybg`, but its kiosk model is not suitable as the
main shell if the device needs persistent OSDs. Sway is the current default
direction; Labwc remains worth developing as a lighter configured-shell
alternative.
