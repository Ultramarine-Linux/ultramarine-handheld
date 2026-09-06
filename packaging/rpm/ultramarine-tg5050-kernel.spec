Name:           ultramarine-tg5050-kernel
Version:        7.2.0
Release:        1.tg5050%{?dist}
Summary:        Mainline Linux kernel artifacts for TrimUI Smart Pro S
License:        GPL-2.0-only
URL:            https://github.com/torvalds/linux
Source0:        kernel-artifacts.tar


%description
The matched Linux 7.2-rc3 kernel image, TrimUI Smart Pro S device tree,
modules, AIC8800 firmware, and initramfs artifacts for the TG5050 mainline
boot path.

%prep
%setup -q -c -T
%{__tar} -xf %{SOURCE0}

%build
# Artifacts are built by the pinned project kernel pipeline.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -a kernel/. %{buildroot}/

%post
/usr/sbin/depmod -a 7.2.0-rc3-dirty >/dev/null 2>&1 || :

%files
/boot/vmlinuz-7.2.0-rc3-dirty
/boot/initramfs-7.2.0-rc3-dirty.img
/boot/initramfs-7.2.0-rc3-dirty-rescue.img
/usr/lib/modules/7.2.0-rc3-dirty
/usr/lib/firmware/aic8800_sdio
/usr/share/tg5050/dtb/sun55i-a523-trimui-smart-pro-s.dtb

%changelog
* Sun Sep 06 2026 Ultramarine TG5050 Maintainers <noreply@example.invalid> - 7.2.0-1.tg5050
- Package the matched TG5050 mainline kernel, modules, firmware, DTB, and initrds.
