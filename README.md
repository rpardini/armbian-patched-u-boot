#### u-boot patching: 15 total patches; 15 applied; 0 with problems

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `9000-net-rtl8169-do-soft-reset` | `(+0/-2)[1M]` | 95168c30ce620d9faec350b571b6904d2c90e221 `rtl8169.c` | `Ricardo Pardini` _net: rtl8169: do soft reset_ |
| ✅  | `9000-rockchip-rk3528-Add-support-for-booting-from-SPI-fla` | `(+28/-0)[2M]` | f0a6075e663655812ae01a833c5ee329c64cf537 `rk3528-u-boot.dtsi`, `rk3528.c` | `Jonas Karlman` _rockchip: rk3528: Add support for booting from SPI flash_ |
| ✅  | `9001-WIP-net-rockchip-Allow-use-of-rx-tx-delayline-for-rg` | `(+39/-59)[2M]` | 209ade2cad33509db29281b7684781bcc77cc335 `gmac_rockchip.c`, `dwc_eth_qos_rockchip.c` | `Jonas Karlman` _WIP: net: rockchip: Allow use of rx/tx delayline for rgmii-id modes_ |
| ✅  | `9001-net-rtl8169-define-DEBUG_RTL8169` | `(+1/-1)[1M]` | ef8541966e89c60505d0355d642c07378037f2c0 `rtl8169.c` | `Ricardo Pardini` _net: rtl8169: define DEBUG_RTL8169_ |
| ✅  | `9002-WIP-net-rockchip-Use-CRU-as-default-TX-clk-source-fo` | `(+6/-2)[2M]` | c5ec4cde0681cdb177c9465dafd34bca93f8d010 `dwc_eth_qos_rockchip.c`, `gmac_rockchip.c` | `Jonas Karlman` _WIP: net: rockchip Use CRU as default TX clk source for RGMII modes_ |
| ✅  | `9003-WIP-Kwiboo-s-WIP-rk3528.dtsi-with-pcie-usb-combphy-e` | `(+160/-1)[1M]` | b289a18fdc37e14a30d8b4650f78253aa69549d0 `rk3528.dtsi` | `Ricardo Pardini` _WIP: Kwiboo's WIP rk3528.dtsi with pcie usb combphy etc_ |
| ✅  | `9004-WIP-add-e24c-board-model-to-rock-2-rk3528.c` | `(+1/-0)[1M]` | 5198e1b0c85a42f801de3b571983fb96501c304b `rock-2-rk3528.c` | `Ricardo Pardini` _WIP: add e24c board model to rock-2-rk3528.c_ |
| ✅  | `arm64-dts-allwinner-sun55i-a523-add-pcie-spi-combophy` | `(+65/-0)[1M]` | e36f7f83b63c2126cdf37fbb284260ae25124d39 `sun55i-a523.dtsi` | `Marvin Wewer` _arm64: dts: allwinner: sun55i-a523: Add SPI0, PCIe and Combophy nodes_ |
| ✅  | `clk-sunxi-add-sun55i-a523-pcie-usb3-clocks` | `(+4/-0)[2M]` | 18f12967317bd78a9ac3181bfc027bb1c836d3e0 `clk_a523.c`, `sun55i-a523-ccu.h` | `Marvin Wewer` _clk: sunxi: Add PCIe and USB3 clock support for SUN55I A523_ |
| ✅  | `cmd-fileenv-read-string-from-file-into-env` | `(+52/-0)[2M, 1A]` | 2e66677ad176c40b1f64ac16a671d07e5540313a `fileenv.c`, `Kconfig`, `Makefile` | `Ricardo Pardini` _cmd: fileenv: read string from file into env_ |
| ✅  | `pcie-sunxi-add-dw-pcie-support-for-sun55i` | `(+1441/-0)[2M, 3A]` | 4b7be06d84d1ca0640665555929f2e3e88191a0d `pcie-sun55i.c`, `pcie-sun55i.h`, `pcie-sun55i-plat.c`, `Kconfig`, `Makefile` | `Marvin Wewer` _PCIe: sunxi: Add DesignWare PCIe controller support for SUN55I_ |
| ✅  | `phy-allwinner-add-pcie-usb3-driver` | `(+665/-0)[2M, 1A]` | c73424df132c69bfce913b1842f9cf2416030f7b `phy-sun55i-pcie-usb3.c`, `Kconfig`, `Makefile` | `Marvin Wewer` _phy: allwinner: Add SUN55I INNO combo PHY driver for PCIe/USB3_ |
| ✅  | `spi-sunxi-add-sun55i-a523-spl-support` | `(+68/-39)[1M]` | 9cf295dcfe89dd11837e03e57f3cc0ca0db80c25 `spl_spi_sunxi.c` | `Marvin Wewer` _spi: sunxi: Add support for Allwinner A523 SPI controllers in SPL_ |
| ✅  | `spi-sunxi-add-sun55i-a523-support` | `(+44/-0)[1M]` | 7943bcdf05ab82701fa71b87434489577ef5563c `spi-sunxi.c` | `Marvin Wewer` _spi: sunxi: Add support for Allwinner A523 SPI controllers_ |
| ✅  | `sunxi-add-nvme-boot-target` | `(+7/-0)[1M]` | bcbdadb297ee2d4dfbf8b82325c4a3523ffc0a7a `sunxi-common.h` | `Marvin Wewer` _sunxi: Add NVME boot target support_ |


