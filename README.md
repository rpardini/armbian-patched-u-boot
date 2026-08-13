#### u-boot patching: 20 total patches; 20 applied; 0 with problems

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `0001-pci-pcie_dw_rockchip-increase-PCIe-LTSSM-timeout-for-cold-boot` | `(+2/-2)[1M]` | b6d2b6b7e94be9ff8ac34400a7263a20974be7ac `pcie_dw_rockchip.c` | `Robert Pahle` _pci: pcie_dw_rockchip: increase PCIe retry count for Rock 5B cold boot_ |
| ✅  | `0001-rockchip-rk3528-Add-support-for-booting-from-SPI-fla` | `(+28/-0)[2M]` | e68628736a41a21a431bfa76b55466782631eecb `rk3528-u-boot.dtsi`, `rk3528.c` | `Jonas Karlman` _rockchip: rk3528: Add support for booting from SPI flash_ |
| ✅  | `0002-WIP-net-rockchip-Allow-use-of-rx-tx-delayline-for-rg` | `(+39/-59)[2M]` | bc038a53ba5854a106f72d53c482a689118cbeb6 `gmac_rockchip.c`, `dwc_eth_qos_rockchip.c` | `Jonas Karlman` _WIP: net: rockchip: Allow use of rx/tx delayline for rgmii-id modes_ |
| ✅  | `0003-WIP-net-rockchip-Use-CRU-as-default-TX-clk-source-fo` | `(+6/-2)[2M]` | 8ba7c44be8a8da857aab30abb7c6613a99cf5a51 `dwc_eth_qos_rockchip.c`, `gmac_rockchip.c` | `Jonas Karlman` _WIP: net: rockchip Use CRU as default TX clk source for RGMII modes_ |
| ✅  | `0004-WIP-add-e24c-board-model-to-rock-2-rk3528.c` | `(+1/-0)[1M]` | a64db0effe9f2014e3e2afbe3e8009551970f6f2 `rock-2-rk3528.c` | `Ricardo Pardini` _WIP: add e24c board model to rock-2-rk3528.c_ |
| ✅  | `0005-WiP-rk3528-u-boot-dtsi-drop-otp-as-already-in-main-d` | `(+0/-5)[1M]` | cb13cc92e2f46087c7dcc77d1a026053cdab16b7 `rk3528-u-boot.dtsi` | `Ricardo Pardini` _WiP: rk3528-u-boot dtsi drop otp as already in main dtsi_ |
| ✅  | `0006-rockchip-rk3528-add-USB-nodes` | `(+80/-0)[1M]` | e0e894d5d6e0976e037602d5ccf7525c11b73a8c `rk3528.dtsi` | `Ricardo Pardini` _rockchip: rk3528: add USB nodes_ |
| ✅  | `0007-rockchip-rk3528-add-OTP` | `(+47/-0)[1M]` | 335431f341f69ecfd4b36bc44d14dc74e07a12d6 `rk3528.dtsi` | `Ricardo Pardini` _rockchip: rk3528: add OTP_ |
| ✅  | `0008-rockchip-rk3528-add-VPU` | `(+23/-0)[1M]` | ddfa353e606171b9d381f43989dc91ad6e940916 `rk3528.dtsi` | `Ricardo Pardini` _rockchip: rk3528: add VPU_ |
| ✅  | `0009-rockchip-rk3528-add-Watchdog` | `(+8/-0)[1M]` | b6df25b3cf94ba0a57d9657002000b9bf87c099e `rk3528.dtsi` | `Ricardo Pardini` _rockchip: rk3528: add Watchdog_ |
| ✅  | `0010-rockchip-rk3528-add-SFC` | `(+12/-0)[1M]` | a0767be80364b6c19839a8a8cb8740ca9f9cef8d `rk3528.dtsi` | `Ricardo Pardini` _rockchip: rk3528: add SFC_ |
| ✅  | `1001-fdt_fixup_ethernet-add-logs` | `(+59/-15)[2M]` | ef3b781e9f180e716f080d58c29f833fe9539c96 `fdt_support.c`, `image-fdt.c` | `Ricardo Pardini` _fdt_fixup_ethernet: add logs_ |
| ✅  | `cmd-fileenv-read-string-from-file-into-env` | `(+52/-0)[2M, 1A]` | 252bd579860bb54fc8a54a53002f521303d45b99 `fileenv.c`, `Kconfig`, `Makefile` | `Ricardo Pardini` _cmd: fileenv: read string from file into env_ |
| ✅  | `general-fix-btrfs-zstd-decompression` | `(+72/-4)[1M]` | c6ee7b486bebf3e585da4bbfe7575c998119be24 `compression.c` | `Igor Velkov` _fs: btrfs: fix zstd decompression for BTRFS extents_ |
| ✅  | `general-rk3588-add-i2s-mclk-output-to-io-clock-ids` | `(+4/-0)[1M]` | 4a6db22509bcae0627d1d0e7f074e669d227dc4f `rockchip,rk3588-cru.h` | `SuperKali` _dt-bindings: clock: rockchip,rk3588-cru: add I2S MCLK output to IO clock IDs_ |
| ✅  | `mtd-spi-nor-Add-support-for-Zbit-ZB25LQ128` | `(+2/-0)[1M]` | 855c70d9946c43d8dbef3339ee2800fa6ed0eeb8 `spi-nor-ids.c` | `Ricardo Pardini` _mtd: spi-nor: Add support for Zbit ZB25LQ128_ |
| ✅  | `pxe-over-http-v0` | `(+126/-5)[2M]` | 07f4514c986fce09992345187b7c17639237beda `pxe.c`, `Kconfig` | `Ricardo Pardini` _pxe: support fetching PXE/extlinux files over HTTP(S)_ |
| ✅  | `pxe-over-http-v0` | `(+25/-10)[1M]` | 5925726a61474f6b04f9040b6bd8dedfc4ccc452 `bootmeth_pxe.c` | `Ricardo Pardini` _bootstd: extlinux-pxe: fetch files over HTTP(S) when URL-based_ |
| ✅  | `pxe-over-http-v0` | `(+56/-1)[2M]` | ba2843d8a61318fe36183d48d0bb0616022bd5c6 `pxe.rst`, `pxelinux.rst` | `Ricardo Pardini` _doc: pxe: document booting over HTTP(S)_ |
| ✅  | `pxe-over-http-v0` | `(+43/-5)[2M]` | f6957c0f9df97fea42a6c3a52c98e22e9ccecd14 `pxe.c`, `bootmeth_pxe.c` | `Ricardo Pardini` _DEBUG: pxe-http: trace boot path (DO NOT UPSTREAM)_ |


