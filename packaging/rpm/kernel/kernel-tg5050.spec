Name:           kernel-tg5050
Version:        7.2.0
Release:        2.tg5050%{?dist}
Summary:        Fedora-style alternate mainline kernel for TrimUI Smart Pro S
License:        GPL-2.0-only
URL:            https://github.com/torvalds/linux
Source0:        https://cdn.kernel.org/pub/linux/kernel/v7.x/linux-7.2.tar.xz
Source2:        https://github.com/MidG971/trimui_mainline_dts/archive/634e03ab964fbeab5395248038c518d8e27688b7.tar.gz
Source3:        https://raw.githubusercontent.com/warpme/minimyth2/97b9429b90db1fca1fe3b93a112fb739b0c5452d/script/kernel/linux-7.1/files/3401-net-wireless-backport-aic8800-sdio-v2025_0926_91c9dae5-mm2.patch
Source4:        https://raw.githubusercontent.com/warpme/minimyth2/97b9429b90db1fca1fe3b93a112fb739b0c5452d/script/kernel/linux-7.1/files/3401-net-wireless-backport-aic8800-sdio-v2025_0926_91c9dae5-mm2-fix-kernel7.1.patch
Source1000:      trimui.config
Source1001:      required.config
Source1002:      aic8800-warpme-v7.2.patch
# Production USB gadget console fragment used by the TG5050 recovery path.
Source1003:      usb-gadget-console.config
Source1004:      display-built-in.config

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
Patch1024: 0027-ASoC-sun4i-codec-sort-sound-includes.patch
Patch1025: 0028-ASoC-sun4i-codec-separate-DAC-ADC-clocks.patch
Patch1026: 0029-ASoC-sun4i-codec-A523-playback.patch
Patch1027: 0030-ASoC-dt-bindings-A523-codec.patch
Patch1028: 0031-ASoC-sun4i-codec-A523-capture-WIP.patch
Patch1029: 0032-pinctrl-sunxi-A523-fix-voltage-withstand-encoding.patch
Patch1030: 0033-mmc-pwrseq-simple-tolerate-missing-reset-controller.patch
Patch1031: 0034-Input-sun4i-lradc-keys-set-HOLD_KEY_EN-for-A523-r329.patch
Patch1032: 0035-ASoC-sun4i-codec-A523-enable-Line-Out-ramp-and-VRP-LDO.patch
Patch1033: 0036-arm64-dts-tg5050-usb-pd-power-and-pins.patch
Patch1034: 0037-arm64-dts-tg5050-disable-unused-etnaviv-npu-binding.patch
Patch1035: 0038-drm-sunxi-sun55i-a523-de33-skip-legacy-sram-claim.patch
Patch1036: 0039-arm64-dts-sun55i-a523-add-display-engine-node.patch
Patch1037: 0040-drm-sun4i-a523-de35-rcq-backend-and-integration.patch
Patch1038: 0041-drm-sun4i-tcon-log-a523-dsi-trigger-state.patch
Patch1039: 0042-drm-sun6i-dsi-attach-panel-before-drm-master.patch
Patch1040: 0043-drm-sun4i-tcon-log-enable-state.patch
Patch1041: 0044-drm-sun4i-force-tcon-vblank-enable.patch
Patch1042: 0045-drm-sun6i-dsi-a523-video-start-delay-one.patch
Patch1043: 0046-drm-sun6i-dsi-a523-combine-hs-video-start.patch
Patch1044: 0047-drm-sun6i-dsi-log-post-hs-state.patch
%global buildid .tg5050
%global krel 7.2.0-tg5050
%global debug_package %{nil}
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
BuildRequires:  curl
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  gcc-aarch64-linux-gnu
BuildRequires:  gcc-c++
BuildRequires:  kmod
BuildRequires:  make
BuildRequires:  openssl-devel
BuildRequires:  sccache
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
Provides:       kernel-uname-r = 7.2.0.tg5050
Provides:       kernel-core-uname-r = 7.2.0.tg5050

%description core
The bootable Image, board device tree, and built-in kernel metadata for the
TG5050 alternate kernel.

