Name:           marina-cage
Version:        0.2.0
Release:        1.tg5050%{?dist}
Summary:        Nested Wayland kiosk with forced internal resolution for Marina game containers
License:        MIT
URL:            https://github.com/waydroid-helper/cage
# waydroid-helper cage fork, tag release-202511191018.
Source0:        cage-0.2.0-waydroid-52797b1.tar.gz
# Pinned wlroots from the fork's subprojects/wlroots.wrap
# (ayasa0520/wlroots.git, branch waydroid-helper-new). Vendored so the
# build never hits the network; meson runs with --wrap-mode=nodownload.
Source1:        wlroots-0.19-waydroid-5f05d57.tar.gz

%global cage_tag     release-202511191018
%global cage_commit  52797b1f95d8e912ab4b799b63d6b8bb5ca4f143
%global cage_sha256  10775ce765ddded5242ca2e08886f54cfb8fd3b2ffbd7faa0942f7813a4d696a
%global wlroots_commit 5f05d574f3ed1f73c35cf7aed9277568947386e5
%global wlroots_sha256 9167921a63944232b29133a1d872b131b046b7e5f1dbd84a7099552ab4c2decc

%global debug_package %{nil}

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig
BuildRequires:  scdoc
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  pixman-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  mesa-libGLES-devel
BuildRequires:  mesa-libgbm-devel
BuildRequires:  libdrm-devel
BuildRequires:  libinput-devel
BuildRequires:  libseat-devel
BuildRequires:  libdisplay-info-devel
BuildRequires:  libliftoff-devel
BuildRequires:  lcms2-devel
BuildRequires:  hwdata-devel
BuildRequires:  systemd-devel
BuildRequires:  libxcb-devel
BuildRequires:  xcb-util-devel
BuildRequires:  xcb-util-wm-devel
BuildRequires:  xcb-util-image-devel
BuildRequires:  xcb-util-renderutil-devel
BuildRequires:  xcb-util-errors-devel
BuildRequires:  xorg-x11-server-Xwayland-devel

# Cage is built with Xwayland support, so the Xwayland server must be
# present at runtime for X11 ports. The GLES renderer comes from mesa.
Requires:       xorg-x11-server-Xwayland
Requires:       mesa-dri-drivers

%description
Nested Wayland kiosk compositor for Marina game containers, built from
the waydroid-helper cage fork with its matching wlroots snapshot.

Unlike stock cage, this build adds a logical (internal) resolution that
is independent of the outer window size, with no client-side
decorations and the game binary passed as argv:

  marina-cage -W 720 -H 1280 -w 360 -h 640 -- ./port_binary

The port renders at 360x640 while the compositor presents a 720x1280
window to the parent compositor. Resizing by the parent does not
clobber the logical resolution unless --allow-resize is given. The
GLES2 renderer path works on Panfrost; no Vulkan is required.

The wlroots snapshot is linked statically into the binary, so this
package does not interact with the system's wlroots. The binary is
named marina-cage to avoid any conflict with Fedora's cage package.

%prep
# Verify the pinned sources before touching anything.
echo "%{cage_sha256}  %{SOURCE0}" | sha256sum --check -
echo "%{wlroots_sha256}  %{SOURCE1}" | sha256sum --check -
%setup -q -n cage-%{cage_tag}
rm -rf subprojects/wlroots
mkdir -p subprojects/wlroots
tar -xzf %{SOURCE1} -C subprojects/wlroots --strip-components=1
test -f subprojects/wlroots/meson.build

%build
# - default_library=static: the forked wlroots is private to this
#   binary; its install payload is dropped in %%install.
# - renderers=gles2: Vulkan is unnecessary on this GLES-only target.
# - examples=false: unneeded demo clients.
# - werror=false: snapshot fork, do not fail on new-toolchain warnings.
%meson --wrap-mode=nodownload -Ddefault_library=static -Dwerror=false \
  -Dwlroots:examples=false -Dwlroots:renderers=gles2
%meson_build

%install
%meson_install
# Drop the private wlroots install payload; it is statically linked.
rm -rf %{buildroot}%{_libdir}/libwlroots-0.19* \
  %{buildroot}%{_includedir}/wlroots-0.19 \
  %{buildroot}%{_libdir}/pkgconfig/wlroots-0.19.pc
# Appliance binary name; no conflict with Fedora's cage.
mv %{buildroot}%{_bindir}/cage %{buildroot}%{_bindir}/marina-cage
mv %{buildroot}%{_mandir}/man1/cage.1 %{buildroot}%{_mandir}/man1/marina-cage.1
sed -i -e 's/"cage"/"marina-cage"/' -e 's/^cage /marina-cage /' \
  %{buildroot}%{_mandir}/man1/marina-cage.1

%files
%license LICENSE
%doc README.md
%{_bindir}/marina-cage
%{_mandir}/man1/marina-cage.1*

%changelog
* Thu Sep 24 2026 Cappy Ishihara <cappy@fyralabs.com> - 0.2.0-1.tg5050
- Package the waydroid-helper cage fork as marina-cage for Marina game
  containers: forced logical resolution without client-side decorations.
- Vendor the pinned cage tag and its matching wlroots snapshot with
  SHA-256 verification; meson runs with --wrap-mode=nodownload.
- Link the forked wlroots statically; drop its install payload.
- GLES2 renderer only; Xwayland support retained for X11 ports.
