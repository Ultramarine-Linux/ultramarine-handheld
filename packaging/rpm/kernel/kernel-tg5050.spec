Name:           kernel-tg5050
Version:        7.2.0
Release:        1.tg5050%{?dist}
Summary:        Fedora-style alternate mainline kernel for TrimUI Smart Pro S
License:        GPL-2.0-only
URL:            https://github.com/torvalds/linux
Source0:        https://github.com/torvalds/linux/archive/refs/tags/v7.2-rc3.tar.gz
Source2:        https://github.com/MidG971/trimui_mainline_dts/archive/634e03ab964fbeab5395248038c518d8e27688b7.tar.gz
Source1000:      trimui.config
Source1001:      required.config

Patch1001: 0001-drm-sun4i-dsi-add-sun55i-a523-MIPI-DSI-host-variant.patch
Patch1002: 0002-phy-allwinner-add-sun55i-DSI-combo-D-PHY.patch
Patch1003: 0003-arm64-dts-allwinner-sun55i-a523-add-display-pipeline.patch
Patch1004: 0004-drm-sun4i-tcon-add-sun55i-a523-TCON-LCD-compatible.patch
Patch1005: 0005-arm64-dts-allwinner-sun55i-a523-add-PWM0.patch
Patch1006: 0006-pwm-sun20i-wire-up-the-D1-A523-PWM-driver.patch
Patch1007: 0007-drm-panel-add-Trimui-Smart-Pro-S-DSI-panel.patch
Patch1008: 0008-drm-sun4i-sun8i-mixer-add-sun55i-a523-DE3.5-DE33-mix.patch
Patch1009: 0010-arm64-dts-allwinner-sun55i-a523-add-audio-codec.patch
Patch1010: 0011-arm64-dts-allwinner-sun55i-a523-add-LRADC.patch
Patch1011: 0013-usb-musb-sunxi-add-optional-USB-role-switch-support.patch
Patch1012: 0015-clk-sunxi-ng-add-sun55i-a523-cpu-ccu.patch
Patch1013: 0016-arm64-dts-sun55i-a523-add-cpu-clock-controller.patch
Patch1014: 0017-clk-sunxi-ng-a523-cpu-reparent-clusters.patch
Patch1015: 0018-clk-sunxi-ng-a523-cpu-skip-unused-pll-cpu0.patch
Patch1016: 0019-clk-sunxi-ng-ccu-factor-update-handshake.patch
Patch1017: 0020-clk-sunxi-ng-a523-cpu-commit-bit26-pll-init.patch
Patch1018: 0021-thermal-sun8i-add-sun55i-a523-ths.patch
Patch1019: 0022-thermal-sun8i-add-sun55i-a523-ddr-ths.patch
Patch1020: 0023-thermal-sun8i-a523-guard-npu-channel.patch
Patch1021: 0024-mfd-axp20x-power-off-the-AXP717-via-SOFT_PWROFF.patch
Patch1022: 0025-watchdog-sunxi_wdt-per-variant-restart-priority.patch
Patch1023: 0026-ASoC-sun4i-codec-set-playback_only-for-H616.patch
Patch1024: 0027-ASoC-sun4i-codec-sort-sound-includes.patch
Patch1025: 0028-ASoC-sun4i-codec-separate-DAC-ADC-clocks.patch
Patch1026: 0029-ASoC-sun4i-codec-A523-playback.patch
Patch1027: 0030-ASoC-dt-bindings-A523-codec.patch
Patch1028: 0031-ASoC-sun4i-codec-A523-capture-WIP.patch
Patch1029: 0032-pinctrl-sunxi-A523-fix-voltage-withstand-encoding.patch
Patch1030: 0033-mmc-pwrseq-simple-tolerate-missing-reset-controller.patch
Patch1031: 0034-Input-sun4i-lradc-keys-set-HOLD_KEY_EN-for-A523-r329.patch
Patch1032: 0035-ASoC-sun4i-codec-A523-enable-Line-Out-ramp-and-VRP-LDO.patch


%global buildid .tg5050
%global krel 7.2.0-rc3-tg5050
%global kernel_package_name kernel
%global kernel_build_dir %{_builddir}/kernel-build
%global _binary_payload w3T.xzdio
%global _lto_cflags %{nil}
%global _disable_source_fetch 0
%undefine _include_frame_pointers

Provides:       kernel = %{version}-%{release}

BuildRequires:  bash
BuildRequires:  bc
BuildRequires:  binutils
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  openssl-devel
BuildRequires:  tar
BuildRequires:  elfutils-libelf-devel