%package modules
Summary:        Loadable modules for the TG5050 alternate kernel
Requires:       %{name}-core = %{version}-%{release}
Provides:       kernel-modules = %{version}-%{release}
Provides:       kernel-modules-uname-r = 7.2.0.tg5050

%description modules
Loadable kernel modules for the TG5050 alternate kernel.

%package -n kmod-aic8800
Summary:        AIC8800 SDIO Wi-Fi/Bluetooth modules for the TG5050 kernel
Requires:       %{name}-modules = %{version}-%{release}
Provides:       kmod-aic8800 = %{version}-%{release}

%description -n kmod-aic8800
Out-of-tree AIC8800 SDIO Wi-Fi and Bluetooth modules built against the
TG5050 kernel ABI. This package contains aic8800_bsp, aic8800_fdrv, and
aic8800_btlpm; it does not compile anything on the target device.

%prep
%autosetup -n linux-7.2 -p1 -N
%autopatch -p1 -m 1001 -M 1032
mkdir integration
tar -xf %{SOURCE2} -C integration --strip-components=1
cp integration/kernel/trimui.config trimui.config
cp %{SOURCE1001} required.config
cp %{SOURCE1003} usb-gadget-console.config
cp %{SOURCE1004} display-built-in.config
install -D -m 0644 integration/kernel/drivers/phy-sun55i-dsi-combo.c drivers/phy/allwinner/phy-sun55i-dsi-combo.c
install -D -m 0644 integration/kernel/drivers/pwm-sun20i.c drivers/pwm/pwm-sun20i.c
install -D -m 0644 integration/kernel/drivers/panel-trimui-smart-pro-s.c drivers/gpu/drm/panel/panel-trimui-smart-pro-s.c
for dts in sun55i-a523-trimui-smart-pro-s.dts sun55i-a523.dtsi trimui-de-reconcile.dtsi trimui-panel.dtsi; do
    install -D -m 0644 "integration/dts/$dts" "arch/arm64/boot/dts/allwinner/$dts"
done
printf '%s\n' 'dtb-$(CONFIG_ARCH_SUNXI) += sun55i-a523-trimui-smart-pro-s.dtb' >> arch/arm64/boot/dts/allwinner/Makefile
%patch 1033 -p1
%patch 1034 -p1
%patch 1035 -p1
%patch 1036 -p1
%patch 1037 -p1
%patch 1038 -p1
%patch 1039 -p1
%patch 1040 -p1
%patch 1041 -p1
%patch 1042 -p1
%patch 1043 -p1
%patch 1044 -p1
%global make %{__make} %{_make_output_sync} %{?_smp_mflags} %{_make_verbose} CC="$CC" CXX="$CXX" HOSTCC="${HOSTCC:-gcc}" HOSTCXX="${HOSTCXX:-g++}" CROSS_COMPILE="${CROSS_COMPILE-}"
%build
export ARCH=arm64
export KBUILD_BUILD_USER=ultramarine
export KBUILD_BUILD_HOST=tg5050-builder
export KBUILD_BUILD_TIMESTAMP="${SOURCE_DATE_EPOCH}"
%{make} defconfig
./scripts/kconfig/merge_config.sh -m .config trimui.config required.config usb-gadget-console.config display-built-in.config
# The board fragment carries the display drivers as modules.  Force the
# first-light path built-in after all fragments have been merged, otherwise
# the DRM master modesets before the panel and DSI host are registered.
scripts/config --enable CONFIG_DRM_PANEL_TRIMUI_SMART_PRO_S
scripts/config --enable CONFIG_DRM_SUN6I_DSI
scripts/config --set-str CONFIG_LOCALVERSION "-tg5050"
%{make} olddefconfig
%{make} Image modules
%{make} allwinner/sun55i-a523-trimui-smart-pro-s.dtb

