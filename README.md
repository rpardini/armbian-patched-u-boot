#### u-boot patching: 3 total patches; 3 applied; 0 with problems

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `board.odroidhc4.hc4_sd_defconfig.for.writing.to.mtd` | `(+77/-0)[1A]` | b0b6ad5132391aa5f5a27c509219885194bdf242 `odroid-hc4_sd_defconfig` | `Ricardo Pardini` _odroidhc4: add a marker boot-from-SD-write-to-SPI defconfig for the HC4 based the C4 DT_ |
| ✅  | `board.odroidhc4.preboot.pci.enum.usb.start` | `(+2/-0)[1M]` | bd5adadd869d1ed9dd40ae6876ef02f5ba887672 `odroid-hc4_defconfig` | `Ricardo Pardini` _odroidhc4: u-boot: spi: add pci enum & usb start to preboot_ |
| ✅  | `meson64-boot-usb-nvme-scsi-first` | `(+3/-3)[1M]` | 15e6bd35d809475765caee7d6b02fec4efd3c495 `meson64.h` | `Ricardo Pardini` _meson64: change `BOOT_TARGET_DEVICES` to try to boot USB, NVME and SCSI before SD, MMC, PXE, DHCP_ |


