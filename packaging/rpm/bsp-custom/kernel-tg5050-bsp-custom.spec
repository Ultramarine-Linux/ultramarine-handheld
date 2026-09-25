Name:           kernel-tg5050-bsp-custom
Version:        5.15.147
Release:        8.tina.tg5050%{?dist}
Summary:        custom vendor BSP kernel for TG5050
License:        GPL-2.0-only
URL:            https://gitlab.com/tina5.0_aiot/lichee/linux-5.15
ExclusiveArch:  aarch64

# Immutable source tarballs, pinned by commit. These are fetched from GitLab's
# archive endpoint by the RPM/Andaman source fetch stage.
%global linux_commit fad5efecec8666fe4af9a736c3cd7162a2a6d5da
%global bsp_commit a5fe197076f2fed46223ac911588b4e6e6bffd3c
%global a523_commit 8eaf09844af409420476cff11e77ac9e603ad4ca
Source0: https://gitlab.com/tina5.0_aiot/lichee/linux-5.15/-/archive/%{linux_commit}/linux-5.15-%{linux_commit}.tar.gz
Source1: https://gitlab.com/tina5.0_aiot/lichee/bsp/-/archive/%{bsp_commit}/bsp-%{bsp_commit}.tar.gz
Source2: https://gitlab.com/tina5.0_aiot/lichee/device/config/a523/-/archive/%{a523_commit}/a523-%{a523_commit}.tar.gz

Patch0: 0001-pwm-base-fallback.patch
Patch2: 0003-tg5050-uart-gamepad-pins.patch
Patch3: 0004-tg5050-pwm-fan-vibrator.patch
Patch4: 0005-tg5050-ledc-stick-rings.patch
Patch5: 0006-tg5050-panel-720x1280-timing.patch
Patch6: 0007-tg5050-pad-power-regulators.patch
Patch7: 0008-tg5050-lradc-home-key.patch
Patch8: 0009-tg5050-fn-gpio-key.patch
# 0010's speculative post-resume force flush is deliberately not applied.
Patch9: 0013-de350-vendor-channel-mode2.patch
Patch10: 0011-tg5050-panel-reset-init.patch
Patch11: 0014-tg5050-vendor-de-channel-mode.patch
Patch12: 0015-de350-rcq-force-ahb-trigger.patch
Patch13: 0016-de350-rcq-frequency-shadow.patch
Patch14: 0017-de350-rcq-request-dispatch.patch
Patch15: 0018-pmu-reset-powerkey-vendor-policy.patch
Patch16: 0019-tg5050-vendor-pwm-fan-i2s0-ownership.patch
Patch17: 0020-tg5050-vendor-power-usb-parity.patch
Patch18: 0021-tg5050-vendor-backlight-contract.patch
Patch19: 0022-tg5050-vendor-thermal-trips.patch
Patch20: 0023-tg5050-vendor-battery-jeita-policy.patch
Patch21: 0024-tg5050-vendor-usb-vbus-regulators.patch
Patch22: 0025-tg5050-vendor-usb-wakeup-policy.patch
Patch23: 0026-tg5050-vendor-usb-host-status.patch
Patch24: 0027-tg5050-vendor-audio-eeprom-supply-policy.patch
Patch25: 0028-tg5050-vendor-vind-tcon-status.patch
Patch26: 0029-tg5050-vendor-sensor-gpio-status.patch
Patch27: 0030-tg5050-vendor-sdmmc-delay-table.patch
Patch28: 0031-tg5050-vendor-gpu-clock-opp-contract.patch
Patch29: 0032-tg5050-vendor-usb-supply-phandles.patch
Patch30: 0033-tg5050-vendor-husb311-typec-graph.patch
Patch31: 0034-tg5050-vendor-drm-dp-status.patch
Patch32: 0035-tg5050-vendor-husb311-vbus-supply.patch
Patch33: 0036-tg5050-drm-shutdown-display-teardown.patch
Patch34: 0037-tg5050-dsi-enable-state-commit.patch
Patch35: 0038-tg5050-dsi-burst-clock-reenable.patch
Patch36: 0039-tg5050-panel-unprepare-cleanup.patch
Patch37: 0040-tg5050-dsi-disable-before-powerdown.patch



BuildRequires: bc
BuildRequires: bison
BuildRequires: flex
BuildRequires: gcc-aarch64-linux-gnu
BuildRequires: openssl-devel
BuildRequires: openssl-devel-engine
BuildRequires: perl
BuildRequires: python3
BuildRequires: dtc