%description
A Fedora-style alternate kernel package for the TrimUI Smart Pro S TG5050.
The package applies the pinned A523/TG5050 integration through RPM Patch
preambles, builds the matched arm64 kernel and modules, and installs normal
Fedora-compatible kernel paths and release metadata.

%package core
Summary:        Core files for the TG5050 alternate kernel
Requires:       %{name} = %{version}-%{release}
Provides:       kernel-core = %{version}-%{release}
Provides:       kernel-uname-r = 7.2.0-rc3.tg5050
Provides:       kernel-core-uname-r = 7.2.0-rc3.tg5050

%description core
The bootable Image, board device tree, and built-in kernel metadata for the
TG5050 alternate kernel.

%package modules
Summary:        Loadable modules for the TG5050 alternate kernel
Requires:       %{name}-core = %{version}-%{release}
Provides:       kernel-modules = %{version}-%{release}
Provides:       kernel-modules-uname-r = 7.2.0-rc3.tg5050

%description modules
Loadable kernel modules for the TG5050 alternate kernel.

%prep
%autosetup -n linux-7.2-rc3 -p1
mkdir integration
tar -xf %{SOURCE2} -C integration --strip-components=1
cp integration/kernel/trimui.config trimui.config
cp %{SOURCE1001} required.config
install -D -m 0644 integration/kernel/drivers/phy-sun55i-dsi-combo.c drivers/phy/allwinner/phy-sun55i-dsi-combo.c
install -D -m 0644 integration/kernel/drivers/pwm-sun20i.c drivers/pwm/pwm-sun20i.c
install -D -m 0644 integration/kernel/drivers/panel-trimui-smart-pro-s.c drivers/gpu/drm/panel/panel-trimui-smart-pro-s.c
for dts in sun55i-a523-trimui-smart-pro-s.dts sun55i-a523.dtsi trimui-de-reconcile.dtsi trimui-panel.dtsi; do
    install -D -m 0644 "integration/dts/$dts" "arch/arm64/boot/dts/allwinner/$dts"
done
printf '%s\n' 'dtb-$(CONFIG_ARCH_SUNXI) += sun55i-a523-trimui-smart-pro-s.dtb' >> arch/arm64/boot/dts/allwinner/Makefile

%build
export ARCH=arm64
export KBUILD_BUILD_USER=ultramarine
export KBUILD_BUILD_HOST=tg5050-builder
export KBUILD_BUILD_TIMESTAMP="%{SOURCE_DATE_EPOCH}"
make defconfig
./scripts/kconfig/merge_config.sh -m .config trimui.config required.config
scripts/config --set-str CONFIG_LOCALVERSION "-tg5050"
make olddefconfig
make %{?_smp_mflags} Image modules
make allwinner/sun55i-a523-trimui-smart-pro-s.dtb

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/boot %{buildroot}/usr/lib/modules/%{krel}
install -m 0644 arch/arm64/boot/Image %{buildroot}/boot/vmlinuz-%{krel}
install -m 0644 arch/arm64/boot/dts/allwinner/sun55i-a523-trimui-smart-pro-s.dtb \
    %{buildroot}/usr/lib/modules/%{krel}/dtb-sun55i-a523-trimui-smart-pro-s.dtb
test "$(make -s kernelrelease)" = "%{krel}"
make modules_install KERNELRELEASE="%{krel}" INSTALL_MOD_PATH=%{buildroot}/usr INSTALL_MOD_STRIP=
rm -f %{buildroot}/usr/lib/modules/%{krel}/build %{buildroot}/usr/lib/modules/%{krel}/source

%files

%files core
/boot/vmlinuz-%{krel}
/usr/lib/modules/%{krel}/modules.builtin*
/usr/lib/modules/%{krel}/modules.order
/usr/lib/modules/%{krel}/modules.softdep
/usr/lib/modules/%{krel}/modules.symbols*
/usr/lib/modules/%{krel}/dtb-sun55i-a523-trimui-smart-pro-s.dtb

%files modules
/usr/lib/modules/%{krel}/kernel
/usr/lib/modules/%{krel}/modules.alias*
/usr/lib/modules/%{krel}/modules.dep*
/usr/lib/modules/%{krel}/modules.devname
/usr/lib/modules/%{krel}/modules.weakdep

%changelog
* Sun Sep 06 2026 Cappy Ishihara <cappy@fyralabs.com> - 7.2.0-1.tg5050
- Build the TG5050 kernel using Fedora-style alternate-kernel packaging.
- Apply the complete TG5050 integration through RPM Patch entries.
