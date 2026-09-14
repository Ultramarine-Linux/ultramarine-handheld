Name:           kmod-zram-bsp
Version:        5.15.147
Release:        1.tg5050%{?dist}
Summary:        zram and zsmalloc modules for the TG5050 vendor kernel
License:        GPL-2.0-only
URL:            https://gitlab.com/tina5.0_aiot/lichee/linux-5.15
ExclusiveArch:  aarch64

%global linux_commit 81fb98f097b35a3d41f9d9b334811ca163dbb208
%global radxa_commit 87387566b989bef746d55117880259498ba496db
Source0:        https://gitlab.com/tina5.0_aiot/lichee/linux-5.15/-/archive/%{linux_commit}/linux-5.15-%{linux_commit}.tar.gz
Source1:        https://github.com/radxa/allwinner-bsp/archive/%{radxa_commit}/allwinner-bsp-%{radxa_commit}.tar.gz
Source2:        kmod-zram-bsp.config
Source3:        kmod-zram-bsp.conf

%global krel 5.15.147
%global debug_package %{nil}

Requires:       kernel-tg5050-bsp-core = %{version}-%{release}
Provides:       kmod-zram = %{version}-%{release}

%description
Out-of-tree zsmalloc and zram modules built against the exact TG5050 vendor
5.15.147 kernel source and configuration. The matched vendor kernel is a
binary-provenance payload and is not rebuilt by this package.

%prep
%setup -q -n linux-5.15-%{linux_commit}
mkdir -p bsp
 tar -xf %{SOURCE1} --strip-components=1 -C bsp
cp -p %{SOURCE2} .
install -D -m 0644 bsp/configs/linux-5.15/sun55iw3p1_min_defconfig \
    arch/arm64/configs/sun55iw3p1_min_defconfig
mkdir external-zsmalloc
cp -p mm/zsmalloc.c external-zsmalloc/
printf '%s\n' 'obj-m += zsmalloc.o' > external-zsmalloc/Makefile
mkdir external-lz4
cp -p crypto/lz4.c external-lz4/crypto_lz4.c
printf '%s\n' 'obj-m += crypto_lz4.o' > external-lz4/Makefile
mkdir external-lz4-lib
cp -p lib/lz4/lz4_compress.c external-lz4-lib/
cp -p lib/lz4/lz4defs.h external-lz4-lib/
printf '%s\n' 'obj-m += lz4_compress.o' > external-lz4-lib/Makefile

%build
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
export CC=aarch64-linux-gnu-gcc
export HOSTCC=gcc
export KBUILD_MODPOST_WARN=1
export BSP_TOP="$PWD/bsp/"
make BSP_TOP="$BSP_TOP" sun55iw3p1_min_defconfig
./scripts/kconfig/merge_config.sh -m .config kmod-zram-bsp.config
./scripts/config --set-val CONFIG_ZSMALLOC m
./scripts/config --set-val CONFIG_ZRAM m
make BSP_TOP="$BSP_TOP" olddefconfig
./scripts/config --set-val CONFIG_ZSMALLOC m
./scripts/config --set-val CONFIG_ZRAM m
./scripts/config --set-val CONFIG_ZRAM_DEF_COMP_LZ4 y
./scripts/config --set-val CONFIG_CRYPTO_LZ4 m
make syncconfig
make modules_prepare
make %{?_smp_mflags} M=external-zsmalloc modules
make %{?_smp_mflags} M=external-lz4-lib modules
make %{?_smp_mflags} M=external-lz4 modules
make %{?_smp_mflags} M=drivers/block/zram modules

%install
rm -rf %{buildroot}
install -D -m 0644 external-zsmalloc/zsmalloc.ko \
    %{buildroot}/usr/lib/modules/%{krel}/extra/zram/zsmalloc.ko
install -D -m 0644 drivers/block/zram/zram.ko \
    %{buildroot}/usr/lib/modules/%{krel}/extra/zram/zram.ko
install -D -m 0644 external-lz4/crypto_lz4.ko \
    %{buildroot}/usr/lib/modules/%{krel}/extra/zram/crypto_lz4.ko
install -D -m 0644 external-lz4-lib/lz4_compress.ko \
    %{buildroot}/usr/lib/modules/%{krel}/extra/zram/lz4_compress.ko
install -D -m 0644 %{SOURCE3} \
    %{buildroot}/usr/lib/modules-load.d/kmod-zram-bsp.conf

%files
/usr/lib/modules/%{krel}/extra/zram
/usr/lib/modules-load.d/kmod-zram-bsp.conf

%post
if [ -x %{_sbindir}/depmod ]; then
    %{_sbindir}/depmod -a %{krel} || :
fi

%postun
if [ -x %{_sbindir}/depmod ]; then
    %{_sbindir}/depmod -a %{krel} || :
fi

%changelog
* Mon Sep 14 2026 Cappy Ishihara <cappy@fyralabs.com> - 5.15.147-1.tg5050
- Build zsmalloc and zram separately against the matched binary BSP kernel ABI.
