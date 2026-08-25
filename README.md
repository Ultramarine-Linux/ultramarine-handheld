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

Board-owned vendor inputs live under `board/trimui-smart-pro-s/`:

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
just ext4-rootfs
just p4
just direct-root-env
just sd-image
```

The final command verifies GPT structure and byte identity for boot0, the boot
package, p2, and p3. It also verifies p5 with `e2fsck`.

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

The compact image occupies the first 6 GiB of a larger card. Do not expand p5
until the unchanged compact layout has booted successfully. After that test,
p5 may be enlarged to the remaining card capacity and its ext4 filesystem
resized.

## usb gadget mode

The p5 rootfs enables an early ConfigFS RNDIS gadget on the bottom USB-C
gadget port. It assigns the device `192.168.42.1/24`; this is the preferred
bring-up path for SSH and logs. The top USB-C port is host-only.

A serial getty is also enabled on `ttyAS0`, but physical UART access requires
the debug header. good luck opening up the console

## custom configs

for dev, add configs to `overlay/etc/NetworkManager/system-connections/` and `overlay/root/.ssh/` for quick bring-up testing and fill ur keys there


## Future OSTree work

The current root is a flat ext4 system. A future p4 systemd initrd/bootstrap
can mount p5, select a classic OSTree deployment, and switch root into it.
Classic OSTree/bootc deployments work without composefs; composefs is deferred
because the vendor kernel lacks the required EROFS/fs-verity support.

better immutable might work if we use hermetic root, 
