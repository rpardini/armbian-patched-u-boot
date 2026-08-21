#### u-boot patching: 14 total patches; 14 applied; 0 with problems

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `0001-allow-fdt-fixups-before-dm-as-spl_board_init-works-l` | `(+9/-0)[1M]` | ba7e8c0fd1942febf160360922a3f67659a1847c `spl.c` | `Muhammed Efe Cetin` _allow fdt fixups before dm as spl_board_init works later_ |
| ✅  | `0001-pci-pcie_dw_rockchip-increase-PCIe-LTSSM-timeout-for-cold-boot` | `(+2/-2)[1M]` | 3f0e8c96c93b2906be83fda0e484046421f5b627 `pcie_dw_rockchip.c` | `Robert Pahle` _pci: pcie_dw_rockchip: increase PCIe retry count for Rock 5B cold boot_ |
| ✅  | `0002-add-common-nanopi6-series-board-config` | `(+365/-0)[1M, 7A]` | 6fa82b86f928cb2b01ea779c84e35b4d2bd85aac `nanopi6-series-rk3588s.c`, `nanopi6-series-rk3588s_defconfig`, `rk3588s-nanopi6-series.dts`, `rk3588s-nanopi6-series-u-boot.dtsi`, `Kconfig`, `nanopi6-series-rk3588s.h`, `Makefile` | `Muhammed Efe Cetin` _add common nanopi6 series board config_ |
| ✅  | `0003-add-support-for-NanoPi-M6V2-board` | `(+11/-5)[2M]` | f58b017952ce8cb925486bd8f64998f5e0e017ec `nanopi6-series-rk3588s.c`, `nanopi6-series-rk3588s_defconfig` | `Muhammed Efe Cetin` _add support for NanoPi M6V2 board_ |
| ✅  | `0004-add-NanoPC-6-series-to-common-nanopi-config` | `(+95/-12)[4M, 2A]` | 45d5d5de5c694e2549348fe852dc4f7d321a912f `nanopi6-series-rk3588s.c`, `rk3588-nanopc-t6-lts-plus.dts`, `rk3588s-nanopi6-series-u-boot.dtsi`, `rk3588-nanopc-t6-lts-plus-u-boot.dtsi`, `nanopi6-series-rk3588s_defconfig`, `rk3588s-nanopi6-series.dts` | `Muhammed Efe Cetin` _add NanoPC 6 series to common nanopi config_ |
| ✅  | `1001-fdt_fixup_ethernet-add-logs` | `(+59/-15)[2M]` | f9feb708e2a3479df90cfe5517f8957896020348 `fdt_support.c`, `image-fdt.c` | `Ricardo Pardini` _fdt_fixup_ethernet: add logs_ |
| ✅  | `cmd-fileenv-read-string-from-file-into-env` | `(+52/-0)[2M, 1A]` | 0da47481752dc758e25c13b4e2ef52d425e66415 `fileenv.c`, `Kconfig`, `Makefile` | `Ricardo Pardini` _cmd: fileenv: read string from file into env_ |
| ✅  | `general-fix-btrfs-zstd-decompression` | `(+72/-4)[1M]` | 8d9388aa8881d0f8abcf2320b7884a249cc65005 `compression.c` | `Igor Velkov` _fs: btrfs: fix zstd decompression for BTRFS extents_ |
| ✅  | `general-rk3588-add-i2s-mclk-output-to-io-clock-ids` | `(+4/-0)[1M]` | 571a816df84b8f9c2cda540aadc6b0c7e8c17604 `rockchip,rk3588-cru.h` | `SuperKali` _dt-bindings: clock: rockchip,rk3588-cru: add I2S MCLK output to IO clock IDs_ |
| ✅  | `mtd-spi-nor-Add-support-for-Zbit-ZB25LQ128` | `(+2/-0)[1M]` | 581af4832913a62f97b70b4c10c397edfecf2da5 `spi-nor-ids.c` | `Ricardo Pardini` _mtd: spi-nor: Add support for Zbit ZB25LQ128_ |
| ✅  | `pxe-over-http-v0` | `(+126/-5)[2M]` | 3909732809b7fa370942650fb9c39841d6b13eeb `pxe.c`, `Kconfig` | `Ricardo Pardini` _pxe: support fetching PXE/extlinux files over HTTP(S)_ |
| ✅  | `pxe-over-http-v0` | `(+25/-10)[1M]` | ab979ea53d7b217625806fcffddc989218b5b743 `bootmeth_pxe.c` | `Ricardo Pardini` _bootstd: extlinux-pxe: fetch files over HTTP(S) when URL-based_ |
| ✅  | `pxe-over-http-v0` | `(+56/-1)[2M]` | 109702b989b84c1cbb3d9c7951fdd57f8bf03562 `pxe.rst`, `pxelinux.rst` | `Ricardo Pardini` _doc: pxe: document booting over HTTP(S)_ |
| ✅  | `pxe-over-http-v0` | `(+43/-5)[2M]` | cc794c5c9d7d954cfb3b2ce94078d429d8fbd7ee `pxe.c`, `bootmeth_pxe.c` | `Ricardo Pardini` _DEBUG: pxe-http: trace boot path (DO NOT UPSTREAM)_ |


