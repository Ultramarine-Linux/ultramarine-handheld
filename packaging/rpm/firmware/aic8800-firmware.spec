Name:           aic8800-firmware
Version:        2024.06.25
Release:        3.tg5050%{?dist}
Summary:        AIC8800D80 firmware for TrimUI Smart Pro S
License:        GPL-2.0-only
URL:            https://github.com/knulli-cfw/knulli-linux
BuildArch:      noarch
BuildRequires:  coreutils

# KNULLI's board overlay matches every file from the working manual-build commit
# 30efb20218b29d7f170f5419ea6b7bd05c027455, including the user configuration.
# Do not substitute the generic Batocera AIC8800 firmware collection.
# Keep Version for upgrade ordering; it is not a date claim about these blobs.
%global firmware_commit 0b1fd94415ba6e35e2715b72b7a7757efee41e81
%global firmware_url https://raw.githubusercontent.com/knulli-cfw/knulli-linux/%{firmware_commit}/board/allwinner/a527/fsoverlay/lib/firmware/aic8800d80

Source0:        stock-firmware.sha256
Source1:        %{firmware_url}/fmacfw_8800d80_h_u02.bin
Source2:        %{firmware_url}/fmacfw_8800d80_u02.bin
Source3:        %{firmware_url}/fw_adid_8800d80_u02.bin
Source4:        %{firmware_url}/fw_patch_8800d80_u02.bin
Source5:        %{firmware_url}/fw_patch_8800d80_u02_ext0.bin
Source6:        %{firmware_url}/fw_patch_table_8800d80_u02.bin
Source7:        %{firmware_url}/lmacfw_rf_8800d80_u02.bin
Source1000:     %{firmware_url}/aic_userconfig_8800d80.txt
Source1001:     README.md

%global debug_package %{nil}

%description
Firmware for the AIC8800D80 SDIO Wi-Fi/Bluetooth device used by the
TrimUI Smart Pro S TG5050. Includes the stock D80 firmware and configuration
used by the known-working manual build, verified against pinned SHA-256
digests before installation.

%prep
%setup -q -c -T
mkdir firmware
install -m 0644 %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} \
    %{SOURCE5} %{SOURCE6} %{SOURCE7} %{SOURCE1000} firmware/
(cd firmware && sha256sum --check %{SOURCE0})
cp %{SOURCE1001} README.md

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/lib/firmware/aic8800D80
cp -a firmware/. %{buildroot}/usr/lib/firmware/aic8800D80/
mkdir -p %{buildroot}/usr/lib/firmware/aic8800_sdio
cp -a firmware/. %{buildroot}/usr/lib/firmware/aic8800_sdio/

%files
%doc README.md
/usr/lib/firmware/aic8800D80
/usr/lib/firmware/aic8800_sdio

%changelog
* Tue Sep 08 2026 Cappy Ishihara <cappy@fyralabs.com> - 2024.06.25-3.tg5050
- Restore the complete known-working stock D80 firmware and configuration.
- Fetch all eight files from a pinned KNULLI A527 board overlay commit.
- Verify Sources against the manual-build commit's SHA-256 digests.
- Package architecture-independent firmware as noarch.

* Mon Sep 07 2026 Cappy Ishihara <cappy@fyralabs.com> - 2024.06.25-2.tg5050
- Add the flat aic8800_sdio firmware layout required by the out-of-tree driver.

* Sun Sep 06 2026 Cappy Ishihara <cappy@fyralabs.com> - 2024.06.25-1.tg5050
- Package the pinned KNULLI/Batocera AIC8800D80 firmware set.
- Override the generic user configuration with the TG5050 board configuration.