# Build the pinned AIC8800 SDIO Wi-Fi/Bluetooth backport out of tree against
# this exact kernel configuration and release. The two upstream patches are
# pinned Sources; the local patch carries the v7.2 API delta.
%{make} modules_prepare
rm -rf aic8800-build
mkdir -p aic8800-build/src
cd aic8800-build/src
patch -p1 -f --no-backup-if-mismatch < %{SOURCE3} >/dev/null 2>&1 || true
patch -p1 -f --no-backup-if-mismatch < %{SOURCE4} >/dev/null 2>&1 || true
test -f drivers/net/wireless/aic8800_sdio/aic8800_fdrv/rwnx_main.c
patch -p1 < %{SOURCE1002}
env -u CFLAGS -u CXXFLAGS -u CPPFLAGS -u LDFLAGS \
    %{make} -C ../.. ARCH=arm64 \
    M="$PWD/drivers/net/wireless/aic8800_sdio" \
    CONFIG_AIC_SDIO_WLAN_SUPPORT=y \
    CONFIG_AIC8800_WLAN_SUPPORT=m \
    CONFIG_AIC8800_BTLPM_SUPPORT=m \
    modules
cd ../..

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/boot %{buildroot}/usr/lib/modules/%{krel}
install -m 0644 arch/arm64/boot/Image %{buildroot}/boot/vmlinuz-%{krel}
install -m 0644 .config %{buildroot}/usr/lib/modules/%{krel}/config
mkdir -p %{buildroot}/usr/lib/modules/%{krel}/dtb
install -m 0644 arch/arm64/boot/dts/allwinner/sun55i-a523-trimui-smart-pro-s.dtb \
    %{buildroot}/usr/lib/modules/%{krel}/dtb/sun55i-a523-trimui-smart-pro-s.dtb
test "$(make -s kernelrelease)" = "%{krel}"
make modules_install KERNELRELEASE="%{krel}" INSTALL_MOD_PATH=%{buildroot}/usr INSTALL_MOD_STRIP=
while IFS= read -r -d '' module; do
    install -D -m 0644 "$module" \
        "%{buildroot}/usr/lib/modules/%{krel}/extra/aic8800/$(basename "$module")"
done < <(find aic8800-build/src/drivers/net/wireless/aic8800_sdio -type f -name '*.ko' -print0)
depmod -b %{buildroot} -m /usr/lib/modules %{krel}
rm -f %{buildroot}/usr/lib/modules/%{krel}/build %{buildroot}/usr/lib/modules/%{krel}/source

%files

%files core
/boot/vmlinuz-%{krel}
/usr/lib/modules/%{krel}/config
/usr/lib/modules/%{krel}/modules.builtin*
/usr/lib/modules/%{krel}/modules.order
/usr/lib/modules/%{krel}/modules.softdep
/usr/lib/modules/%{krel}/modules.symbols*
/usr/lib/modules/%{krel}/dtb/sun55i-a523-trimui-smart-pro-s.dtb

%files modules
/usr/lib/modules/%{krel}/kernel
/usr/lib/modules/%{krel}/modules.alias*
/usr/lib/modules/%{krel}/modules.dep*
/usr/lib/modules/%{krel}/modules.devname
/usr/lib/modules/%{krel}/modules.weakdep

%files -n kmod-aic8800
/usr/lib/modules/%{krel}/extra/aic8800

%post -n kmod-aic8800
if [ -x %{_sbindir}/depmod ]; then
    %{_sbindir}/depmod -a -m /usr/lib/modules %{krel} || :
fi

%postun -n kmod-aic8800
if [ -x %{_sbindir}/depmod ]; then
    %{_sbindir}/depmod -a -m /usr/lib/modules %{krel} || :
fi

%changelog
* Wed Sep 09 2026 Cappy Ishihara <cappy@fyralabs.com> - 7.2.0-2.tg5050
- Disable the unused generic Vivante NPU binding; Etnaviv NULL-dereferences
  when DRM clients probe the resulting second card.

* Mon Sep 07 2026 Cappy Ishihara <cappy@fyralabs.com> - 7.2.0-1.tg5050
- Build and package the pinned AIC8800 SDIO Wi-Fi/Bluetooth modules.

* Sun Sep 06 2026 Cappy Ishihara <cappy@fyralabs.com> - 7.2.0-1.tg5050
- Build the TG5050 kernel using Fedora-style alternate-kernel packaging.
- Apply the complete TG5050 integration through RPM Patch entries.
