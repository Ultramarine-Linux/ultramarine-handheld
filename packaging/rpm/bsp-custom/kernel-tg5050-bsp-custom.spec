Name:           kernel-tg5050-bsp-custom
Version:        5.15.147
Release:        1.tina.tg5050%{?dist}
Summary:        Boot-tested custom vendor BSP kernel for TG5050
License:        GPL-2.0-only AND LicenseRef-Proprietary
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
Patch1: 0002-de350-channel-mode-fallback.patch



BuildRequires: bc
BuildRequires: bison
BuildRequires: flex
BuildRequires: gcc-aarch64-linux-gnu
BuildRequires: openssl-devel
BuildRequires: perl
BuildRequires: python3
BuildRequires: dtc

%global krel 5.15.147
%global debug_package %{nil}

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
cp bsp/configs/linux-5.15/sun55iw3p1.dtsi \
    arch/arm64/boot/dts/sunxi/sun55iw3p1.dtsi
cp board/configs/pro3_linux_aiot/linux-5.15/board.dts \
    arch/arm64/boot/dts/sunxi/board.dts
cp -a bsp/include/dt-bindings/. include/dt-bindings/
printf '%s\n' '#ifndef __SUNXI_AUTOGEN_H__' '#define __SUNXI_AUTOGEN_H__' \
    '#define AW_BSP_VERSION "aiot-linux-v1.5.0"' '#endif' > include/sunxi-autogen.h
%patch 0 -p1 -d bsp
%patch 1 -p1 -d bsp


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
make O="$PWD/out" BSP_TOP="$BSP_TOP" KERNEL_SRC_DIR="$KERNEL_SRC_DIR" \
    ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" pro3_defconfig
scripts/config --file out/.config \
    --enable BLK_DEV_LOOP --enable SQUASHFS --enable SQUASHFS_ZSTD \
    --enable FS_POSIX_ACL --enable EXT4_FS_POSIX_ACL \
    --enable EXT4_FS_SECURITY --enable SECURITY \
    --disable MALI_MIDGARD --disable DRM_PANFROST --module AW_DRM_PANFROST \
    --disable FRAMEBUFFER_CONSOLE --module ZSMALLOC --module ZRAM \
    --enable CRYPTO_ZSTD --enable ZRAM_DEF_COMP_ZSTD --module EROFS_FS \
    --enable AIC_WLAN_SUPPORT --module AIC8800_WLAN_SUPPORT \
    --module AIC8800_BTLPM_SUPPORT
make O="$PWD/out" BSP_TOP="$BSP_TOP" KERNEL_SRC_DIR="$KERNEL_SRC_DIR" \
    ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" olddefconfig
make O="$PWD/out" BSP_TOP="$BSP_TOP" KERNEL_SRC_DIR="$KERNEL_SRC_DIR" \
    ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" LOCALVERSION= \
    -j%{?_smp_build_ncpus}%{!?_smp_build_ncpus:1} Image modules

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

%files

%files core
/boot/vmlinuz-%{krel}
/usr/lib/modules/%{krel}/config

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