%global krel 5.15.147
%global debug_package %{nil}
# Optional host-tool flags for immutable build hosts. Normal builds get these
# from BuildRequires: openssl-devel-engine and leave the macro empty.
%{!?kernel_hostcflags:%global kernel_hostcflags %{nil}}
%{!?kernel_hostldflags:%global kernel_hostldflags %{nil}}
%{!?kernel_pkgconfigpath:%global kernel_pkgconfigpath %{nil}}
%{!?kernel_cryptocflags:%global kernel_cryptocflags %{nil}}
%{!?kernel_cryptolibs:%global kernel_cryptolibs %{nil}}

%description
Boot-tested custom Allwinner A523 vendor-BSP kernel for the TrimUI Smart Pro S.
The RPM builds the pinned Linux kernel, Tina BSP overlay, and A523 board
configuration from source, applies the downstream PWM and DE350 compatibility
patches, enables loop/ACL/security support, and packages the resulting Image
and matching modules. Android carrier and vendor boot-package assembly is
handled separately by the profile image packer.

%package core
Summary:        Bootable core files for the TG5050 Tina kernel
Provides:       kernel-uname-r = %{krel}
Provides:       kernel-core-uname-r = %{krel}

%description core
The bootable Tina kernel Image and matching kernel configuration for the TG5050.

%package modules
Summary:        Complete loadable modules for the TG5050 Tina kernel
Requires:       %{name}-core = %{version}-%{release}
Provides:       kernel-modules-uname-r = %{krel}

%description modules
The complete loadable module tree and depmod metadata built against the matching
TG5050 Tina kernel.

%prep
%setup -q -n linux-5.15-%{linux_commit} -a 1 -a 2
mv bsp-%{bsp_commit} bsp
mv a523-%{a523_commit} board
mkdir -p arch/arm64/boot/dts/sunxi arch/arm64/configs
cp board/configs/pro3_linux_aiot/linux-5.15/bsp_defconfig \
    arch/arm64/configs/pro3_defconfig
cp -a bsp/include/dt-bindings/. include/dt-bindings/
printf '%s\n' '#ifndef __SUNXI_AUTOGEN_H__' '#define __SUNXI_AUTOGEN_H__' \
    '#define AW_BSP_VERSION "aiot-linux-v1.5.0"' '#endif' > include/sunxi-autogen.h
%patch 0 -p1 -d bsp
%patch 2 -p1 -d board
%patch 3 -p1 -d board
%patch 4 -p1 -d board
%patch 5 -p1 -d board
%patch 6 -p1 -d board
%patch 7 -p1 -d board
%patch 8 -p1 -d board
%patch 9 -p1 -d bsp -F 0
%patch 10 -p1 -d board -F 0
%patch 11 -p1 -d board -F 0
%patch 12 -p1 -d bsp -F 0
%patch 13 -p1 -d bsp -F 0
%patch 14 -p1 -d bsp -F 0
%patch 15 -p1 -d board -F 0
%patch 16 -p1 -d board -F 0
%patch 17 -p1 -d board -F 0
%patch 18 -p1 -d board -F 0
%patch 19 -p1 -d bsp -F 0
%patch 20 -p1 -d board -F 0
%patch 21 -p1 -d board -F 0
%patch 22 -p1 -d board -F 0
%patch 23 -p1 -d board -F 0
%patch 24 -p1 -d board -F 0
%patch 25 -p1 -d board -F 0
%patch 26 -p1 -d board -F 0
%patch 27 -p1 -d bsp -F 0
%patch 28 -p1 -d bsp -F 0
%patch 29 -p1 -d board -F 0
%patch 30 -p1 -d board -F 0
%patch 31 -p1 -d bsp -F 0
%patch 32 -p1 -d board -F 0
%patch 33 -p1 -d bsp -F 0
%patch 34 -p1 -d bsp -F 0
%patch 35 -p1 -d bsp -F 0
%patch 36 -p1 -d bsp -F 0
%patch 37 -p1 -d bsp -F 0
cp bsp/configs/linux-5.15/sun55iw3p1.dtsi \
    arch/arm64/boot/dts/sunxi/sun55iw3p1.dtsi
cp board/configs/pro3_linux_aiot/linux-5.15/board.dts \
    arch/arm64/boot/dts/sunxi/board.dts
printf '%s\n' 'dtb-$(CONFIG_ARCH_SUNXI) += board.dtb' >> \
    arch/arm64/boot/dts/sunxi/Makefile
printf '%s\n' 'subdir-y += sunxi' >> arch/arm64/boot/dts/Makefile


