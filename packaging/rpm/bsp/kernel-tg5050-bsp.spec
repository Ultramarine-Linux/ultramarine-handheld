Name:           kernel-tg5050-bsp
Version:        5.15.147
Release:        1.tg5050%{?dist}
Summary:        Vendor BSP kernel and modules for TrimUI Smart Pro S
License:        GPL-2.0-only AND LicenseRef-Proprietary
URL:            https://github.com/knulli-cfw/knulli-linux
ExclusiveArch:  aarch64

Source0:        vendor-kernel-5.15.147.Image
Source1:        vendor-kernel.dtb
Source2:        aic8800_bsp.ko
Source3:        aic8800_btlpm.ko
Source4:        aic8800_fdrv.ko
Source100:      modules.alias
Source101:      modules.builtin
Source102:      modules.builtin.modinfo
Source103:      modules.dep
Source104:      modules.order
Source105:      modules.softdep
Source106:      modules.symbols
Source107:      trimui-smart-pro-s.conf
Source108:      SHA256SUMS

%global krel 5.15.147
%global debug_package %{nil}

%description
The matched vendor Allwinner BSP kernel payload for the TrimUI Smart Pro S
TG5050. This package is used only by the explicitly selected BSP boot profile;
it is not a replacement for the reproducible mainline kernel package.

%package core
Summary:        Vendor BSP kernel core and board device tree
Provides:       kernel-uname-r = %{krel}
Provides:       kernel-core-uname-r = %{krel}

%description core
The vendor 5.15.147 ARM64 Image, matching TG5050 device tree, and module-load
policy required by the vendor Mali and AIC8800 modules.

%package modules
Summary:        Vendor BSP loadable kernel modules
Requires:       %{name}-core = %{version}-%{release}
Provides:       kernel-modules-uname-r = %{krel}

%description modules
The matched vendor 5.15.147 Mali kbase and AIC8800 loadable modules together
with the module metadata captured from the same BSP kernel.

%prep
mkdir payload
cp -p %{SOURCE0} payload/vendor-kernel-5.15.147.Image
cp -p %{SOURCE1} payload/vendor-kernel.dtb
mkdir payload/modules payload/config
for source in %{SOURCE2} %{SOURCE3} %{SOURCE4} \
    %{SOURCE100} %{SOURCE101} %{SOURCE102} %{SOURCE103} %{SOURCE104} \
    %{SOURCE105} %{SOURCE106}; do
    cp -p "$source" payload/modules/
done
cp -p %{SOURCE107} payload/config/trimui-smart-pro-s.conf
cp -p %{SOURCE108} payload/SHA256SUMS
(cd payload && sha256sum --check --strict SHA256SUMS)

%build
# This is a binary-provenance package; the payload is validated, not rebuilt.
true

%install
rm -rf %{buildroot}
install -D -m 0644 payload/vendor-kernel-5.15.147.Image \
    %{buildroot}/boot/vmlinuz-5.15.147
install -D -m 0644 payload/vendor-kernel.dtb \
    %{buildroot}/usr/lib/tg5050/bsp/sun55i-a523-trimui-smart-pro-s.dtb
install -D -m 0644 payload/config/trimui-smart-pro-s.conf \
    %{buildroot}/usr/lib/modules-load.d/trimui-smart-pro-s.conf
install -d -m 0755 %{buildroot}/usr/lib/modules/%{krel}
for file in aic8800_bsp.ko aic8800_btlpm.ko aic8800_fdrv.ko \
    modules.alias modules.builtin modules.builtin.modinfo modules.dep \
    modules.order modules.softdep modules.symbols; do
    install -D -m 0644 "payload/modules/$file" "%{buildroot}/usr/lib/modules/%{krel}/$file"
done

%files

%files core
/boot/vmlinuz-5.15.147
/usr/lib/tg5050/bsp/sun55i-a523-trimui-smart-pro-s.dtb
/usr/lib/modules-load.d/trimui-smart-pro-s.conf
/usr/lib/modules/%{krel}/modules.builtin
/usr/lib/modules/%{krel}/modules.builtin.modinfo
/usr/lib/modules/%{krel}/modules.order
/usr/lib/modules/%{krel}/modules.softdep
/usr/lib/modules/%{krel}/modules.symbols

%files modules
/usr/lib/modules/%{krel}/aic8800_bsp.ko
/usr/lib/modules/%{krel}/aic8800_btlpm.ko
/usr/lib/modules/%{krel}/aic8800_fdrv.ko
/usr/lib/modules/%{krel}/modules.alias
/usr/lib/modules/%{krel}/modules.dep

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
- Run depmod with the target kernel release so module indexes are generated.
- Package the matched vendor BSP kernel, DTB, and AIC8800 modules.
- Preserve the BSP module metadata and module-load policy as RPM payloads.
