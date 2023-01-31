#### u-boot patching: 3 total patches; 3 applied; 0 with problems

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `board.odroidhc4.preboot.pci.enum.usb.start` | `(+2/-0)[1M]` | 9b858f4e5edda74de56d310a15868b5f7db34d8c `odroid-hc4_defconfig` | `Ricardo Pardini` _odroidhc4: u-boot: spi: add pci enum & usb start to preboot_ |
| ✅  | `board.odroidhc4.sd.config.sans.spi` | `(+77/-0)[1A]` | 6d5d5e287f787d0e1c705e6c1a0ceae7de112f74 `odroid-hc4_sd_defconfig` | `Ricardo Pardini` _odroidhc4: add a marker boot-from-SD-write-to-SPI defconfig for the HC4 based the C4 DT_ |
| ✅  | `meson64-boot-usb-nvme-scsi-first` | `(+3/-3)[1M]` | 58c4a508f3722fd57be084f314d6f90050b52f2a `meson64.h` | `Ricardo Pardini` _meson64: change `BOOT_TARGET_DEVICES` to try to boot USB, NVME and SCSI before SD, MMC, PXE, DHCP_ |


