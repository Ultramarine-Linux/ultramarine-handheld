Name:           kmod-panfrost
Version:        5.15.147
Release:        1.tg5050%{?dist}
Summary:        Source-built Panfrost GPU modules for the TG5050 vendor kernel
License:        GPL-2.0-only
URL:            https://gitlab.com/tina5.0_aiot/lichee/linux-5.15
ExclusiveArch:  aarch64

# The vendor kernel and Radxa GPU overlay are separate source projects.
%global linux_commit 81fb98f097b35a3d41f9d9b334811ca163dbb208
%global radxa_commit 87387566b989bef746d55117880259498ba496db
Source0:        https://gitlab.com/tina5.0_aiot/lichee/linux-5.15/-/archive/%{linux_commit}/linux-5.15-%{linux_commit}.tar.gz
Source1:        https://github.com/radxa/allwinner-bsp/archive/%{radxa_commit}/allwinner-bsp-%{radxa_commit}.tar.gz
Source2:        kmod-panfrost.conf
Source3:        kmod-panfrost.config
Source4:        0001-external-shmem-module-license.patch

%global krel 5.15.147
%global debug_package %{nil}

Requires:       kernel-tg5050-bsp-core = %{version}-%{release}
Provides:       kmod-panfrost = %{version}-%{release}

%description
Panfrost, DRM scheduler, and DRM GEM shmem helper modules built from the pinned
vendor Linux 5.15 source plus the pinned Radxa Allwinner GPU overlay. This
package replaces the proprietary mali_kbase module for the Panfrost/Mesa stack.

%prep
%setup -q -n linux-5.15-%{linux_commit}
mkdir -p bsp
 tar -xf %{SOURCE1} --strip-components=1 -C bsp
cp -p %{SOURCE2} %{SOURCE3} .
install -D -m 0644 bsp/configs/linux-5.15/sun55iw3p1_min_defconfig \
    arch/arm64/configs/sun55iw3p1_min_defconfig
mkdir external-shmem
cp -p drivers/gpu/drm/drm_gem_shmem_helper.c external-shmem/
printf '%s\n' 'obj-m += drm_gem_shmem_helper.o' > external-shmem/Makefile
patch -p0 < %{SOURCE4}

%build
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
export CC=aarch64-linux-gnu-gcc
export HOSTCC=gcc
export KBUILD_MODPOST_WARN=1
export BSP_TOP="$PWD/bsp/"
make BSP_TOP="$BSP_TOP" sun55iw3p1_min_defconfig
./scripts/kconfig/merge_config.sh -m .config kmod-panfrost.config
./scripts/config --set-val CONFIG_DRM_SCHED m
./scripts/config --set-val CONFIG_DRM_GEM_SHMEM_HELPER m
./scripts/config --set-val CONFIG_AW_DRM_PANFROST m
make BSP_TOP="$BSP_TOP" olddefconfig
make modules_prepare
make %{?_smp_mflags} M=drivers/gpu/drm/scheduler modules
make %{?_smp_mflags} M=drivers/gpu/drm modules
make %{?_smp_mflags} M=external-shmem modules
make %{?_smp_mflags} M=bsp/drivers/gpu/panfrost modules

%install
rm -rf %{buildroot}
install -D -m 0644 drivers/gpu/drm/scheduler/gpu-sched.ko \
    %{buildroot}/usr/lib/modules/%{krel}/extra/panfrost/gpu-sched.ko
install -D -m 0644 external-shmem/drm_gem_shmem_helper.ko \
    %{buildroot}/usr/lib/modules/%{krel}/extra/panfrost/drm_gem_shmem_helper.ko
install -D -m 0644 bsp/drivers/gpu/panfrost/panfrost.ko \
    %{buildroot}/usr/lib/modules/%{krel}/extra/panfrost/panfrost.ko
install -D -m 0644 kmod-panfrost.conf \
    %{buildroot}/usr/lib/modules-load.d/kmod-panfrost.conf

%files
/usr/lib/modules/%{krel}/extra/panfrost
/usr/lib/modules-load.d/kmod-panfrost.conf

%post
if [ -x %{_sbindir}/depmod ]; then
    %{_sbindir}/depmod -a %{krel} || :
fi

%postun
if [ -x %{_sbindir}/depmod ]; then
    %{_sbindir}/depmod -a %{krel} || :
fi

%changelog
* Sat Sep 12 2026 Cappy Ishihara <cappy@fyralabs.com> - 5.15.147-1.tg5050
- Build Panfrost and its DRM helper modules from pinned Git sources.
- Package the modules separately from the vendor BSP kernel package.
