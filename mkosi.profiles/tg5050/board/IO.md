# TrimUI Smart Pro S hardware I/O

This documents the verified Knulli reference behavior and the current
Ultramarine implementation.

## Integrated controls and rumble

The Smart Pro S controller is not exposed directly by the two controller MCUs.
The userspace daemon reads the vendor serial endpoints:

```text
/dev/ttyAS5  left controller half
/dev/ttyAS7  right controller half
```

and publishes one uinput device:

```text
TRIMUI Smart Pro S Controller
```

The source-backed daemon lives in the `korewaChino/Trimui_Inputd` fork. It
contains runtime stick calibration (startup center learning, filtering,
adaptive deadzone, span learning, and parked-stick recentering), plus the
Smart Pro S `pwm-vibrator` force-feedback backend. The current development
image temporarily carries the tested ARM64 daemon as a separate board
`ExtraTrees` input until the fork is integrated as a normal source build.

The physical motor is a kernel input device, not a GPIO userspace motor:

```text
/dev/input/by-path/platform-soc@3000000:pwm_vibrator-event
/sys/class/thermal/cooling_device0  pwm-fan
```

FF applications can address the vibrator through its `event` node. The
input daemon forwards FF upload/play/erase requests from its virtual gamepad
to that kernel endpoint. Knulli's reference implementation also exposes
this as a separate `pwm-vibrator` input device.

## Audio

The vendor kernel exposes the internal codec through ordinary ALSA:

```text
card 0: audiocodec
playback: digital audio playback, device 0
capture:  digital audio capture, device 0
```

The kernel-side codec path is therefore usable by PipeWire. Knulli runs
PipeWire/WirePlumber above ALSA, but explicitly disables ACP and UCM for this
board and configures the built-in speaker node directly. Its relevant policy
is:

```text
ALSA card/device: audiocodec, device 0
format:           S16LE
rate:             48000 Hz
channels:        2
soft mixer:       enabled
mmap:             disabled for the speaker node
```

That is the sensible Ultramarine approach too: use PipeWire for the session
and routing layer, while keeping an explicit WirePlumber ALSA rule for the
vendor `audiocodec` card instead of assuming desktop UCM profiles exist.
PipeWire should be tested against the capture path separately; playback is the
important initial target.

The hardware mixer remains available through ALSA controls. Knulli's volume
keys ultimately adjust the PipeWire system volume, while low-level board
helpers use `amixer` for codec-specific controls such as `DAC` and
`DACL DACR Swap`. The vendor kernel and codec driver remain unchanged.

Useful first-pass checks once the packages are installed are:

```bash
cat /proc/asound/cards
aplay -l
arecord -l
wpctl status
pw-play --target <sink> test.wav
```

## Brightness and display power

The live panel uses the standard raw backlight interface:

```text
/sys/class/backlight/backlight0/brightness
/sys/class/backlight/backlight0/max_brightness   # 255
/sys/class/backlight/backlight0/actual_brightness
/sys/class/backlight/backlight0/bl_power
```

Knulli's `knulli-brightness` helper discovers the first backlight directory,
uses a minimum of 1% (with a raw floor of 3), and supports percentage values,
`+/-` changes, cycling, dimming, and display off/on. It stores the previous
brightness under `/var/run/` while dimmed or off and optionally updates the
RGB lighting service. Its fallback path uses `/sys/class/graphics/fb0/blank`
when no backlight device exists.

For this board, direct development control is simply:

```bash
cat /sys/class/backlight/backlight0/brightness
echo 128 > /sys/class/backlight/backlight0/brightness
```

Applications should discover `/sys/class/backlight/*` rather than assume the
`backlight0` name. The KMS console's DPMS timeout is separately disabled with
`--dpms-timeout 0`; that controls inactivity blanking, not the backlight level.

## CPU frequency and governor control

The vendor 5.15 kernel exposes two cpufreq policies:

```text
policy0: little cluster, 408000..1416000 kHz
policy4: big cluster,    408000..2160000 kHz
```

The live driver is `cpufreq-dt`. Available governors on the current image are:

```text
conservative ondemand userspace powersave performance schedutil
```

Knulli applies one governor to every policy. Its reference startup logic
prefers the saved setting, otherwise `schedutil`, and finally `performance`.
It writes:

```text
/sys/devices/system/cpu/cpufreq/policy*/scaling_governor
```

Knulli's `knulli-overclock` helper controls the per-policy ceiling through:

```text
/sys/devices/system/cpu/cpufreq/policy*/scaling_max_freq
```

It enumerates each policy's `scaling_available_frequencies`, clamps the
requested frequency to a value supported by every policy, and restores a
board-specific default when requested. On this board the policy tables must
be treated independently: the big cluster can reach 2160000 kHz while the
little cluster tops out at 1416000 kHz.

Useful development commands on the running image are:

```bash
# inspect policies and governors
for p in /sys/devices/system/cpu/cpufreq/policy*; do
    echo "[$p]"
    cat "$p/scaling_available_frequencies" 2>/dev/null
    cat "$p/scaling_governor" "$p/scaling_min_freq" "$p/scaling_max_freq"
done

# set a governor across all policies
for p in /sys/devices/system/cpu/cpufreq/policy*; do
    echo schedutil > "$p/scaling_governor"
done

# set policy ceilings, using values present in each policy's table
echo 1416000 > /sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq
echo 2160000 > /sys/devices/system/cpu/cpufreq/policy4/scaling_max_freq
```

