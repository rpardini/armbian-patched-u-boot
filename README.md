#### u-boot patching: 11 total patches; 11 applied; 1 with problems; 1 needs_rebase

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `0001-pci-pcie_dw_rockchip-increase-PCIe-LTSSM-timeout-for-cold-boot` | `(+2/-2)[1M]` | b6d2b6b7e94be9ff8ac34400a7263a20974be7ac `pcie_dw_rockchip.c` | `Robert Pahle` _pci: pcie_dw_rockchip: increase PCIe retry count for Rock 5B cold boot_ |
| ✅  | `1001-fdt_fixup_ethernet-add-logs` | `(+59/-15)[2M]` | 547ab9eda4428d21b471e19887f822cb4c7f29db `fdt_support.c`, `image-fdt.c` | `Ricardo Pardini` _fdt_fixup_ethernet: add logs_ |
| ✅  | `cmd-fileenv-read-string-from-file-into-env` | `(+52/-0)[2M, 1A]` | aaf13d698615fdfee8396261322ce24bdbca949f `fileenv.c`, `Kconfig`, `Makefile` | `Ricardo Pardini` _cmd: fileenv: read string from file into env_ |
| ✅  | `general-fix-btrfs-zstd-decompression` | `(+72/-4)[1M]` | b4a6785d7bc9e8855083e87580b8df6cbfa12049 `compression.c` | `Igor Velkov` _fs: btrfs: fix zstd decompression for BTRFS extents_ |
| ✅  | `general-rk3588-add-i2s-mclk-output-to-io-clock-ids` | `(+4/-0)[1M]` | 39a507d92acc0e559bab0155715e292919fa7d33 `rockchip,rk3588-cru.h` | `SuperKali` _dt-bindings: clock: rockchip,rk3588-cru: add I2S MCLK output to IO clock IDs_ |
| ⚠️`[needs_rebase]`  | `general-rk3588-raise-cpu-clocks-via-scmi` | `(+41/-0)[2M]` | 1b53995d10032be27096d4c93c97f9c9769a0a91 `clk_rk3588.c`, `cru_rk3588.h` | `SuperKali` _clk: rockchip: rk3588: raise CPU clocks through SCMI in U-Boot proper_ |
| ✅  | `mtd-spi-nor-Add-support-for-Zbit-ZB25LQ128` | `(+2/-0)[1M]` | 408f7acd7803e02bb3c7762aa46fcea9d196d8f6 `spi-nor-ids.c` | `Ricardo Pardini` _mtd: spi-nor: Add support for Zbit ZB25LQ128_ |
| ✅  | `pxe-over-http-v0` | `(+126/-5)[2M]` | 312ba60f75a66f6bd50a5c23fb38fb23fcf581eb `pxe.c`, `Kconfig` | `Ricardo Pardini` _pxe: support fetching PXE/extlinux files over HTTP(S)_ |
| ✅  | `pxe-over-http-v0` | `(+25/-10)[1M]` | 791edcb40974d787254f5c2204e30625339a41ca `bootmeth_pxe.c` | `Ricardo Pardini` _bootstd: extlinux-pxe: fetch files over HTTP(S) when URL-based_ |
| ✅  | `pxe-over-http-v0` | `(+56/-1)[2M]` | 597bb4b124cb4b4c0a0fa192fba449dc4a797c4a `pxe.rst`, `pxelinux.rst` | `Ricardo Pardini` _doc: pxe: document booting over HTTP(S)_ |
| ✅  | `pxe-over-http-v0` | `(+43/-5)[2M]` | 7f42cd1366803e4bd3b201640905812bd5b08cb2 `pxe.c`, `bootmeth_pxe.c` | `Ricardo Pardini` _DEBUG: pxe-http: trace boot path (DO NOT UPSTREAM)_ |


