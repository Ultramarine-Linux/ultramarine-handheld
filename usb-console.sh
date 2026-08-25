#!/bin/sh
# SPDX-License-Identifier: (GPL-2.0-only OR MIT)
# Copyright (C) 2026 Midgy BALON
#
# usb-console.sh — read the mainline kernel boot console over the usb/dp port's
# USB gadget serial (CDC-ACM), so you get the boot log WITHOUT the physical
# ttyS0 UART pads (no teardown / soldering).
#
# Requires the bring-up kernel built with the gadget serial console
# (kernel/usb-gadget-console.config) + console=ttyGS0,115200 on the cmdline.
# The device then enumerates on THIS host as /dev/ttyACM0 (CDC-ACM) or
# /dev/ttyUSB0 (generic g_serial). Run this on the HOST, then (re)boot the device
# — it waits for any /dev/ttyACM* port to appear and opens it.
# Logging is opt-in with -o.
#
# CAVEAT: the gadget console only exists from USB-gadget init onward — it does
# NOT capture SPL / U-Boot proper or the earliest pre-USB kernel lines. For the
# FEL DRAM-training step (before any USB gadget), validate DRAM serial-free with
# sunxi-fel instead.
#
# Usage: sh usb-console.sh [-b BAUD] [-d /dev/ttyACMx] [-o LOGFILE] [-t SECONDS]

set -u
BAUD=115200
DEV=""
LOG=""
TIMEOUT=0

while [ $# -gt 0 ]; do
    case "$1" in
        -b) BAUD=$2; shift 2 ;;
        -d) DEV=$2; shift 2 ;;
        -o) LOG=$2; shift 2 ;;
        -t) TIMEOUT=$2; shift 2 ;;
        -h|--help)
            sed -n '2,26p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *) echo "unknown option: $1 (see -h)" >&2; exit 2 ;;
    esac
done

find_dev() {
    for d in /dev/ttyACM*; do
        [ -e "$d" ] && printf '%s\n' "$d"
    done | sort -V | tail -n 1
}

if [ -z "$DEV" ]; then
    echo "Waiting for any USB gadget ACM device to appear (/dev/ttyACM*)"
    waited=0
    while ! DEV=$(find_dev); do
        sleep 1
        waited=$((waited + 1))
        if [ "$TIMEOUT" -gt 0 ] && [ "$waited" -ge "$TIMEOUT" ]; then
            echo "Timed out after ${TIMEOUT}s — nothing enumerated." >&2
            echo "Check the gadget serial function and console=ttyGS0,115200." >&2
            exit 1
        fi
    done
fi

REQUESTED_DEV="$DEV"
WAITING_REPORTED=0

while :; do
    if [ -n "$REQUESTED_DEV" ]; then
        DEV="$REQUESTED_DEV"
    else
        DEV=""
        if [ "$WAITING_REPORTED" -eq 0 ]; then
            echo "Waiting for any USB gadget ACM device to appear (/dev/ttyACM*)"
            WAITING_REPORTED=1
        fi
        waited=0
        while ! DEV=$(find_dev); do
            sleep 1
            waited=$((waited + 1))
            if [ "$TIMEOUT" -gt 0 ] && [ "$waited" -ge "$TIMEOUT" ]; then
                echo "Timed out after ${TIMEOUT}s — nothing enumerated." >&2
                echo "Check the gadget serial function and console=ttyGS0,115200." >&2
                exit 1
            fi
        done
        WAITING_REPORTED=0
    fi

    if [ ! -e "$DEV" ]; then
        echo "Console device disappeared: $DEV" >&2
        [ -n "$REQUESTED_DEV" ] || continue
        sleep 1
        continue
    fi

    if [ -n "$LOG" ]; then
        echo "Console device: $DEV @ ${BAUD} 8N1 -> logging to $LOG"
    else
        echo "Console device: $DEV @ ${BAUD} 8N1 (logging disabled)"
    fi
    echo "(exit the terminal program to wait for the next connection.)"

    if command -v picocom >/dev/null 2>&1; then
        if [ -n "$LOG" ]; then
            picocom -b "$BAUD" --imap lfcrlf --logfile "$LOG" "$DEV"
        else
            picocom -b "$BAUD" --imap lfcrlf "$DEV"
        fi
    elif command -v screen >/dev/null 2>&1; then
        if [ -n "$LOG" ]; then
            screen -L -Logfile "$LOG" "$DEV" "$BAUD"
        else
            screen "$DEV" "$BAUD"
        fi
    elif command -v cu >/dev/null 2>&1; then
        if [ -n "$LOG" ]; then
            cu -l "$DEV" -s "$BAUD" | tee "$LOG"
        else
            cu -l "$DEV" -s "$BAUD"
        fi
    else
        command -v stty >/dev/null 2>&1 && \
            stty -F "$DEV" "$BAUD" cs8 -cstopb -parenb raw -echo 2>/dev/null
        if [ -n "$LOG" ]; then
            cat "$DEV" | tee "$LOG"
        else
            cat "$DEV"
        fi
    fi

    echo "Console closed; waiting for the next /dev/ttyACM* connection..."
    [ -n "$REQUESTED_DEV" ] || DEV=""
    sleep 1
done