%build
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
export BSP_TOP="$PWD/bsp/"
export KERNEL_SRC_DIR="$PWD"
export LICHEE_KERN_DIR="$PWD"
export KBUILD_BUILD_VERSION=1
export KBUILD_BUILD_USER=builder
export KBUILD_BUILD_HOST=buildhost
export KBUILD_BUILD_TIMESTAMP="$(date -u -d "@${SOURCE_DATE_EPOCH}" '+%a %b %e %T %Y')"
export HOSTCFLAGS="%{kernel_hostcflags}"
export HOSTLDFLAGS="%{kernel_hostldflags}"
export PKG_CONFIG_PATH="%{kernel_pkgconfigpath}${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}"
%if ! 0%{?kernel_skip_build}
make O="$PWD/out" BSP_TOP="$BSP_TOP" KERNEL_SRC_DIR="$KERNEL_SRC_DIR" \
    ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" pro3_defconfig
scripts/config --file out/.config \
    --enable USER_NS \
    --enable BLK_DEV_LOOP --enable SQUASHFS --enable SQUASHFS_ZSTD \
    --enable FS_POSIX_ACL --enable EXT4_FS_POSIX_ACL \
    --enable EXT4_FS_SECURITY --enable SECURITY \
    --disable MALI_MIDGARD --disable DRM_PANFROST --module AW_DRM_PANFROST \
    --disable FRAMEBUFFER_CONSOLE --module ZSMALLOC --module ZRAM \
    --enable CRYPTO_ZSTD --enable ZRAM_DEF_COMP_ZSTD --module EROFS_FS \
    --enable INPUT_MISC --enable INPUT_EVDEV --module INPUT_UINPUT \
    --module INPUT_PWM_VIBRA --enable HWMON --module SENSORS_PWM_FAN \
    --enable AW_LEDC \
    --enable GPIO_SYSFS \
    --enable KEYBOARD_GPIO \
    --enable AIC_WLAN_SUPPORT --module AIC8800_WLAN_SUPPORT \
    --module AIC8800_BTLPM_SUPPORT
make O="$PWD/out" BSP_TOP="$BSP_TOP" KERNEL_SRC_DIR="$KERNEL_SRC_DIR" \
    ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" olddefconfig
make O="$PWD/out" BSP_TOP="$BSP_TOP" KERNEL_SRC_DIR="$KERNEL_SRC_DIR" \
    ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" LOCALVERSION= \
    V=1 CRYPTO_CFLAGS="%{kernel_cryptocflags}" CRYPTO_LIBS="%{kernel_cryptolibs}" \
    -j%{?_smp_build_ncpus}%{!?_smp_build_ncpus:1} Image modules dtbs
%endif

%install
rm -rf %{buildroot}
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
export BSP_TOP="$PWD/bsp/"
export KERNEL_SRC_DIR="$PWD"
export LICHEE_KERN_DIR="$PWD"
make O="$PWD/out" BSP_TOP="$BSP_TOP" KERNEL_SRC_DIR="$KERNEL_SRC_DIR" \
    ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" LOCALVERSION= \
    INSTALL_MOD_PATH="%{buildroot}/usr" modules_install
rm -f "%{buildroot}/usr/lib/modules/%{krel}/build" \
    "%{buildroot}/usr/lib/modules/%{krel}/source"
install -D -m 0644 out/arch/arm64/boot/Image \
    %{buildroot}/boot/vmlinuz-%{krel}
install -D -m 0644 out/.config \
    %{buildroot}/usr/lib/modules/%{krel}/config
install -D -m 0644 out/arch/arm64/boot/dts/sunxi/board.dtb \
    %{buildroot}/usr/lib/tg5050/bsp/sun55i-a523-trimui-smart-pro-s.dtb

%files

%files core
/boot/vmlinuz-%{krel}
/usr/lib/modules/%{krel}/config
/usr/lib/tg5050/bsp/sun55i-a523-trimui-smart-pro-s.dtb

%files modules
/usr/lib/modules/%{krel}/kernel
/usr/lib/modules/%{krel}/modules.*

%post modules
if [ -x %{_sbindir}/depmod ]; then
    %{_sbindir}/depmod -a -m /usr/lib/modules %{krel} || :
fi

%postun modules
if [ -x %{_sbindir}/depmod ]; then
    %{_sbindir}/depmod -a -m /usr/lib/modules %{krel} || :
fi

%changelog
* Tue Sep 15 2026 Cappy Ishihara <cappy@fyralabs.com> - 5.15.147-1.acl.de1.panfrost
- Build the boot-tested Tina A523 kernel and modules from pinned source tarballs.
- Apply PWM alias and DE350 channel-mode compatibility patches.
- Enable loop, Ext4 ACL/security, and SquashFS support.
- Disable proprietary Mali kbase and build Panfrost as a kernel module.
- Keep fbcon disabled because the vendor fbdev cursor path panics during takeover.
- Enable EROFS filesystem support.
- Build the BSP AIC8800 modules against the matching kernel ABI.
