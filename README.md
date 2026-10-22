#### u-boot patching: 6 total patches; 6 applied; 0 with problems

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `5000-Fixed-restart-issues-with-pd-adapter` | `(+140/-76)[3M]` | 56315a25309b2ba62a58c4fb49ba67b1d3be9356 `tcpm.c`, `fusb302.c`, `board.c` | `tom` _Fixed restart issues with pd adapter._ |
| ✅  | `5001-fix-power_delivery-driver-affects-adb-to-enter-loader-mode` | `(+8/-1)[1M]` | 2face8e4a3a6c4cd48c4a785be93beb5ca2de844 `board.c` | `tom` _fix power_delivery driver affects adb to enter loader mode._ |
| ✅  | `5002-use-serial-as-base-for-MAC-address-find-serial-first-then-ethaddr-add-a-lot-of-debugging-adapted-for-Mixtile` | `(+67/-5)[1M]` | d416c7f3ceec5f04f5eadf7034017fc74c5d08ee `board.c` | `Ricardo Pardini` _use serial# as base for MAC address; find serial# first, then ethaddr; add a lot of debugging; adapted for Mixtile_ |
| ✅  | `add-board-nanopi-r76s` | `(+232/-0)[2A]` | 78f7b715d6ff5a84276be8d22efd0b3a7085e31a `nanopi-r76s-rk3576_defconfig`, `rk3576-nanopi-r76s.dts` | `SuperKali` _Add uboot support for FriendlyELEC NanoPi R76S_ |
| ✅  | `fix-u-boot-itb-dependency-on-u-boot-dtb` | `(+1/-1)[1M]` | 745e16b5039aa89bddd7c9c7c43002a9c4435862 `Makefile` | `Yi Ding` _Makefile: fix u-boot.itb dependency on u-boot.dtb_ |
| ✅  | `rk3566-Add-rk3566-to-soc-name` | `(+1/-0)[1M]` | 0828019572ff39fd3b20e25967be0808ea9f65e8 `rkcommon.c` | `Piotr Szczepanik` _Add SoC based image name (rk3566) to rk35xx u-boot_ |


