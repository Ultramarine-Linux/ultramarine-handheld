# Start the appliance compositor from the real tty1 PAM/logind session.
if [ -z "${WAYLAND_DISPLAY:-}" ] && [ "$(tty 2>/dev/null)" = /dev/tty1 ]; then
    systemctl --user unset-environment WAYLAND_DISPLAY DISPLAY SWAYSOCK || true
    systemctl --user import-environment \
        XDG_SESSION_ID XDG_SESSION_TYPE XDG_RUNTIME_DIR \
        DBUS_SESSION_BUS_ADDRESS WAYLAND_DISPLAY DISPLAY SWAYSOCK || true
    exec systemctl --user start --wait marina-session.service
fi
