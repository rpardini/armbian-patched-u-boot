#### u-boot patching: 3 total patches; 3 applied; 1 with problems; 1 needs_rebase

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `5000-use-serial-as-base-for-MAC-address-find-serial-first-then-ethaddr-add-a-lot-of-debugging` | `(+67/-5)[1M]` | 932da060299d33f80e84d8470b1efe43d7db9a51 `board.c` | `Ricardo Pardini` _use serial# as base for MAC address; find serial# first, then ethaddr; add a lot of debugging_ |
| ⚠️`[needs_rebase]`  | `5001-boot_rkimg-don-t-try-rockchip_u2phy_vbus_detect-when-RECOVERY-button-pressed` | `(+6/-3)[1M]` | 1b48aef5effeae8ec701611efac8729fcd367fe9 `boot_rkimg.c` | `Ricardo Pardini` _boot_rkimg: don't try rockchip_u2phy_vbus_detect when RECOVERY button pressed_ |
| ✅  | `rk3566-Add-rk3566-to-soc-name` | `(+1/-0)[1M]` | 6196b059560571641667eb3fa5224075e79eb734 `rkcommon.c` | `Piotr Szczepanik` _Add SoC based image name (rk3566) to rk35xx u-boot_ |


