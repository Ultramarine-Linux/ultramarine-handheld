Name:           uboot-images-tg5050
Version:        2026.07
Release:        1.tg5050%{?dist}
Summary:        Fedora-style mainline U-Boot images for TrimUI Smart Pro S
License:        GPL-2.0-only
BuildArch:      noarch
URL:            https://github.com/MidG971/u-boot

# Exact known-good manual-build tree from the pinned MidG971 fork.
Source0:        https://github.com/MidG971/u-boot/archive/a8bb626aea0b0b96e5945ce905e29e85186fc886.tar.gz
Source1:        https://github.com/jernejsk/arm-trusted-firmware/archive/e019f64d91ff7c2dfbbfe7f76a14f240761b9edc.tar.gz
Source1000:     trimui-tg5050_defconfig

%global debug_package %{nil}


BuildRequires:  bc
BuildRequires:  bison
BuildRequires:  dtc
BuildRequires:  flex
BuildRequires:  gcc-aarch64-linux-gnu
BuildRequires:  gcc
BuildRequires:  gnutls-devel
BuildRequires:  libuuid-devel
BuildRequires:  make
BuildRequires:  ncurses-devel
BuildRequires:  openssl-devel
BuildRequires:  openssl-devel-engine
BuildRequires:  sccache
BuildRequires:  perl-interpreter
BuildRequires:  python3
BuildRequires:  python3-devel
BuildRequires:  python3-libfdt
BuildRequires:  python3-setuptools
BuildRequires:  SDL2-devel
BuildRequires:  swig

%description
The matched mainline U-Boot SPL and FIT images for the TrimUI Smart Pro S
TG5050 boot path. The RPM builds the exact pinned MidG971 board tree used by
the known-good manual build and installs artifacts for the board-defined raw
boot slots.

%prep
%autosetup -n u-boot-a8bb626aea0b0b96e5945ce905e29e85186fc886
mkdir -p ../tfa-a523
%{__tar} -xf %{SOURCE1} -C ../tfa-a523 --strip-components=1
cp %{SOURCE1000} configs/trimui-tg5050_defconfig

%build
export ARCH=arm64
unset CFLAGS CXXFLAGS CPPFLAGS LDFLAGS
export CROSS_COMPILE=aarch64-linux-gnu-
CC="${CROSS_COMPILE}gcc"
HOSTCC=gcc
HOSTCXX=g++
if test -x /usr/bin/sccache; then
    sccache_bin=/usr/bin/sccache
    sccache_cc="$(command -v "${CROSS_COMPILE}gcc")"
    sccache_hostcc="$(command -v gcc)"
    sccache_cxx="$(command -v g++)"
    echo "sccache: $sccache_bin"
    "$sccache_bin" --version
    echo "sccache target compiler: $sccache_cc"
    echo "sccache host compiler: $sccache_hostcc"
    CC="$sccache_bin $sccache_cc"
    HOSTCC="$sccache_bin $sccache_hostcc"
    HOSTCXX="$sccache_bin $sccache_cxx"
fi
export CC HOSTCC HOSTCXX
env -u CFLAGS -u CXXFLAGS -u CPPFLAGS -u LDFLAGS \
    make -C ../tfa-a523 CC="$CC" HOSTCC="$HOSTCC" HOSTCXX="$HOSTCXX" PLAT=sun55i_a523 DEBUG=1 \
    ENABLE_STACK_PROTECTOR=none bl31
make CC="$CC" HOSTCC="$HOSTCC" HOSTCXX="$HOSTCXX" trimui-tg5050_defconfig
make CC="$CC" HOSTCC="$HOSTCC" HOSTCXX="$HOSTCXX" olddefconfig
make %{?_smp_mflags} CC="$CC" HOSTCC="$HOSTCC" HOSTCXX="$HOSTCXX" \
    BL31=../tfa-a523/build/sun55i_a523/debug/bl31.bin

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
* Sun Sep 06 2026 Cappy Ishihara <cappy@fyralabs.com> - 2026.07-1.tg5050
- Build and package the matched TG5050 U-Boot SPL and FIT from source.
- Pin the source to the known-good MidG971 TrimUI board tree.
- Build the tested debug TF-A BL31 variant for manual-boot parity.
