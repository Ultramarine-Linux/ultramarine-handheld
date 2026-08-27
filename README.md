# Ultramarine for TrimUI Smart Pro S

an attempt to build Ultramarine for the TrimUI Smart Pro S using Knulli and the stock firmware
as a reference image, may also be applicable to other boards,
may be added if anyone wants to support it lol

## boot chain

- bootrom seeks SPL
- it loads boot0/SPL from LBA 256
- then loads the vendor boot package from LBA 32800
- after that, the boot package loads U-Boot
- which then reads the GPT table, and then hands off control to the kernel
- partition 1 contains assets for Android boot image that handles pre-boot firmware shit like charging and boot logo
- partition 2 contains the U-Boot environment config, which is loaded according to the boot package (which reads from partlabel `env` thus the partition)
- partition 3 contains the Android boot image and kernel, which then loads assets from partition 1
- partition 4 contains the ext4 bootstrap, used as initramfs
- partition 5 contains the actual root filesystem

The vendor boot layers remain intentionally intact. In particular, the raw
boot package contains battery/charger-mode and boot-logo logic.
p3 also carries vendor early userspace, modules, and charger-related `healthd` support.

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

Requirements include `mkosi`, `systemd-repart`, `sfdisk`, `mkenvimage`,
`e2fsprogs`, and standard loop-device support. `just sd-image` requires `sudo`
for loop devices and filesystem resizing inside the output image.

```bash
just profile=tg5050 env rootfs-image
just profile=tg5050 image
```

The final command verifies GPT structure and byte identity for boot0, the boot
package, p2, and p3. It also verifies the direct p4 system root with `e2fsck`.

Inspect a completed image:

```bash
sha256sum build/ultramarine-trimui-6g.raw
sudo sfdisk -d build/ultramarine-trimui-6g.raw
sudo sfdisk --verify build/ultramarine-trimui-6g.raw
```

## Flash and first boot test

Use the 32 GiB target card, not the preserved known-working 8 GiB template.
Confirm the target device carefully before writing:

```bash
lsblk -o NAME,PATH,SIZE,MODEL,TRAN,RM
sudo dd if=build/ultramarine-trimui-6g.raw \
  of=/dev/sdX \
  bs=16M status=progress conv=fsync
sync
```

The compact image occupies the first 6 GiB of a larger card. Its final p4
partition is the direct Ultramarine system root; there is no p5 bootstrap or
secondary root partition.

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