Ultramarine uses Fedora's standard `tuned` daemon with `tuned-ppd` for the
power-profiles-daemon compatibility API. It overrides the stock named TuneD
profiles in `/etc/tuned/profiles/` to preserve dynamic DDR scaling without
changing PPD's standard mapping:

```text
power-saver → powersave
balanced    → balanced
on battery  → balanced-battery
performance → throughput-performance
```

Each named profile retains its Fedora behavior and adds
`/sys/class/devfreq/3120000.dmcfreq/governor=simple_ondemand`. The balanced
profile selects `schedutil` for both CPU policies. Thermal cpufreq cooling
remains the emergency backstop rather than a normal idle-power policy.

## GPU and DDR devfreq

The vendor `mali_kbase` driver exposes the GPU through:

```text
/sys/class/devfreq/1800000.gpu
```

At confirmed idle, it uses `simple_ondemand`, remains at its 150 MHz minimum,
and runtime-suspends the GPU; an 888 MHz PLL rate alone is not evidence that
the PLL is enabled. Inspect the debugfs enable counts before attributing heat to
the GPU.

The DDR controller is separately exposed at:

```text
/sys/class/devfreq/3120000.dmcfreq
```

The vendor default `performance` governor pins it at 1.2 GHz even when Mali is
runtime-suspended. The board TuneD profiles set it to `simple_ondemand`, which
reached 150 MHz during idle validation. Do not force a GPU ceiling until an
actual GPU-utilisation trace proves it is the hot component.

### Handheld clock-control contract

The future handheld software stack should expose clock domains by discovering
the live sysfs controls, not by hardcoding a single shared clock value:

```text
CPU little  /sys/devices/system/cpu/cpufreq/policy0
CPU big     /sys/devices/system/cpu/cpufreq/policy4
GPU         /sys/class/devfreq/1800000.gpu
DDR         /sys/class/devfreq/3120000.dmcfreq
```

For every domain, report its current frequency, governor, min/max bounds, and
`scaling_available_frequencies` or `available_frequencies`. A ceiling request
must be validated against that domain's own OPP list. The CPU UI may offer a
single target ceiling only by rounding down independently for each policy: the
little cluster tops out at 1416 MHz, while the big cluster reaches 2160 MHz.

The supported controls are governor selection plus validated `min_freq` and
`max_freq` bounds. `schedutil` (CPU) and `simple_ondemand` (GPU/DDR) are the
normal dynamic modes. Exact fixed-frequency mode must be capability-probed when
switching a devfreq domain to its `userspace` governor; do not expose a fixed
clock control until the vendor driver's runtime sysfs interface has been
verified. The privileged broker/UI belongs in the separate handheld-software
repository, while this board image owns only the hardware contract and TuneD
defaults.

## Fan and thermal control

Knulli's A527 reference starts `knulli-fan-control` from
`board/allwinner/a527/fsoverlay/etc/init.d/S06fan-control-daemon`. For the
Smart Pro S it writes the thermal cooling state:

```text
/sys/class/thermal/cooling_device0/cur_state
```

with a range of `0..31`, using the hottest `cpu*`/`cluster*` thermal zone.
Its default temperature ramp is:

```text
below 30 C: fan off
35 C:       minimum ramp point
80 C:       maximum ramp point
```

The vendor `pwm-fan` is also exposed through hwmon as `pwmfan` / `pwm1`, while
the big-cluster thermal zone is a direct thermal-sysfs input. Ultramarine ships
the standard `lm_sensors` `fancontrol.service` with an absolute-path
configuration mapping those paths: 35°C stops the fan, 80°C reaches PWM 255,
and a stopped fan restarts at PWM 180. There is no tachometer, so `FCFANS` is
intentionally empty. `pwmconfig` remains useful for an interactive physical
minimum-start test if the curve needs further tuning.

## Power, display, and other I/O

- `axp2202-pek` is `/dev/input/event2` on the inspected boot. The power-toggle
  service discovers it by name rather than relying on that event number: a
  short `KEY_POWER` press toggles `/sys/class/backlight/*/bl_power` between 0
  and 4, while logind retains long press as poweroff.
- `pwm-vibrator` is `/dev/input/event1` on the current boot, but applications
  should use its `/dev/input/by-path/` link rather than the event number.
- The KMS journal console uses kmscon with `--dpms-timeout 0`; the default
  600-second screen blanking is disabled.
- Early USB ConfigFS RNDIS uses dynamic UDC discovery and identifies the
  board from device-tree/runtime identity; it does not hardcode the
  `sun55iw3` model as a controller selector.
- A serial getty is enabled on `ttyAS0`; the controller daemon uses `ttyAS5`
  and `ttyAS7`.
- `axp2202-battery` and `axp2202-usb` provide battery/charger state through
  `/sys/class/power_supply/`. Vendor boot0/boot-package/p3 remain intact for
  charger mode, boot indicators, panel bring-up, and other pre-userspace
  behavior.

## USB gadget

The direct p4 rootfs enables an early ConfigFS RNDIS gadget on the bottom USB-C
gadget port. It assigns the device `192.168.42.1/24`; this is the preferred
bring-up path for SSH and logs. The top USB-C port is host-only.

The gadget service discovers the actual UDC through `/sys/class/udc/` and
derives descriptor identity from the live device tree and board serial rather
than hardcoding a SoC/controller name or image machine-id.

## Serial console

A serial getty is enabled on `ttyAS0`, but physical UART access requires the
debug header. The controller daemon uses `ttyAS5` and `ttyAS7` independently.
