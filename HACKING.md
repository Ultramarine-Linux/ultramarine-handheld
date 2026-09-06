# Hacking the TG5050 image

This document records board bring-up procedures that are easy to forget or
misinterpret. The target is the TrimUI Smart Pro S / TG5050 image.

## Running Sway over SSH with logind seat ownership

For a normal installed image, prefer `greetd` instead of launching Sway from
SSH. `greetd` creates the PAM/logind session and starts the compositor from
the real VT, avoiding the activation race described below.

The image configuration installs `greetd` and `tuigreet`, writes:

```toml
[terminal]
vt = 1

[default_session]
command = "tuigreet --time --remember --cmd sway"
user = "cappy"

[initial_session]
command = "sway"
user = "cappy"
```

and enables `greetd.service` while masking `getty@tty1.service` and disabling
`ultramarine-kms-journal.service`. The `initial_session` autologins `cappy` to
Sway once per boot; `default_session` is the fallback `tuigreet` screen after
that session exits. Those services must not compete with greetd for tty1/DRM.

For a live root mutation during bring-up:

```bash
sudo dnf install -y greetd tuigreet
sudo install -d -m 0755 /etc/greetd
sudoedit /etc/greetd/config.toml
sudo systemctl disable ultramarine-kms-journal.service
sudo systemctl mask getty@tty1.service
sudo systemctl enable --now greetd.service
```

Verify the greeter session with:

```bash
loginctl list-sessions
systemctl status greetd.service
```

The expected greeter session has `USER=cappy`, `SEAT=seat0`, `CLASS=greeter`,
and `TTY=tty1`. Sway will not own `/dev/dri/card0` until a user logs in
through `tuigreet`.

SSH is not a graphical logind seat. Starting `sway` directly over SSH causes
wlroots to wait for an active DRM session and eventually fail with:

```text
Timeout waiting session to become active
Failed to start a DRM session
```

The working arrangement is:

```text
systemd-run + PAM login session
  → cappy session on tty1
  → loginctl activates that session on seat0
  → sway starts after activation
  → wlroots acquires /dev/dri/card0
```

The test below is intentionally transient. It does not install a persistent
service or alter the image.

### Preconditions

Use the board's root SSH access. The example assumes:

- user: `cappy` (UID 1000)
- VT: `tty1`
- DRM device: `/dev/dri/card0`
- compositor: `/usr/bin/sway`

Stop other services that may own the VT or DRM device:

```bash
sudo systemctl stop getty@tty1.service
sudo systemctl stop ultramarine-kms-journal.service 2>/dev/null || true
```

### Start the delayed compositor session

Run this as root. The delay is deliberate: it gives systemd/logind time to
create the PAM-backed session before Sway asks wlroots for DRM.

```bash
systemd-run \
  --unit=wayland-test \
  --property=User=cappy \
  --property=UtmpIdentifier=tty1 \
  --property=UtmpMode=user \
  --property=PAMName=login \
  --property=TTYPath=/dev/tty1 \
  --property=StandardInput=tty-fail \
  --property=StandardOutput=journal \
  --property=StandardError=journal \
  --property=TTYVHangup=yes \
  --property=TTYReset=yes \
  --setenv=XDG_RUNTIME_DIR=/run/user/1000 \
  /bin/sh -c 'sleep 15; exec sway -d'
```

Use a unique unit name if an earlier transient unit is still loaded, for
example `--unit=wayland-test2`.

### Activate the logind session

From a second root SSH connection, find the session whose user is `cappy` and
whose TTY is `tty1`:

```bash
loginctl list-sessions
```

There may also be a second `cappy` session with no TTY and no seat. Do not
activate that one. Activate the `tty1` session:

```bash
loginctl activate SESSION_ID
```

Verify the result:

```bash
loginctl show-session SESSION_ID \
  -p Name -p User -p Seat -p TTY -p Active -p Remote
```

The expected state is:

```text
Name=cappy
User=1000
Seat=seat0
TTY=tty1
Active=yes
Remote=no
```

Sway should then remain running and own both devices:

```bash
fuser -v /dev/dri/card0 /dev/tty1
```

A successful test shows the `cappy` Sway process using `/dev/dri/card0` and
`/dev/tty1`.

### Cleanup

Stop the transient unit:

```bash
systemctl stop wayland-test.service
```

If the normal boot journal console is desired again:

```bash
systemctl start ultramarine-kms-journal.service
```

Do not run Sway, `getty@tty1.service`, and the KMS journal console together;
they compete for the same VT/DRM path.

### Why `PAMName=login` matters

The important distinction is between a process running as user `cappy` and a
real local logind session. `User=cappy` changes credentials, but the PAM and
TTY properties cause systemd to open a session that logind can associate with
`seat0`:

```text
User=cappy
PAMName=login
TTYPath=/dev/tty1
UtmpIdentifier=tty1
UtmpMode=user
StandardInput=tty-fail
```

Opening the PAM session is not sufficient by itself. It must also be active.
`loginctl activate` is the step that makes the session the foreground owner of
`seat0`; `chvt 1` alone does not create or activate a logind session.

## Testing Cage instead of Sway

Cage is suitable for one fullscreen application:

```bash
... /usr/bin/cage -- /path/to/application
```

Cage is not a replacement for Sway when the shell needs `wlr-layer-shell`
panels, overlays, launchers, or virtual-keyboard surfaces.
