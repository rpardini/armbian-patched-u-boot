#### u-boot patching: 4 total patches; 4 applied; 1 with problems; 1 needs_rebase

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `5000-Fixed-restart-issues-with-pd-adapter` | `(+140/-76)[3M]` | 56315a25309b2ba62a58c4fb49ba67b1d3be9356 `tcpm.c`, `fusb302.c`, `board.c` | `tom` _Fixed restart issues with pd adapter._ |
| ✅  | `5001-fix-power_delivery-driver-affects-adb-to-enter-loader-mode` | `(+8/-1)[1M]` | 2face8e4a3a6c4cd48c4a785be93beb5ca2de844 `board.c` | `tom` _fix power_delivery driver affects adb to enter loader mode._ |
| ✅  | `5002-use-serial-as-base-for-MAC-address-find-serial-first-then-ethaddr-add-a-lot-of-debugging-adapted-for-Mixtile` | `(+67/-5)[1M]` | d416c7f3ceec5f04f5eadf7034017fc74c5d08ee `board.c` | `Ricardo Pardini` _use serial# as base for MAC address; find serial# first, then ethaddr; add a lot of debugging; adapted for Mixtile_ |
| ⚠️`[needs_rebase]`  | `rk3566-Add-rk3566-to-soc-name` | `(+1/-0)[1M]` | 7a8310518417febf0c9b911c874d329a69fd86b6 `rkcommon.c` | `Piotr Szczepanik` _Add SoC based image name (rk3566) to rk35xx u-boot_ |


