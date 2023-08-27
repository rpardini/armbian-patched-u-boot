#### u-boot patching: 11 total patches; 11 applied; 0 with problems

| Status | Patch  | Diffstat Summary | Files patched | Author / Subject |
| :---:    | :---   | :---   | :---   | :---  |
| ✅  | `1000-Add-Blade-3-defines` | `(+275/-0)[2A]` | ea670c0a4e885357bcad749d4e56e3b32d66773c `blade3_defconfig`, `rk3588-blade3.dts` | `Martin Liu` _Add Blade 3 defines_ |
| ✅  | `1001-Fixed-restart-issues-with-pd-adapter` | `(+140/-76)[3M]` | 3e3c52397d8129ab81f1606fc5d1ed525ad09f3d `tcpm.c`, `fusb302.c`, `board.c` | `tom` _Fixed restart issues with pd adapter._ |
| ✅  | `1002-fix-power_delivery-driver-affects-adb-to-enter-loade` | `(+8/-1)[1M]` | 175a79cd23fcea131fc0a4eb0ff0f459760a5f40 `board.c` | `tom` _fix power_delivery driver affects adb to enter loader mode._ |
| ✅  | `1003-cmd-source-fix-the-error-that-the-command-source-fai` | `(+1/-1)[1M]` | 0899ec2f1a48b144d73759f9c07c723964807369 `source.c` | `Ricardo Pardini` _cmd: source: fix the error that the command source failed to execute_ |
| ✅  | `1004-add-device-tree-with-sata-support` | `(+252/-0)[2A]` | d753662b9d5fb58e026a9042b2e5acf91bc4b45d `blade3_sata_defconfig`, `rk3588-blade3-sata.dts` | `Joshua Riek` _add device tree with sata support_ |
| ✅  | `1090-disable-optee-in-defconfig` | `(+2/-8)[2M]` | 98724c23b65dac55d163acc369b14229593a883c `blade3_defconfig`, `blade3_sata_defconfig` | `Ricardo Pardini` _disable optee in defconfig_ |
| ✅  | `1091-mixtile-blade3-enable-OTP-in-defconfig` | `(+2/-0)[2M]` | 57b26fc1f23f07b8aefb2e7e500c43a7dd9ab37e `blade3_defconfig`, `blade3_sata_defconfig` | `Ricardo Pardini` _mixtile-blade3: enable OTP in defconfig_ |
| ✅  | `1092-enable-nvme-pci-and-scsi-in-the-defconfig` | `(+34/-2)[2M]` | 4b80f7c2cf43e585db98f704cca69459018b9fdb `blade3_defconfig`, `blade3_sata_defconfig` | `Joshua Riek` _enable nvme, pci, and scsi in the defconfig_ |
| ✅  | `1093-use-serial-as-base-for-MAC-address-find-serial-first-then-ethaddr-add-a-lot-of-debugging-adapted-for-Mixtile` | `(+67/-5)[1M]` | cfe5691eafeb20fb10812d5dc1562dc512cb7ac9 `board.c` | `Ricardo Pardini` _use serial# as base for MAC address; find serial# first, then ethaddr; add a lot of debugging; adapted for Mixtile_ |
| ✅  | `1094-blade3-dts-hack-pcie3x4-pcie30phy-and-some-regulators-in` | `(+45/-0)[1M]` | 6b1c0897de8dd0c1f9ea7436b527b44ce42faa68 `rk3588-blade3.dts` | `Ricardo Pardini` _blade3: dts: hack pcie3x4, pcie30phy and some regulators in_ |
| ✅  | `2000-arch-arm-mach-rockchip-fix-srctree-path` | `(+2/-2)[2M]` | 332775a6e5de2e754ee40fbe9670b71ac68f9f8f `fit_nodes.sh`, `make_fit_atf.sh` | `Joshua Riek` _arch: arm: mach-rockchip: fix srctree path_ |


