#### u-boot patching: 6 total patches; 6 applied; 0 with problems

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `0001-pci-pcie_dw_rockchip-increase-PCIe-LTSSM-timeout-for-cold-boot` | `(+2/-2)[1M]` | b6d2b6b7e94be9ff8ac34400a7263a20974be7ac `pcie_dw_rockchip.c` | `Robert Pahle` _pci: pcie_dw_rockchip: increase PCIe retry count for Rock 5B cold boot_ |
| ✅  | `1001-fdt_fixup_ethernet-add-logs` | `(+59/-15)[2M]` | 547ab9eda4428d21b471e19887f822cb4c7f29db `fdt_support.c`, `image-fdt.c` | `Ricardo Pardini` _fdt_fixup_ethernet: add logs_ |
| ✅  | `cmd-fileenv-read-string-from-file-into-env` | `(+52/-0)[2M, 1A]` | aaf13d698615fdfee8396261322ce24bdbca949f `fileenv.c`, `Kconfig`, `Makefile` | `Ricardo Pardini` _cmd: fileenv: read string from file into env_ |
| ✅  | `general-fix-btrfs-zstd-decompression` | `(+72/-4)[1M]` | b4a6785d7bc9e8855083e87580b8df6cbfa12049 `compression.c` | `Igor Velkov` _fs: btrfs: fix zstd decompression for BTRFS extents_ |
| ✅  | `general-rk3588-add-i2s-mclk-output-to-io-clock-ids` | `(+4/-0)[1M]` | 39a507d92acc0e559bab0155715e292919fa7d33 `rockchip,rk3588-cru.h` | `SuperKali` _dt-bindings: clock: rockchip,rk3588-cru: add I2S MCLK output to IO clock IDs_ |
| ✅  | `mtd-spi-nor-Add-support-for-Zbit-ZB25LQ128` | `(+2/-0)[1M]` | 55bde8fcbd63f0ac7607b1d4e361fdbf479e9a14 `spi-nor-ids.c` | `Ricardo Pardini` _mtd: spi-nor: Add support for Zbit ZB25LQ128_ |


