Name:           uboot-images-tg5050
Version:        2026.07
Release:        1.tg5050%{?dist}
Summary:        Fedora-style mainline U-Boot images for TrimUI Smart Pro S
License:        GPL-2.0-only
URL:            https://github.com/MidG971/u-boot

# origin/main of the pinned MidG971 fork, before the nine TG5050 commits.
Source0:        https://github.com/u-boot/u-boot/archive/e354b34a6ab4b1887fd451bea8ceb7be146070a8.tar.gz
Source1:        https://github.com/jernejsk/arm-trusted-firmware/archive/e019f64d91ff7c2dfbbfe7f76a14f240761b9edc.tar.gz
Source1000:     trimui-tg5050_defconfig

Patch1001:      0001-configs-add-Trimui-Smart-Pro-S-sun55i-a523-TG5050.patch
Patch1002:      0002-mmc-sunxi-use-PERIPH0-600M-mux-source-for-A523-micro.patch
Patch1003:      0003-sunxi-deterministic-raw-U-Boot-sector-for-A523-128-K.patch
Patch1004:      0004-HACK-avaota-a1-disable-eMMC-for-Trimui-SD-only-bring.patch
Patch1005:      0005-power-axp-add-AXP2202-AXP1530-Trimui-Smart-Pro-S-A52.patch
Patch1006:      0006-sunxi-Trimui-Smart-Pro-S-U-Boot-control-DTB-real-PMI.patch
Patch1007:      0007-power-axp-fix-AXP717-B-C-dcdc4-max-voltage-3700-3400.patch
Patch1008:      0008-sunxi-A523-read-the-U-Boot-FIT-from-the-configured-r.patch
Patch1009:      0009-configs-trimui-smart-pro-s-correct-A523-DRAM-params-.patch

BuildRequires:  bc
BuildRequires:  bison
BuildRequires:  dtc
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  openssl-devel
BuildRequires:  python3
BuildRequires:  swig

%description
The matched mainline U-Boot SPL and FIT images for the TrimUI Smart Pro S
TG5050 boot path. The RPM applies the nine board commits through RPM Patch
preambles and installs artifacts for the board-defined raw boot slots.

%prep
%autosetup -n u-boot-e354b34a6ab4b1887fd451bea8ceb7be146070a8 -p1
mkdir -p ../tfa-a523
%{__tar} -xf %{SOURCE1} -C ../tfa-a523 --strip-components=1
cp %{SOURCE1000} configs/trimui-tg5050_defconfig

%build
export ARCH=arm64
env -u CFLAGS -u CXXFLAGS -u CPPFLAGS -u LDFLAGS \
    make -C ../tfa-a523 PLAT=sun55i_a523 DEBUG=0 \
    ENABLE_STACK_PROTECTOR=none bl31
make trimui-tg5050_defconfig
make olddefconfig
make %{?_smp_mflags} BL31=../tfa-a523/build/sun55i_a523/release/bl31.bin

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/lib/uboot/tg5050
install -m 0644 spl/sunxi-spl.bin \
    %{buildroot}/usr/lib/uboot/tg5050/sunxi-spl.bin
install -m 0644 u-boot-sunxi-with-spl.fit.itb \
    %{buildroot}/usr/lib/uboot/tg5050/u-boot.itb

%files
/usr/lib/uboot/tg5050/sunxi-spl.bin
/usr/lib/uboot/tg5050/u-boot.itb

%changelog
* Sun Sep 06 2026 Ultramarine TG5050 Maintainers <noreply@example.invalid> - 2026.07-1.tg5050
- Build and package the matched TG5050 U-Boot SPL and FIT from source.
- Apply board changes through RPM Patch entries.
