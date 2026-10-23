# mixtile-blade3: reliable USB-PD power input (U-Boot v2026.10 + kernel 7.3)

The Blade 3 is powered only through USB-C1, a FUSB302 on i2c1. With a PD
charger, the board often lost power during boot. The charger would send a
Hard Reset because no Request ever came, either in U-Boot or when the kernel
took over U-Boot's contract.

## Board / DT

- `7e34f8762e` rockchip64-7.3: make USB-C1 sink-only
  - with "dual", tcpm DRP-toggles; while Rp is presented, the source sees Rd
    vanish and may drop VBUS
  - drops `source-pdos` and `try-power-role`

## U-Boot

- `2cc8fc9751` bump mainline U-Boot to v2026.10
  - DT synced from v7.3
  - `-u-boot.dtsi` forces `usb_con1` to `power-role = "sink"`. U-Boot's tcpm
    only auto-probes sink ports, so before this U-Boot never negotiated PD.
  - `vendor*` uses the vendor BL31 (for HDMI-RX)
- `41df86bc1b` bring back vendor U-Boot (Radxa next-dev-v2024.03) for
  `vendor*`
  - switches: `BLADE3_USE_MAINLINE_UBOOT` / `BLADE3_USE_VENDOR_UBOOT`
  - restores Mixtile's fusb302 patches 5000/5001; drops 5002
- `8bd5d49fba` 030–033: Sebastian Reichel's
  ["USB-PD TCPM improvements" v2](https://lore.kernel.org/all/20250226184506.64114-1-sebastian.reichel@collabora.com/),
  not merged as of v2026.10
  - [1/4](https://lore.kernel.org/all/20250226184506.64114-2-sebastian.reichel@collabora.com/):
    keep servicing PD messages after SNK_READY
  - [2/4](https://lore.kernel.org/all/20250226184506.64114-3-sebastian.reichel@collabora.com/):
    send Get_Source_Cap / Soft_Reset instead of a Hard Reset when Source_Caps
    are missing. Also explains why the FUSB302 keeps its state across power
    loss: voltage leaks in from the serial pins.
  - 3/4: print an error on Hard Reset
  - 4/4: better recovery from a data role mismatch
- `e8bb048a64` 010 fusb302: really delay BC_LVL handling on CC activity, as
  the kernel does. Before, PD traffic produced invalid CC readings.
- `8d13814a0e` 020 fusb302: drain the RX FIFO on TX_SUCCESS/GCRCSENT
  - the driver read only one message per event. On a warm reboot, Accept and
    Source_Caps arrive back to back after U-Boot's Soft_Reset, Source_Caps
    was lost, and the charger sent a Hard Reset.
  - same fix as the kernel's 912, below
- `75a6b7c966` 090 DEBUG: serial console tracing for tcpm/fusb302 (on by
  default)

## Kernel (rockchip64-7.3)

- `7c5f0e79b7` 912 fusb302: drain the RX FIFO on TX_SUCCESS/GCRCSENT
  - tcpm sends a Soft_Reset to take over U-Boot's contract. Accept and
    Source_Caps then arrive a few ms apart; Source_Caps was lost, and the
    charger sent a Hard Reset and the board lost power.
  - seen on about 75% of boots with the Pine and SyncWire chargers
  - prior art: Rockchip's BSP kernel has the same drain (`99321070f1a0`),
    never posted upstream. Frank Wang's related tcpm patch was
    [rejected](https://lore.kernel.org/all/7038030f-1d7a-4c91-a255-bec73847b7c9@roeck-us.net/)
    as "a problem in the fusb302 driver", and the series
    ([v1](https://lore.kernel.org/all/20230313025843.17162-1-frank.wang@rock-chips.com/),
    [v4](https://lore.kernel.org/all/20230616075241.27690-1-frank.wang@rock-chips.com/))
    went no further
  - Reichel's
    ["fusb302: cache PD RX state"](https://lore.kernel.org/all/20250704-fusb302-race-condition-fix-v1-1-239012c0e27a@kernel.org/)
    fixes a different race (the flush), not this one
  - to be sent upstream

## Tested

- SyncWire, UGREEN and Pine chargers: cold boots and repeated reboots. Each
  reached a 20 V contract in U-Boot and again in Linux, with no power loss.
- True cold boot, with the serial adapter also powered off: the FUSB302
  started from power-on defaults and negotiated cleanly.

## Related upstream work

- Peng Fan's
  ["usb: Add TCPCI driver and DWC3 OTG dual-role support" v2](https://lore.kernel.org/all/20260621-tcpci-dwc3-v2-0-990ecacc111c@nxp.com/)
  ([01/10](https://lore.kernel.org/all/20260621-tcpci-dwc3-v2-1-990ecacc111c@nxp.com/),
  [02/10](https://lore.kernel.org/all/20260621-tcpci-dwc3-v2-2-990ecacc111c@nxp.com/))
  overlaps with Reichel's 1/4 and 2/4. Rebase if it lands first.
- Already in v2026.10:
  ["usb: tcpm: fix inverted poll condition in tcpm_pd_transmit()"](https://lore.kernel.org/all/20260618-tcpm-fix-v2-1-57d16534b04f@nxp.com/)
