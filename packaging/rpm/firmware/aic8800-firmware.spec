Name:           aic8800-firmware
Version:        2024.06.25
Release:        1.tg5050%{?dist}
Summary:        AIC8800D80 firmware for TrimUI Smart Pro S
License:        GPL-2.0-only
URL:            https://github.com/batocera-linux/aic8800

# Pinned by KNULLI's Batocera package for the AIC8800 firmware set.
Source0:        https://github.com/batocera-linux/aic8800/archive/ccba7fffed8554fe861bd631ff6f852d2d6eec39.tar.gz
# The board-specific config is maintained by the TG5050 mainline DTS repo.
Source1000:     aic_userconfig_8800d80.txt

%global debug_package %{nil}

%description
Firmware for the AIC8800D80 SDIO Wi-Fi/Bluetooth device used by the
TrimUI Smart Pro S TG5050. The firmware payload is sourced from the pinned
KNULLI/Batocera AIC8800 package; the TG5050-specific user configuration is
kept as a separate RPM source input.

%prep
%setup -q -n aic8800-ccba7fffed8554fe861bd631ff6f852d2d6eec39

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/lib/firmware/aic8800D80
cp -a firmware/aic8800D80/. %{buildroot}/usr/lib/firmware/aic8800D80/
install -m 0644 %{SOURCE1000} \
    %{buildroot}/usr/lib/firmware/aic8800D80/aic_userconfig_8800d80.txt

%files
/usr/lib/firmware/aic8800D80/aic_powerlimit_8800d80.txt
/usr/lib/firmware/aic8800D80/aic_userconfig_8800d80.txt
/usr/lib/firmware/aic8800D80/calibmode_8800d80.bin
/usr/lib/firmware/aic8800D80/fmacfw_8800d80_u02.bin
/usr/lib/firmware/aic8800D80/fmacfw_8800d80_u02_ipc.bin
/usr/lib/firmware/aic8800D80/fw_adid_8800d80_u02.bin
/usr/lib/firmware/aic8800D80/fw_ble_scan_ad_filter.bin
/usr/lib/firmware/aic8800D80/fw_patch_8800d80_u02.bin
/usr/lib/firmware/aic8800D80/fw_patch_table_8800d80_u02.bin
/usr/lib/firmware/aic8800D80/lmacfw_rf_8800d80_u02.bin

%changelog
* Sun Sep 06 2026 Ultramarine TG5050 Maintainers <noreply@example.invalid> - 2024.06.25-1.tg5050
- Package the pinned KNULLI/Batocera AIC8800D80 firmware set.
- Override the generic user configuration with the TG5050 board configuration.
