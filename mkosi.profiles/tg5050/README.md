# Trimui Smart Pro S (TG5050)

this board is based on the Allwinner A523 platform.

Currently there are two profiles; BSP package and mainline kernel.

the BSP package profile currently uses a custom Tina Linux patchset, based on reverse-engineering
the stock BSP package.

There is also the actual stock Tina Linux kernel image that came with the BSP package from the stock
eMMC image, which has less features than our custom kernel

The custom patchset does not support suspend/resume properly at the moment, as the DSI display panel
breaks and fails to reinitialize after resume.

However, our distro config comes with an Android-style idle mode that works around this issue by using cgroups and suspending things safely enough to avoid the panel issues. This still pins the Display Engine and Video Engine to active though, so the idle mode is not a perfect solution, battery life will be affected until the panel issues are resolved.

## Mainline profile

The mainline profile is based on kernel 7.2.0, with [MidG971's patches](https://github.com/MidG971/trimui_mainline_dts/) staging towards the actual mainline kernel.

Display also does not work properly as of yet with the mainline kernel.


## display issues

The display initialization breaks on both paths and requires a full cold boot to work properly.
by "full cold boot" means that you must power off the device completely, remove the battery, wait
for the board to discharge completely, then power it back on with the battery reinserted.

This is a very annoying process that is mechanically intensive and may damage the JST connector. so beware.

I managed to break the JST PH-3(?) board-side connector doing this, so uh, be careful because it's insanely hard to remove the battery from that JST connector, and then it breaks and becomes loose and damaged. fortunately it's not that hard to replace because it's a standard 2mm JST PH-3 connector. still very annoying and requires solder work to replace.

-cappy