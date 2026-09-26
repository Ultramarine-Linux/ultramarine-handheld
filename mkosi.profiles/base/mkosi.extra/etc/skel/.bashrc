# Marina interactive shell
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

export EDITOR=${EDITOR:-nano}
export VISUAL=${VISUAL:-$EDITOR}
export PAGER=${PAGER:-less}

# Keep interactive shells in the same Wayland/session environment as Foot.
if [ -n "${WAYLAND_DISPLAY:-}" ]; then
    export MOZ_ENABLE_WAYLAND=1
    export QT_QPA_PLATFORM=wayland
    export SDL_VIDEODRIVER=wayland
fi
