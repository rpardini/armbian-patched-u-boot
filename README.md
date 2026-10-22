#### u-boot patching: 11 total patches; 11 applied; 0 with problems

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `0001-pci-pcie_dw_rockchip-increase-PCIe-LTSSM-timeout-for-cold-boot` | `(+2/-2)[1M]` | 49e124d8be90a39f1abd7bf7196c857df0fa55b3 `pcie_dw_rockchip.c` | `Robert Pahle` _pci: pcie_dw_rockchip: increase PCIe retry count for Rock 5B cold boot_ |
| ✅  | `1001-fdt_fixup_ethernet-add-logs` | `(+59/-15)[2M]` | b0cf81e60cc9b000e474377b3d54879d3384aebc `fdt_support.c`, `image-fdt.c` | `Ricardo Pardini` _fdt_fixup_ethernet: add logs_ |
| ✅  | `cmd-fileenv-read-string-from-file-into-env` | `(+52/-0)[2M, 1A]` | 8bb3ef2a2f0ecd4cc06970f75cd2b719681630f7 `fileenv.c`, `Kconfig`, `Makefile` | `Ricardo Pardini` _cmd: fileenv: read string from file into env_ |
| ✅  | `general-fix-btrfs-zstd-decompression` | `(+72/-4)[1M]` | 321a9336ea863fc5d5de368a2ee0a058e3c8b24f `compression.c` | `Igor Velkov` _fs: btrfs: fix zstd decompression for BTRFS extents_ |
| ✅  | `general-rk3588-add-i2s-mclk-output-to-io-clock-ids` | `(+4/-0)[1M]` | 057457aa84c5a1445795a3d5de9ebbc67b93aa66 `rockchip,rk3588-cru.h` | `SuperKali` _dt-bindings: clock: rockchip,rk3588-cru: add I2S MCLK output to IO clock IDs_ |
| ✅  | `general-rk3588-raise-cpu-clocks-via-scmi` | `(+41/-0)[2M]` | 162edf33f2267304a91b45363ab5860c8a7854c7 `clk_rk3588.c`, `cru_rk3588.h` | `SuperKali` _clk: rockchip: rk3588: raise CPU clocks through SCMI in U-Boot proper_ |
| ✅  | `mtd-spi-nor-Add-support-for-Zbit-ZB25LQ128` | `(+2/-0)[1M]` | a2725c61656e83455e545125cb1bb3dedda921aa `spi-nor-ids.c` | `Ricardo Pardini` _mtd: spi-nor: Add support for Zbit ZB25LQ128_ |
| ✅  | `pxe-over-http-v0` | `(+126/-5)[2M]` | 5a961c0e9a60159c218735115a0188020f02ced4 `pxe.c`, `Kconfig` | `Ricardo Pardini` _pxe: support fetching PXE/extlinux files over HTTP(S)_ |
| ✅  | `pxe-over-http-v0` | `(+25/-10)[1M]` | 347efaebebbb1ef394f4f0eea282a999d4e679e9 `bootmeth_pxe.c` | `Ricardo Pardini` _bootstd: extlinux-pxe: fetch files over HTTP(S) when URL-based_ |
| ✅  | `pxe-over-http-v0` | `(+56/-1)[2M]` | 0f28d2c99ddc81864e1241dc1a2c9d91e4bef107 `pxe.rst`, `pxelinux.rst` | `Ricardo Pardini` _doc: pxe: document booting over HTTP(S)_ |
| ✅  | `pxe-over-http-v0` | `(+43/-5)[2M]` | fd73ba17fa5eeeed3fcf10ed94dfc1571f89383c `pxe.c`, `bootmeth_pxe.c` | `Ricardo Pardini` _DEBUG: pxe-http: trace boot path (DO NOT UPSTREAM)_ |


