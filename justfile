set dotenv-load := false

project := justfile_directory()
profile := "tg5050"
profile_justfile := project / "mkosi.profiles" / profile / "justfile"

_default:
    @just --list

# Dispatch semantic artifact recipes to the selected board profile.
env:
    just --justfile {{profile_justfile}} env

rootfs:
    just --justfile {{profile_justfile}} rootfs

rootfs-image:
    just --justfile {{profile_justfile}} rootfs-image

initrd:
    just --justfile {{profile_justfile}} initrd

image:
    just --justfile {{profile_justfile}} image

summary:
    just --justfile {{profile_justfile}} summary

status:
    @git status --short
    @du -sh build/* 2>/dev/null || true
