# Mixtile Blade 3: USB-PD power input in U-Boot

Date: 2026-10-22
Tree: mainline U-Boot v2026.10 + Armbian patches,
branch `armbian-armsurvivors-mixtile-blade3-edge-20261022-debug-usbpd`
Defconfig: `configs/mixtile-blade3-rk3588_defconfig` (reuses `TARGET_ROCK5B_RK3588`)

## Summary

The Blade 3 is powered through USB-C1 (FUSB302 on `i2c1`, `i2c@fea90000`).
U-Boot never negotiated USB-PD on it, and when it did, two problems could
make it lose power. With the two fixes below, U-Boot gets an explicit PD
contract from all four chargers that answered PD (one gave no PD response at all in its only run):

| Supply   | PD  | Offers                                         | Contract      |
|----------|-----|------------------------------------------------|---------------|
| SyncWire | 3.0 | 5/9/12/15/20 V fixed + 2 PPS                   | 20 V / 1.5 A  |
| Pixel 4  | 2.0 | 5 V / 3 A, 9 V / 2 A                           | 9 V / 2 A     |
| UGREEN   | 3.0 | 5 V / 3 A, 9 V / 2.22 A, 12 V / 1.67 A + 2 PPS | 12 V / 1.67 A |
| Pine     | 3.0 | 5/9/12/15 V @ 3 A, 20 V @ 3.25 A + 2 PPS       | 20 V / 3 A    |

Linux has not been tested yet.

## Root causes

### 1. U-Boot never probed the TCPM on the power port

`tcpm_post_bind()` only auto-probes a connector whose `power-role` is
`"sink"`. The upstream Blade 3 DT has `"dual"` on both ports, so PD was left
to Linux, which starts long after the ~5 s window in which a source still
expects a sink to talk. A late PD start ends in a Hard Reset, which takes
VBUS to 0 V and resets a board powered only through USB-C.

Fix: `&usb_con1 { power-role = "sink"; }` in
`arch/arm/dts/rk3588-mixtile-blade3-u-boot.dtsi`. USB-C0 (`i2c6`,
OTG/maskrom) stays `"dual"` and is not probed.

The kernel DT has the same `"dual"` role on USB-C1. With it, Linux toggles
between sink and source on the power port, during which the source can see
the sink disappear and drop VBUS. The kernel DT should get the same
`"sink"` override.

### 2. FUSB302 driver used invalid BC_LVL samples

`fusb302_bc_lvl_handler()` logged "CC activities detected, delay handling"
but used the BC_LVL value anyway. BC_LVL is meaningless while PD packets are
on CC. Every log showed bogus `rp-3.0 -> rp-def / rp-1.5` flips right after
a Request. In one Pixel 4 run the sample read `open`: TCPM detached in the
middle of negotiation, the source sent Soft Reset, then Hard Reset, and VBUS
dropped.

Fix: skip the sample on CC activity and re-check after 30 ms from
`poll_event`, as the Linux driver does. Verified on the Pixel 4 and later
runs: the delay path triggers, no false CC change, negotiation completes.

## Timing

Milliseconds since SoC power-on (arch timer), typical RAMBOOT run:

| Event                           | t (ms)     |
|---------------------------------|------------|
| SPL console up                  | ~1850-1930 |
| SPL jumps to TF-A               | ~1980-2070 |
| TCPM probe (U-Boot proper)      | ~3720-3810 |
| Attach debounced, PD RX enabled | ~4020-4100 |
| Source_Capabilities received    | ~4060-4250 |
| Explicit contract (`SNK_READY`) | ~4200-4410 |

The deadline that matters is tSenderResponse: the sink must send its Request
within ~24-30 ms of acknowledging Source_Capabilities. Normal builds manage
10-12 ms. With per-message console dumps at 1.5 Mbaud it took ~29 ms and the
SyncWire answered with a Hard Reset; that tracing is now gated behind
`CONFIG_TYPEC_TCPM_DEBUG_VERBOSE` (default off).

The ~1.7 s from SPL to the TCPM probe is partly due to RAMBOOT; it should be
re-measured when booting from eMMC.

## Per-supply runs

| Supply           | Runs               | Notes                                                                                                                                                                                   |
|------------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| (first, unnamed) | 1 fail             | No Source_Capabilities at ~4 s, Soft_Reset not acknowledged; TCPM sent Hard Reset and the board lost power. Charger most likely had given up on PD before U-Boot started. Not retested. |
| SyncWire         | 1 fail, 2 OK       | Fail was the slow debug tracing (fixed by gating). The supply that worked with the vendor stack.                                                                                        |
| Pixel 4          | 2 OK, 1 fail, 2 OK | Fail was the BC_LVL bug; OK after the fix. PD 2.0: TCPM drops to rev2 correctly.                                                                                                        |
| UGREEN           | 1 fail, 1 OK       | Fail caused by stale FUSB302 state (see below), not by the charger.                                                                                                                     |
| Pine             | 1 OK               | Ran despite stale FUSB302 state.                                                                                                                                                        |

## Open item: FUSB302 keeps state while the board is unplugged

The FUSB302 on USB-C1 keeps its registers through power-off. Each
"before sw reset" dump shows the configuration the previous session left
behind, plus Source_Capabilities from the newly plugged charger in the RX FIFO.

Ruled out:

- serial adapter TX back-power (TX disconnected)
- residual charge (60 s off)
- maskrom cable (unplugged during power-off)
- a second boot in the same session (RAMBOOT script loaded once)

Effect: if the previous session left the chip in U-Boot's low-power state (auto-GoodCRC on), the chip acknowledges the
new charger's first
Source_Capabilities before any software runs. The charger then expects a
Request, gets none, and escalates to Hard Reset. The UGREEN kept escalating
and cut power during the attach debounce; the Pine and Pixel 4 kept offering
and U-Boot still got a contract.

Next step: measure FUSB302 VDD with everything unplugged; check the
schematic for the rail feeding it. Bench workaround for clean cold-boot
tests: reset the chip from the U-Boot prompt before power-off (`i2c dev <i2c1>; i2c mw 0x22 0x0c 0x01`).

## Not yet covered

- U-Boot leaves the FUSB302 at `POWER=0x03` (oscillator off) after the
  contract. Nothing services PD until Linux probes its driver. No failure has
  been attributed to this yet; a `CONFIG_CYCLIC` poll after `SNK_READY` is the
  likely fix if one shows up.
- Linux: kernel DT `power-role`, handover of the existing contract (Linux has
  to Soft Reset to get Source_Capabilities again), tcpm debugfs logs.
- Booting from eMMC instead of RAMBOOT, `reboot` from Linux, and USB-C hubs.
- `i2c1` runs at the 100 kHz default; 400 kHz would add margin to the
  tSenderResponse budget.

## Commits

| Commit        | Upstream | Description                                                          |
|---------------|----------|----------------------------------------------------------------------|
| `84c8d44cb2c` | Armbian  | arm: dts: rockchip: blade3: make USB-C1 sink-only in U-Boot          |
| `e6d3a560de1` | yes      | usb: tcpm: fusb302: really delay BC_LVL handling on CC activity      |
| `328680ffe53` | no       | DEBUG: verbose PD tracing, timestamps, reset cause, SPL timestamps   |
| `5ec03866ed2` | no       | DEBUG: gate verbose tracing behind `CONFIG_TYPEC_TCPM_DEBUG_VERBOSE` |
| `481014888e2` | no       | DEBUG: identify which Type-C port logs                               |
| `44f91b18988` | no       | DEBUG: dump stale RX FIFO messages before sw reset                   |

The BC_LVL fix applies cleanly without the debug commits and builds without
warnings; checkpatch only flags the `Assisted-by:` trailer.

------------------------------------------------------------------------------------------------------------------------
# 2nd round


## Setup

- eMMC boot (no RAMBOOT), U-Boot and Linux 7.3 with the debug patches.
- Kernel DT: `usb_con1` changed to `power-role = "sink"` (Armbian `2cfb02d486`).
  Linux shows `port0` as `[sink]`.
- Kernel debug: tcpm and fusb302 debugfs logs mirrored to the console
  (`tcpm.console_log`, `fusb302.console_log`, default on), plus a dump of
  FUSB302 registers and RX FIFO before the driver's sw reset.

## Handover from U-Boot to Linux

U-Boot leaves an explicit contract in place. Linux's TCPM starts from scratch:
sw reset, `PORT_RESET`, ~1 s wait, attach, then 310 ms waiting for
Source_Capabilities that never come (the source is already in a contract).
TCPM then sends **Soft_Reset**; the source answers Accept and sends
Source_Capabilities again. This happens at ~3.1 s into the kernel boot.

The same path runs in U-Boot after a warm `reboot` from Linux: the source is
still in Linux's contract, so U-Boot also has to Soft_Reset.

## Bug 3: FUSB302 driver loses back-to-back RX messages

Both drivers (Linux and U-Boot's port) read **one** message from the RX FIFO
per `TX_SUCCESS` / `GCRCSENT` interrupt bit. These bits are latched: if two
messages arrive before the handler reads `INTERRUPTB`, it sees one event and
reads one message. The others stay in the FIFO, already acknowledged with a
GoodCRC by the chip.

After a Soft_Reset the source sends Accept and Source_Capabilities a few ms
apart. When both land in one event, Source_Capabilities is never read, no
Request is sent, and after tSenderResponse the source sends Hard Reset. VBUS
drops and the board power cycles. Linux IRQ handling (2-6 ms, longer with
console logging) makes this likely; U-Boot only hits it on warm reboot.

Before the fix, 6 of 8 Soft_Reset attempts failed this way, with both the Pine
and the SyncWire. Hard Reset always came 26-28 ms after the Accept:

| Charger  | Accept IRQ (s) | Hard Reset (s) | Gap   |
|----------|----------------|----------------|-------|
| Pine     | 3.1659         | 3.1929         | 27 ms |
| Pine     | 3.0708         | 3.0982         | 27 ms |
| SyncWire | 3.1401         | 3.1657         | 26 ms |
| SyncWire | 3.1695         | 3.1973         | 28 ms |

U-Boot after cold attach never failed (8 of 8): Source_Capabilities, Accept
and PS_RDY arrive 5-130 ms apart, so they never coalesce.

Fix: after `TX_SUCCESS` / `GCRCSENT`, read messages until `STATUS1.RX_EMPTY`,
bounded by FIFO size (11). Logs `read N PD messages from RX FIFO` when N > 1.

Verified after the fix:

| Charger  | Boot              | U-Boot                     | Linux                                    |
|----------|-------------------|----------------------------|------------------------------------------|
| SyncWire | warm `reboot`     | Soft_Reset, `read 3`, OK   | `read 3` incl. Source_Caps, `SNK_READY`  |
| SyncWire | cold              | OK                         | `read 3`, `SNK_READY`                    |
| Pine     | cold              | OK                         | coalesced case (`b: 0x00` on TX_SUCCESS, one later GCRCSENT), `read 3`, `SNK_READY` |
| Pine     | warm `reboot`     | Soft_Reset, `read 3`, OK   | **power lost**, see below                |
| Pine     | cold (after loss) | OK                         | coalesced case, `read 3`, `SNK_READY`    |

The two Pine cold boots are exactly the pattern that failed before; the old
code would have lost Source_Capabilities there.

UGREEN, 1 cold boot + 5 warm `reboot`s, 12 V / 1.67 A every time:

- U-Boot, all 5 warm reboots: one TX_SUCCESS event with `b: 0x00`, then
  `read 3` (GoodCRC, Accept, Source_Caps `0x3361`). The old code would have
  read only the GoodCRC.
- Linux, all 6 boots: Accept and Source_Caps under a single `GCRCSENT`
  (`read 2`, once `read 3`). The old code would have lost Source_Caps.
- The cold boot started with stale chip state (`HARDRST`, `GCRCSENT`, an
  acknowledged Source_Caps) — the condition that made the UGREEN cut power in
  round 1. U-Boot negotiated normally.

Totals since the fix:

| Charger  | Boots | Soft_Resets (U-Boot + Linux) | Lost to the FIFO bug | Other failures                      |
|----------|-------|------------------------------|----------------------|-------------------------------------|
| SyncWire | 2     | 3                            | 0                    | 0                                   |
| Pine     | 3     | 4                            | 0                    | 1 (power lost after Soft_Reset)     |
| UGREEN   | 6     | 11                           | 0                    | 0                                   |
| SyncWire | 10    | 18 (8 + 10)                  | 0                    | 1 (late Request, see below)         |

The last SyncWire row is a separate run: 8 warm `reboot`s plus 2 cold boots,
20 V / 1.5 A. U-Boot reached `SNK_READY` 10 of 10, Linux 9 of 10. The drain
read several messages 37 times (19 `read 2`, 18 `read 3`) and never lost a
Source_Caps. No Pine-style power loss at 20 V.

## Open: late Request with console tracing on

The one Linux failure in the SyncWire reboot run:

- 3.0636: `read 3` returned GoodCRC, Accept and Source_Caps. The fix worked.
- 3.0915: TCPM sent the Request.
- 3.1032: one IRQ with **COLLISION** and **HARDRST**: the SyncWire had given up
  waiting and was sending Hard Reset as our Request went out. The next U-Boot
  dump has a fresh Source_Caps with `id=0`, confirming it.

| Boots       | Accept read -> Request TX |
|-------------|---------------------------|
| 9 good      | 10.4 - 14.5 ms            |
| the failure | 19.3 ms                   |

The chip acknowledges Source_Caps before the driver reads it, so from the
source's side the Request came ~25 ms after Source_Caps: the low end of
tSenderResponse (24-30 ms). In the failure, reading GoodCRC and Accept took
8.6 ms instead of ~4 ms, while systemd was printing to the same console. With
`console_log` on, every tcpm/fusb302 line goes to the 1.5 Mbaud console from
the IRQ work and the TCPM worker, with `chip->lock` held. A kernel without the
debug patch does not pay this.

Next:

- Repeat the warm-reboot loop with tracing off, close to production timing:
  `extraargs=tcpm.console_log=0 fusb302.console_log=0` in
  `/boot/armbianEnv.txt`. debugfs logs still record surviving boots; U-Boot's
  pre-reset dump still catches failures.
- If it still happens: reduce Linux's Source_Caps -> Request latency, starting
  with `i2c1` at 400 kHz instead of 100 kHz.

## Open: Pine loses power right after Soft_Reset

A separate failure, only seen with the Pine. The SoC loses power a few ms after
a Soft_Reset while the PD exchange is still correct.

Pine warm `reboot`, Linux Soft_Reset at 3.1548 s. The console stops mid-line.
The next U-Boot found the RX FIFO misaligned by one byte. Reassembled:

- GoodCRC for our Soft_Reset, **missing its SOP token**: Linux had read exactly
  one byte of it when the SoC died, ~5 ms after the Soft_Reset.
- Accept, then Source_Capabilities, acknowledged by the chip (`GCRCSENT`).
- Hard Reset (`HARDRST`), sent by the Pine because no Request came.

So power went first; the Hard Reset is a consequence. The Pine kept talking on
CC and the FUSB302 kept working.

Other runs that fit:

| Run                    | Stage                | SoC died                                   |
|------------------------|----------------------|--------------------------------------------|
| first Pine log, boot A | U-Boot after reboot  | ~6 ms after its Soft_Reset                 |
| Pine, before the fix   | Linux                | ~50 ms after Soft_Reset, after the Request |
| Pine, after the fix    | Linux after reboot   | ~5 ms after Soft_Reset                     |

No SyncWire failure fits: every one had a Hard Reset logged before the loss.
After the fix the SyncWire, also at 20 V, went through 18 Soft_Resets without
a sudden power loss, so the 20 V contract alone does not explain it; the Pine
itself is the main suspect.

Hypothesis: the Pine changes VBUS on Soft_Reset (back to 5 V, or a brief cut),
against the spec, and the board browns out at that load. Not proven.

Next:

- Measure VBUS (scope, or a logging USB-C meter) around the Soft_Reset with
  the Pine.
- Test, not done yet: make U-Boot request 5 V only, so Linux's Soft_Reset
  happens on a 5 V contract and Linux moves to 20 V with a normal transition.
  If the Pine failures stop, the hypothesis holds and this is the workaround.
  U-Boot does not need more than 15 W:

  ```dts
  &usb_con1 {
  	power-role = "sink";
  	sink-pdos = <PDO_FIXED(5000, 3000, PDO_FIXED_USB_COMM)>;
  };
  ```

## Other findings

- `CRU GLB_RST_ST` reads `0x00000000` after a software `reboot` too, so it
  cannot tell a reset from a power loss. The debug print is useless as is;
  drop it or read the register in SPL.
- The FUSB302 still keeps its registers and RX FIFO across power loss. The
  pre-reset dumps are what proved the Hard Reset cases and the misaligned
  FIFO above; keep them while debugging.
- Linux uses PD rev 2.0 (DT `pd-revision`); the chargers answer in rev 3 for
  some messages and adapt. No problem seen.

## Vendor trees

Read only; nothing was built or booted from them.

- U-Boot: `/Volumes/LinuxDev/u-boot-rockchip-vendor`. This is Radxa
  `next-dev-v2024.03` plus Mixtile commits `56315a25309` and `2face8e4a3a`
  (Armbian `legacy/u-boot-radxa-rk35xx/board_mixtile-blade3/5000`, `5001`),
  built with `blade3_defconfig`.
- Kernel: `/Volumes/LinuxDev/kernel`, branch `nyanmisaka-rk-6.1-rkr7.2-fixes`.

### Vendor U-Boot probably does no PD under Armbian

- `fusb302_probe()` needs a `connector` subnode. The U-Boot DT
  (`rk3588-blade3.dts`, identical to Armbian's copy) has none, so the probe
  returns `-ENODEV` ("'connector' node is not found").
- The only other source of a `connector` node is the kernel DTB, through
  `USING_KERNEL_DTB_V2`. In the resolved `.config`, `ROCKCHIP_RESOURCE_IMAGE=y`
  and both `ROCKCHIP_EARLY_DISTRO_DTB` and `EMBED_KERNEL_DTB` are off. The kernel
  DTB can therefore only come from a `boot`, `recovery` or `resource`
  partition, and Armbian images have none of these.
- Confirmed on hardware: see "Run: vendor stack, SyncWire" below. The probe
  is not even attempted, because the boot-mode check is broken.
- If this holds, "vendor works" under Armbian means the vendor kernel with no
  PD in U-Boot. The board runs on default 5 V until Linux negotiates.

### What the Mixtile U-Boot commits do

They only matter where a kernel DTB is available.

- `56315a25309` probes `fusb302` from `board_late_init()`.
- It switches the driver from polling to interrupts:
  - The GPIO0_C6 IRQ is hard-coded instead of being taken from the DT.
  - A Rockchip timer IRQ runs the TCPM state machine's delayed transitions.
- `tcpm_poll_event()` spins until the port reaches a READY state, with no
  timeout, because `poll_event_cnt` is no longer incremented. It then
  busy-waits 3 s while IRQs are still serviced.
- Low-power entry is set to NULL. The chip stays at `POWER=0x0F` with its
  interrupts unmasked when Linux starts. Mainline U-Boot goes to
  `PWR_MEDIUM` (`0x03`).
- `tcpm_pd_transmit()` no longer waits for the TX result, so it acts on the
  `tx_status` of the previous message.
- The BC_LVL debounce `msleep` is commented out. This is the bug that
  `e6d3a560de1` fixes.
- It still reads one message per `GCRCSENT`, which is bug 3 above.
- The handover is the same as ours: SW reset, then `vbus_never_low`, then a
  Soft_Reset on warm reboot.
- `2face8e4a3a` probes only in the normal, recovery and undefined boot modes.
  It works around the unbounded spin, which hung loader/adb mode.

### Vendor kernel fixes missing from mainline

- `99321070f1a08` "usb: typec: tcpm: fusb302: fix pd rx packet loss"
  (Frank Wang, Rockchip, 2023-02):
  - On `GCRCSENT` it reads until `STATUS1.RX_EMPTY` is set.
  - On `TX_SUCCESS` it only reports TX complete. The GoodCRC is read out by
    the `GCRCSENT` drain.
  - Its stated symptom is lost Source_Caps during renegotiation.
  - This is bug 3, found independently and never upstreamed. Cite it in the
    upstream drain patch.
- `7f0e3549fd217` "usb: typec: fusb302: amend irq work to rt priority":
  - IRQ work runs on a dedicated kthread worker with `sched_set_fifo()`.
  - Mainline uses `schedule_work()` on the system workqueue.
  - Candidate fix for the late-Request open item, to try alongside
    `console_log=0`.
- `8dc7042e4b308` "usb: typec: tcpm: fix source caps may lost after soft
  reset":
  - Turns PD RX on before sending Soft_Reset.
  - Skips the FIFO-flushing `set_pd_rx()` when entering
    `SNK_WAIT_CAPABILITIES` from `SOFT_RESET_SEND`.
  - Posted upstream as
    [4/4](https://lore.kernel.org/all/20230313025843.17162-5-frank.wang@rock-chips.com/)
    and dropped after review; see "Prior art on lore.kernel.org".
  - Mainline mostly covers this with Reichel's
    ["fusb302: cache PD RX state"](https://lore.kernel.org/all/20250704-fusb302-race-condition-fix-v1-1-239012c0e27a@kernel.org/),
    which this tree carries as the backport `8887a1d1`.
- `765b15bf` takes the PD revision from the DT `pd-revision`, which mainline
  already respects.
- `30e84167` changes the CC setting on PORT_RESET and was superseded by the
  upstream PORT_RESET fixes, which this tree also carries.

### Vendor Blade 3 DT (`rk3588-mixtile-blade3.dts`, USB-C1)

| Property                | Vendor                                         | Mainline (ours)                       |
|-------------------------|------------------------------------------------|---------------------------------------|
| `power-role`            | dual, `try-power-role = "sink"`                | sink                                  |
| `sink-pdos`             | 5 V 1 A fixed, 5–20 V 1 A var, 5–20 V 1 A PPS  | 5 V 3 A fixed, 5–20 V 3 A var         |
| `op-sink-microwatt`     | 15 W                                           | 15 W                                  |
| `faster-pd-negotiation` | yes                                            | not supported                         |

- `faster-pd-negotiation` is a Radxa tcpm hack (`2e949abc`), also used on the
  ROCK 5B and 5B+. It sets these handover timers to 100 ms:
  - the CC debounce in `SNK_ATTACH_WAIT`
  - the Source_Caps wait before Soft_Reset (`PD_T_SINK_WAIT_CAP`)
  - `PORT_RESET_WAIT_OFF` (`PD_T_PS_SOURCE_OFF`)

  That makes the Linux handover about 1 s shorter.
- The 1 A request is another variable for the Pine power loss, next to the
  deferred 5 V-only test.

### Run: vendor stack, SyncWire

Log: `log-vendor-stack-syncwire.txt`. Three boots: one cold, then two warm
reboots.

The stack was:

- vendor U-Boot (`blade3_defconfig`) with `5003-DEBUG-...`
- the vendor 6.1 kernel with the debug commit `02dd2b0692882`

**Vendor U-Boot never probes the FUSB302.**

- The boot-mode check in `2face8e4a3a` is broken. It compares the raw boot-mode
  register with the `BOOT_MODE_*` enum indices from `boot_rkimg.h`
  (`NORMAL = 0`, `RECOVERY = 1`, ...).
- The register does not hold those values:
  - After a reboot it holds `0x5242c300`. That is `BOOT_NORMAL`
    (`REBOOT_FLAG`), not 0.
  - On the cold boot it held leftover bits, `0x3dc1c78`.
- As a result, the probe was skipped on every boot
  (`pd: boot_mode ..., skipping fusb302`). It can only run if the register
  happens to read 0, 1 or the UNDEFINE index.
- The probe would have failed anyway. The log shows `DM: v2`, then
  `Failed to load DTB, ret=-2` and `No valid DTB, ret=-22`. There is no kernel
  DTB, so there is no `connector` node.
- So under Armbian, the vendor stack does no PD in U-Boot. The board runs on
  default 5 V until Linux negotiates.

**The vendor kernel does the same handover on every boot.**

1. `fusb302` probes at about 4.93 s.
2. `PORT_RESET` takes 100 ms and the attach debounce takes 100 ms.
   `faster-pd-negotiation` shortens both.
3. PD RX turns on. After 100 ms without Source_Caps, the kernel sends
   Soft_Reset.
4. A single `GCRCSENT` IRQ arrives. The drain loop then reads three messages:
   - the GoodCRC for the Soft_Reset
   - the Accept
   - the Source_Caps (7 PDOs: 5/9/12/15/20 V fixed, plus two PPS APDOs)

   This is the bug 3 situation, and Rockchip's `99321070` drain handles it.
5. The kernel requests PDO 4 (20 V, 1 A). Accept and PS_RDY follow, and the
   port reaches `SNK_READY` at about 5.44–5.56 s.
6. Discover Identity completes. There are no Hard Resets and no errors.

| Boot     | Accept read → Request TX | Source_Caps read → Request TX |
|----------|--------------------------|-------------------------------|
| 1 (cold) | 6.1 ms                   | 0.2 ms                        |
| 2 (warm) | 7.1 ms                   | 1.4 ms                        |
| 3 (warm) | 5.9 ms                   | 0.6 ms                        |

- On mainline with console tracing on, Accept read → Request TX took
  10.4–19.3 ms. Console mirroring is also on here, so console printing alone
  does not explain the gap.
- The obvious remaining difference is `7f0e3549`: the RT-priority kthread
  worker for the IRQ. It has not been tested on mainline yet.
- Reading the FIFO is slow: about 2.5–3 ms per message, and about 5.8 ms
  for the 28-byte Source_Caps.

**The cold boot started with FUSB302 state already in place.**

- At pre-reset, the registers were `POWER=0x0f`, `SWITCHES1=0x25`
  (auto-GoodCRC on) and `STATUS1=0x08`.
- One stale Source_Caps (rev 3, id 0, the same 7 PDOs) was in the RX FIFO.
- This matches the finding that the FUSB302 keeps its registers and FIFO
  across power loss.
- It is not clear whether those Source_Caps were received before power-off or
  during this boot. If they had arrived during this boot without an answer,
  the source should have Hard Reset.
- The warm boots had an empty FIFO and `STATUS1=0x28`.

**This run did not cover:**

- the Pine
- a U-Boot that actually speaks PD. The source stays idle until Linux sends
  Soft_Reset, so the "vendor works" result is the vendor kernel's result
  alone.

### Takeaways

1. Try the RT-priority IRQ worker on mainline against the late-Request issue.
2. Cite `99321070` as prior art in the upstream drain patch.
3. Possibly test 1 A sink PDOs with the Pine, as with the deferred 5 V test.

## Prior art on lore.kernel.org

### Tooling

The search used `lei` saved searches, refreshed with `lei up`. The setup is in
`/Volumes/LinuxDev/lore-lei/`:

- `Dockerfile`
- `searches.conf`
- `lore.sh`, with the subcommands `setup`, `searches`, `up`, `ls`, `grep`,
  `show`, `thread` and `export`

The data is in the Docker volume `lore-lei`. The saved searches cover
linux-usb, u-boot and linux-rockchip:

| Search          | Query                                                          | Messages |
|-----------------|----------------------------------------------------------------|----------|
| `fusb302`       | `dfn:.../tcpm/fusb302.c OR s:fusb302` (linux-usb, linux-rockchip) | 641   |
| `tcpm`          | `dfn:.../tcpm/tcpm.c`, since 2018 (linux-usb)                  | 2703     |
| `uboot-tcpm`    | `dfn:drivers/usb/tcpm/ OR s:tcpm OR s:fusb302` (u-boot)        | 204      |
| `pd-power-loss` | fusb302/tcpm with soft/hard reset, source caps, power loss, ... | 1447    |

### Bug 3: nobody upstream has hit it, and Rockchip never posted its fix

- No message on any of the three lists mentions FUSB302 `GCRCSENT`. None
  describes back-to-back messages getting lost in the RX FIFO.
- Rockchip's `99321070` ("fix pd rx packet loss", 2023-02) was never posted.
- Frank Wang's March 2023 series
  ["Fix some defects related Type-C TCPM"](https://lore.kernel.org/all/20230313025843.17162-1-frank.wang@rock-chips.com/)
  included a tcpm-side patch,
  [4/4 "fix source caps may lost after soft reset"](https://lore.kernel.org/all/20230313025843.17162-5-frank.wang@rock-chips.com/).
  This is the vendor `8dc7042e`.
  - Guenter Roeck
    [replied](https://lore.kernel.org/all/f5650fa4-db16-b1e4-f5b4-917fbcabb415@roeck-us.net/):
    "Isn't that a problem of the fusb302 driver that it flushes its buffers
    unconditionally when its set_pd_rx() callback is called?"
  - He also
    [wrote](https://lore.kernel.org/all/7038030f-1d7a-4c91-a255-bec73847b7c9@roeck-us.net/):
    "I see that as a problem in the fusb302 driver ... and I am hesitant to
    work around that problem in the tcpm code."
  - Frank Wang
    [dropped the patch](https://lore.kernel.org/all/6f188a87-f209-b637-27d6-13dba45906d9@rock-chips.com/):
    "Okay, I shall abandon this from the series".
  - The [v4](https://lore.kernel.org/all/20230616075241.27690-1-frank.wang@rock-chips.com/)
    series went in with only "fix cc role at port reset" and "add get max
    power support".
  - The fusb302-side drain was never sent.
- Reichel's
  ["usb: typec: fusb302: cache PD RX state"](https://lore.kernel.org/all/20250704-fusb302-race-condition-fix-v1-1-239012c0e27a@kernel.org/)
  (2025-07,
  [reviewed](https://lore.kernel.org/all/aH4MEsYX43afRO79@kuha.fi.intel.com/)
  by Heikki Krogerus, backported to stable) is the fusb302-side fix that
  Guenter asked for, but only for the flush race. It does not drain multiple
  messages.
- So our drain patch fixes a separate issue that has never been posted
  upstream. Its commit message should:
  - name the Accept + Source_Caps sequence after a Soft_Reset
  - cite Rockchip's `99321070` as independent prior art
  - point to Guenter's 2023 position that this belongs in fusb302, not tcpm

### U-Boot tcpm: fixes posted but not merged

Our tree is v2026.10. `drivers/usb/tcpm/` has only these commits:

- Reichel's original two commits (core framework and fusb302 driver,
  2024-10)
- `78d5f8cb500`
  ["usb: tcpm: fix inverted poll condition in tcpm_pd_transmit()"](https://lore.kernel.org/all/20260618-tcpm-fix-v2-1-57d16534b04f@nxp.com/)
  (Peng Fan, 2026-06). Before this fix,
  `tcpm_pd_transmit()` did not wait for TX completion and went on with a stale
  `tx_status`.
- two tree-wide cleanups

All the U-Boot runs in this report already include the poll fix.

Still on the list, not merged:

- **Reichel,
  ["USB-PD TCPM improvements" v2](https://lore.kernel.org/all/20250226184506.64114-1-sebastian.reichel@collabora.com/)**
  (2025-02-26).
  [v1](https://lore.kernel.org/all/20241031175404.114773-1-sebastian.reichel@collabora.com/)
  was posted 2024-10-31. It has `Tested-by` from
  [Soeren Moch](https://lore.kernel.org/all/0ed21fc1-6982-4c11-a913-bc03dbb541a1@web.de/),
  [Nicolas Frattaroli](https://lore.kernel.org/all/13345767.O9o76ZdvQC@workhorse/)
  (Sige5: "Resolves a problem I've observed with PD supplies where the board
  may bootloop within u-boot") and
  [Marcel Ziswiler](https://lore.kernel.org/all/43d431db9b68b9fffff160abba13b894b2340ad4.camel@codethink.co.uk/)
  (rock5b: "tremendously improves the situation"). In the same message,
  Marcel Ziswiler asked in 2025-06 why it had not landed. The patches:
  - [1/4 "improve handling of some power-supplies"](https://lore.kernel.org/all/20250226184506.64114-2-sebastian.reichel@collabora.com/):
    keep handling PD messages for 50 ms after the ready state. A Cambrionix
    hub sends Get_Sink_Cap, then Soft_Reset, then Hard Reset if nobody
    answers.
  - [2/4 "avoid resets for missing source capability messages"](https://lore.kernel.org/all/20250226184506.64114-3-sebastian.reichel@collabora.com/):
    on a Source_Caps timeout after Soft_Reset, send Get_Source_Cap before
    falling back to Hard Reset. This is the U-Boot port of the kernel's
    `122968f8dda82`
    ([posted](https://lore.kernel.org/all/20240523171806.223727-1-sebastian.reichel@collabora.com/)
    2024-05), which mainline 7.3 has and the vendor 6.1 kernel lacks.
  - 3/4: print an error before sending a Hard Reset.
  - 4/4: better recovery from a data role mismatch.
- **Peng Fan,
  ["usb: Add TCPCI driver and DWC3 OTG dual-role support" v2](https://lore.kernel.org/all/20260621-tcpci-dwc3-v2-0-990ecacc111c@nxp.com/)**
  (2026-06-21). Marek Vasut
  [is waiting](https://lore.kernel.org/all/a6a9f87a-5009-4307-a761-352be017e930@mailbox.org/)
  for Reichel to review the TCPM parts (2026-07-11). The patches relevant
  here:
  - [01/10](https://lore.kernel.org/all/20260621-tcpci-dwc3-v2-1-990ecacc111c@nxp.com/):
    sink-only ports go to `SNK_READY` instead of Hard Reset when Source_Caps
    time out, or when Soft_Reset fails.
  - [02/10](https://lore.kernel.org/all/20260621-tcpci-dwc3-v2-2-990ecacc111c@nxp.com/):
    keep polling for 500 ms after READY to answer messages the source sends
    after the contract, such as Get_Sink_Cap.
  - [03/10](https://lore.kernel.org/all/20260621-tcpci-dwc3-v2-3-990ecacc111c@nxp.com/):
    PD tracing to a RAM ring buffer, with no serial overhead.

Reichel's 1/4 and Peng Fan's 02/10 are the upstream form of the vendor
U-Boot's 3 s servicing window. They also cover the open "wait 5–10 min at the
U-Boot prompt" test, though only partly: both stop servicing after
50–500 ms.

Peng Fan's 01/10 removes U-Boot's own Hard Reset for sink-only ports, so it
would stop the power loss that U-Boot causes itself. We now make USB-C1
sink-only in the U-Boot DT, so it would apply to the Blade 3. It would not help
when the source decides to Hard Reset, as in bug 3 or the Pine case.

### Why the FUSB302 keeps its state (Reichel, U-Boot 2/4)

From the commit message of
[U-Boot 2/4](https://lore.kernel.org/all/20250226184506.64114-3-sebastian.reichel@collabora.com/):

> The board resets, but the fusb302 registers are not reset. This is because
> of a hardware glitch. The serial pins are high when no data is exchanged.
> Apparently the RK3588 has protection diodes, which leak some voltage into
> the power-domain. The Rock 5B serial pins and the fusb302 are using the same
> 3.3V power domain and the leaked voltage is enough to keep the fusb302
> registers alive.

What this means for the Blade 3:

- It probably explains why the FUSB302 keeps its registers and FIFO across
  power loss here too, through the attached serial adapter. Not verified on
  the Blade 3 schematic.
- It probably explains the cold-boot stale Source_Caps with `SWITCHES1=0x25`
  in the vendor run.
- It also suggests a test: power-cycle with the serial adapter unplugged (or
  its TX line disconnected), and see whether the stale state goes away.

Reichel describes a boot loop that follows from this. After a Hard Reset, the
source sends Source_Caps, and the still-configured chip auto-acks them before
U-Boot probes. The source then expects a Request that never comes. It is the
same kind of failure as the misaligned FIFO we found after the Pine power
loss.

### Never posted upstream

These have no hits on any of the three lists:

- `faster-pd-negotiation` (Radxa, `2e949abc`)
- Rockchip's RT-priority fusb302 IRQ worker (`7f0e3549`). Badhri moved the
  tcpm workqueue to RT priority in 2020
  (["Migrate workqueue to RT priority for processing events" v5](https://lore.kernel.org/all/20200731065830.3744049-1-badhri@google.com/)).
  The fusb302 IRQ work is still on the system workqueue in mainline.

### Takeaways

1. Carry Reichel's U-Boot "USB-PD TCPM improvements" v2 (at least 1/4 and
   2/4) in Armbian, and add our `Tested-by` on the list.
2. Watch Peng Fan's series: 01/10 and 02/10 overlap with 1. Rebase our U-Boot
   patches if it lands first.
3. Upstream the kernel drain patch to linux-usb. Cc Guenter Roeck, Heikki
   Krogerus and Sebastian Reichel, and point to
   [Guenter's 2023 reply](https://lore.kernel.org/all/7038030f-1d7a-4c91-a255-bec73847b7c9@roeck-us.net/).
4. Send the U-Boot drain and BC_LVL fixes to the u-boot list. Cc Reichel and
   Marek Vasut.
5. Test whether the serial adapter keeps the FUSB302 powered on the Blade 3.

## Commits (2nd round)

U-Boot, `armbian-armsurvivors-mixtile-blade3-edge-20261022-debug-usbpd`:

| Commit        | Upstream | Description                                                     |
|---------------|----------|-----------------------------------------------------------------|
| `84c8d44cb2c` | Armbian  | arm: dts: rockchip: blade3: make USB-C1 sink-only in U-Boot     |
| `e6d3a560de1` | yes      | usb: tcpm: fusb302: really delay BC_LVL handling on CC activity |
| `d92ab23bb72` | yes      | usb: tcpm: fusb302: drain RX FIFO on TX_SUCCESS/GCRCSENT        |
| `d9d7ce9b471` | no       | DEBUG: tcpm/fusb302: USB-PD bring-up tracing for Blade 3        |

The four debug commits listed above were squashed into `d9d7ce9b471`.

Kernel, `armbian-armsurvivors-rockchip64-7.3-20261022-blade3-tcpm-fusb302-debug`:

| Commit          | Upstream | Description                                                          |
|-----------------|----------|----------------------------------------------------------------------|
| `c1970641078dd` | yes      | usb: typec: tcpm: fusb302: drain RX FIFO on TX_SUCCESS/GCRCSENT      |
| `c3efd0b468b91` | no       | DEBUG: usb: typec: tcpm/fusb302: console PD tracing for Blade 3      |

Armbian `extensions`:

| Commit       | Patch                                                                                |
|--------------|--------------------------------------------------------------------------------------|
| `2cfb02d486` | kernel DT: USB-C1 sink-only                                                          |
| `513a74cecd` | `rockchip64-7.3/913-debug-tcpm-fusb302.patch`                                        |
| `0971fcebc6` | `rockchip64-7.3/912-usb-typec-tcpm-fusb302-drain-rx-fifo-on-tx_success-gcrcsent.patch` |
| `02a270b635` | `u-boot/v2026.10/board_mixtile-blade3/020-usb-tcpm-fusb302-drain-rx-fifo-on-tx_success-gcrcsent.patch` |

Both drain-FIFO fixes pass checkpatch (kernel: `--strict`, clean; U-Boot: only
the `Assisted-by:` trailer) and build without the debug patches.

# 3rd round

## Setup

- U-Boot: round-2 fixes plus Reichel's
  [U-Boot "USB-PD TCPM improvements" v2](https://lore.kernel.org/all/20250226184506.64114-1-sebastian.reichel@collabora.com/),
  all four patches, picked with b4 and rebased under the debug commit.
- Kernel: unchanged from round 2 (drain fix and console tracing).
- Charger: SyncWire.
- Log: `full-log-syncwire-with-fixes-plus-Reichel-with-full-cold-boot.txt`.
  - Boot 1: full cold boot, with the serial adapter also powered off.
  - Boot 2: `reboot` from Linux.

Both boots reached 20 V / 1.5 A in U-Boot and again in the kernel. There were
no Hard Resets and no errors, and the board never lost power.

## The FUSB302 keeps state because of the serial adapter

Boot 1 is the first boot in any of our logs where the FUSB302 really started
from power-on reset. Registers from U-Boot's "before sw reset" dump:

| Log                                                   | SWITCHES1 | POWER  | State           |
|-------------------------------------------------------|-----------|--------|-----------------|
| Every earlier log, boot 1 (including "from poweroff") | `0x25`    | `0x0f` | kept from before |
| Round 3, boot 1 (serial adapter powered off)          | `0x20`    | `0x01` | reset defaults  |
| Round 3, boot 2 (reboot)                              | `0x25`    | `0x0f` | kept from before |

- This closes the round-1 open item and round 2's takeaway 5. It matches
  Reichel's explanation in U-Boot 2/4: the serial pins leak enough voltage
  through the RK3588 protection diodes to keep the chip alive.
- Round 1 had ruled out the adapter's TX line, since disconnecting it did not
  help. Powering the whole adapter off does help. The leak must come through
  another pin, probably the board's TX pin into the adapter's RX input. Not
  measured.
- None of our earlier "cold boot" tests were cold for the PD chip.
- In the field, with no serial adapter attached, a power-off should reset the
  FUSB302.

## U-Boot with Reichel's v2

| Boot | Source_Caps                     | Read → Request TX | SNK_READY | Polling done      |
|------|---------------------------------|-------------------|-----------|-------------------|
| 1    | unprompted, 78 ms after RX on   | 7 ms              | 4019      | 4236 (677 ms)     |
| 2    | none in 310 ms; after Soft_Reset | 10 ms            | 4273      | 4489 (929 ms)     |

- The PD exchange is the same as in round 2's ten-reboot run, message for
  message, and so are its timings.
- The drain fix is still at work: GCRCSENT interrupts read 2–3 messages each.
- 1/4 keeps polling for 100 more loops after SNK_READY. That is meant to be
  50 ms, but with I2C reads and console tracing it takes about 215 ms
  (before: 2 ms). The SyncWire sent nothing in that window.
- 2/4 changes nothing visible with the SyncWire: our tree already sent a
  Soft_Reset when Source_Caps were missing.
- 3/4 and 4/4 were not exercised: no Hard Reset, no data role mismatch.

## Kernel

The same as round 2 on both boots: a Soft_Reset at about 3.15 s, the drain
reads 3 and then 2 messages, and SNK_READY comes at 3.319 s and 3.323 s.

## Takeaways

1. Reichel's v2 works on the Blade 3 with the SyncWire, from a true cold boot
   and from a reboot. That supports our `Tested-by`, with the caveat that this
   is one cold boot and one charger.
2. For cold-boot tests, power the serial adapter off as well, or reset the
   chip from the U-Boot prompt before powering off.
3. Still open:
   - the Pine and other chargers with 030–033
   - the late Request with console tracing on
   - a build without the debug patches

## Commits (3rd round)

U-Boot, `armbian-armsurvivors-mixtile-blade3-edge-20261022-debug-usbpd`:

| Commit        | Upstream       | Description                                                     |
|---------------|----------------|-----------------------------------------------------------------|
| `84c8d44cb2c` | Armbian        | arm: dts: rockchip: blade3: make USB-C1 sink-only in U-Boot     |
| `e6d3a560de1` | yes            | usb: tcpm: fusb302: really delay BC_LVL handling on CC activity |
| `d92ab23bb72` | yes            | usb: tcpm: fusb302: drain RX FIFO on TX_SUCCESS/GCRCSENT        |
| `bf6a39d698d` | Reichel v2 1/4 | usb: tcpm: improve handling of some power-supplies              |
| `874fd9d3ffd` | Reichel v2 2/4 | usb: tcpm: avoid resets for missing source capability messages  |
| `1ac98d46791` | Reichel v2 3/4 | usb: tcpm: print error on hard reset                            |
| `1ee6443a60f` | Reichel v2 4/4 | usb: tcpm: improve data role mismatch error recovery            |
| `1ccfa28aab0` | no             | DEBUG: tcpm/fusb302: USB-PD bring-up tracing for Blade 3        |

`1ccfa28aab0` replaces `d9d7ce9b471`, rebased onto Reichel's patches.

Armbian `extensions`:

| Commit       | Change                                                                                  |
|--------------|-----------------------------------------------------------------------------------------|
| `5392c72290` | adds `u-boot/v2026.10/board_mixtile-blade3/030`–`033` (Reichel v2 1/4–4/4)              |
| `e247a2e88a` | refreshes `u-boot/v2026.10/board_mixtile-blade3/090-debug-tcpm-fusb302.patch`           |

# 4th round: SyncWire through a USB hub

## Setup

- Same U-Boot and kernel as round 3, including Reichel's v2.
- SyncWire → USB-HUB1 → Blade 3 USB-C1. The cable is flipped: CC2,
  polarity 1.
- New serial setup: the console goes to another Rockchip board's `uart3`
  instead of the USB serial adapter.
- Log: `full-log-syncwire-with-usbhub.txt`. Boot 1 is a cold boot; boot 2 is a
  `reboot` from Linux.

Both boots reached a contract in U-Boot and again in Linux. There were no
Hard Resets, no errors, and the board never lost power.

## The hub is the source

The hub sends its own Source_Caps, about 25 W, instead of the SyncWire's:

| PDO | Voltage | Current | Flags (kernel)                       |
|-----|---------|---------|--------------------------------------|
| 0   | 5 V     | 2 A     | `RUDE`: dual-role power + data swap  |
| 1   | 9 V     | 2.45 A  |                                      |
| 2   | 12 V    | 2.09 A  |                                      |
| 3   | 15 V    | 1.67 A  |                                      |
| 4   | 20 V    | 1.25 A  |                                      |

- U-Boot and the kernel both request PDO 2, 12 V / 2.09 A.
- U-Boot boot 1: Source_Caps arrive unprompted. Boot 2: a Soft_Reset first,
  then Accept, Source_Caps, Request, Accept and PS_RDY. The drain reads 2–3
  messages per GCRCSENT.
- Linux, both boots: a Soft_Reset, then SNK_READY at 3.317 s and 3.298 s.
- U-Boot boot 1, about 0.9 s after SNK_READY: the hub sends VCONN_Swap (U-Boot
  answers Not_Supported), then DR_Swap (U-Boot rejects it). The hub accepts
  both answers. CC2 flips between Rp 3.0 and 1.5 around these messages; that
  is PD 3.0 collision avoidance (SinkTxOk/SinkTxNG).
- No swap requests in Linux.

## Open: U-Boot waits 4.5 s for a DR_Swap it will reject

| Boot | SNK_READY | Polling done | Spent after SNK_READY |
|------|-----------|--------------|-----------------------|
| 1    | 4102      | 9670         | 5.6 s                 |
| 2    | 4280      | 8796         | 4.5 s (no swap sent)  |

Without the hub, the time after SNK_READY was 2 ms, and about 215 ms with
Reichel's 1/4.

Cause, in `drivers/usb/tcpm/tcpm.c` (Rockchip-derived code, not from
Reichel's series):

- When Source_Caps arrive (`tcpm_pd_data_request()`, `PD_DATA_SOURCE_CAP`),
  tcpm sets `port->wait_dr_swap_message = true` if PDO 0 is fixed and has both
  `PDO_FIXED_DUAL_ROLE` and `PDO_FIXED_DATA_SWAP`. It does this whatever our
  own port type is.
- On entering `SNK_READY`, if that flag is set, tcpm calls
  `tcpm_reset_event_cnt()`.
- `tcpm_poll_event()` does not stop at SNK_READY while
  `wait_dr_swap_message` is set. It polls until `poll_event_cnt` reaches
  `TCPM_POLL_EVENT_TIME_OUT` (2000).
- The flag is cleared only after a completed DR_Swap, a Hard Reset, or a port
  reset.
- Our port is sink-only (`port_type != TYPEC_PORT_DRP`), so `PD_CTRL_DR_SWAP`
  is always answered with Reject, and the swap never completes. The full 2000
  loops always run, whether or not the hub sends a DR_Swap.
- The code comment assumes 500 µs per loop (1 s in total). With FUSB302 I2C
  reads in every `poll_event()`, a loop takes about 2.25 ms, so 4.5 s.
- Every received message (`tcpm_pd_receive()`) and every completed transmit
  (`tcpm_pd_transmit_complete()`) also sets the counter back to zero. So
  boot 1's swap exchange around 5.05–5.15 s restarted the wait, and boot 1
  took 5.6 s instead of 4.5 s.

Affected sources: anything that advertises dual-role power plus data swap.
That means self-powered hubs, docks and laptops, but not plain chargers. The
cost is boot time only.

Fix needed (not written yet):

1. Set `wait_dr_swap_message` only when the swap can succeed:
   `port->port_type == TYPEC_PORT_DRP` (and maybe `port->typec_caps.data`
   dual).
2. Clear `wait_dr_swap_message` when tcpm answers `PD_CTRL_DR_SWAP` with
   Reject or Wait, so a refused swap ends the wait.
3. Optionally, base the DR_Swap wait on time (`get_timer()`, about 1 s)
   instead of a loop count, so its length doesn't depend on I2C speed or
   debug output. The 100-loop wait from Reichel's 1/4 has the same problem
   (50 ms on paper, 215 ms measured).
4. Upstreamable. Cc Reichel, since it touches the same post-READY polling as
   their 1/4.

## The serial adapter was what kept the FUSB302 alive

Both boots show power-on defaults before U-Boot's software reset
(`SWITCHES1=0x20`, `POWER=0x01`). That includes boot 2, a `reboot` where Linux
had just left the chip in U-Boot's low-power state (`POWER=0x03`) and the hub
kept its contract (VBUS stayed up, and U-Boot had to Soft_Reset).

| Run     | Serial                     | Reboot: SWITCHES1 / POWER |
|---------|----------------------------|---------------------------|
| Round 3 | USB serial adapter         | `0x25` / `0x0f` (kept)    |
| Round 4 | other board's `uart3`      | `0x20` / `0x01` (reset)   |

- On reboot, the Blade 3 really does power-cycle the FUSB302's supply,
  probably through the RK806 reset sequence. Before this run, the USB serial
  adapter fed enough voltage back through the RK3588's UART pins to keep the
  chip's registers. That is the mechanism Reichel describes in their U-Boot
  2/4.
- With the other board's `uart3` there is no such back-feed, so the chip
  starts clean on every boot.
- So the "FUSB302 keeps state" problem from round 1 comes from the bench
  setup (that particular adapter), not from the board. It can still happen to
  users with a similar adapter attached.
- Not measured: the FUSB302 VDD rail during reboot, and which adapter pin
  leaks.

## Open: power loss when PD RX is enabled mid-message (unchecked SOP token)

Log: `full-log-syncwire-with-hub-flipped-cable.txt`. It runs from `poweroff`,
through a cold power-on with the cable flipped (CC1), to Linux. The first
power-on died in U-Boot; the second one went through cleanly.

U-Boot timeline (ms), first power-on:

| Time      | Event |
|-----------|-------|
| 3567      | attach, `cc1 = rp-3.0` |
| 3619/3624 | IRQ `0x51` / `0x59`: `CRC_CHK` while PD RX is still off (no auto-GoodCRC). The hub is already sending Source_Caps, and `0x08` (ALERT) shows the RX FIFO full from its retries. |
| 3783      | `set pd RX on`: RX flush, TX flush, auto-GoodCRC on, PD interrupts on |
| 3786      | `GCRCSENT`: the chip acknowledged a message |
| 3792–3804 | the drain reads 3 "messages": `sop=0xfb header=0x347f len=12`, `sop=0xa7 header=0x4b0 len=0`, `sop=0x00 header=0x7ffb len=28 crc=00000000`. All passed to tcpm and ignored. |
| 3814      | `HARDRST` from the hub, 28 ms after our GoodCRC: no Request came |
| —         | the hub cuts VBUS for the Hard Reset; the board loses power. The console stops after `SNK_HARD_RESET_SINK_OFF`. |

Reading:

- The source resends Source_Caps every tTypeCSendSourceCap (100–200 ms)
  until one is acknowledged. One arrived while `fusb302_set_pd_rx()` was
  running. The RX flush dropped its start, so the rest landed in the FIFO
  without an SOP token: the FIFO was misaligned. Auto-GoodCRC was already on
  by the end of the packet, so the chip acknowledged it.
- From the hub's side, Source_Caps was delivered, so it waited for a Request
  (tSenderResponse) and then sent a Hard Reset. During a Hard Reset the source
  drops VBUS to vSafe0V, and USB-C1 is the board's only power input.
- This is the same kind of misaligned FIFO as in the Pine case above, but here
  the trigger is the RX enable. It is intermittent and depends on timing:
  - the second power-on got Source_Caps 124 ms after RX on
  - boot 1 of `full-log-syncwire-with-usbhub.txt` got them after 165 ms. Its
    boot 2 was a reboot that went through Soft_Reset.
  - the SyncWire alone got its first Source_Caps 78 ms after RX on

The drivers make it worse: neither U-Boot's nor the kernel's
`fusb302_pd_read_message()` checks the SOP token. FUSB302 RX tokens are
`0xE0` (SOP), `0xC0` (SOP'), `0xA0` (SOP''), `0x80` (SOP'_Debug) and `0x60`
(SOP''_Debug). `0xfb`, `0xa7` and `0x00` are all invalid. The header, length
and CRC that follow are garbage, and the drain then reads past the real
message boundaries.

Fix needed (not written yet), for both U-Boot and the kernel:

1. In `fusb302_pd_read_message()`, check the token against the five valid
   values. If it isn't one of them, log it, flush the RX FIFO
   (`CONTROL1.RX_FLUSH`) and stop draining, instead of handing garbage to
   tcpm.
2. Recover quickly. The chip has already sent GoodCRC, so the source is in
   tSenderResponse (24–30 ms) waiting for a Request. tcpm's own
   `SNK_WAIT_CAPABILITIES` timeout is 310 ms, far too late. Send a Soft_Reset
   right away (for example, the driver reports the corruption and tcpm goes to
   `SOFT_RESET_SEND`). The source then Accepts and resends Source_Caps, as on
   every warm boot.
3. Maybe also narrow the window: enable auto-GoodCRC only after the RX flush
   has completed, and flush again if `STATUS1` shows RX activity during the
   switch. This won't close the race completely: a message can always be in
   flight while RX is enabled.
4. Upstreamable on both sides. The token check alone would have turned this
   from a silent Hard Reset into a visible, recoverable error.

## Takeaways

1. The PD stack (our fixes plus Reichel's v2) works through a self-powered hub
   that offers different PDOs and sends unsolicited swap requests.
2. Write the `wait_dr_swap_message` fix: it saves 4.5 s of boot time with hubs
   and docks.
3. Cold-boot results are only valid for a serial setup that does not
   back-feed the board.
4. Write the SOP token check and Soft_Reset recovery. A source that resends
   Source_Caps can hit the RX-enable race on any cold attach, and then the
   board loses power.

## Side quest: hub data (USB, network, HDMI) through USB-C1

This is a separate topic from PD power input. Power works; this section is
about the hub's other functions. Getting them to work depends on a large set
of unmerged upstream patches. Recorded here so it isn't lost; not a goal of
this work.

The hub has an HDMI output, two USB-A ports and a built-in network adapter.
Log: `fragment-switch-to-use-hub.txt`, plus the follow-up commands.

### Default: the board is the USB device, so nothing comes up

- As a sink, USB-C1 attaches as UFP: `usb-role 2` (device). The hub's
  upstream port has no host to talk to.
- No USB enumeration on `usb@fc400000` (xHCI on USB-C1). There is no DP alt
  mode either, because only the DFP sends Discover Identity, so
  `VDM_DISCOVERY` jumps straight to COMPLETE.
- The hub tries to fix this itself with a DR_Swap. U-Boot rejects it because
  the port is sink-only (see the `wait_dr_swap_message` item above). The hub
  doesn't try again in Linux.

### Manual DR_Swap from Linux works

Command: `echo host > /sys/class/typec/port0/data_role`. The kernel DT still
has `data-role = "dual"`, so tcpm accepts a DR_Swap even though the port is a
power sink.

- The hub accepts the swap: `usb-role 1` (host), `Sink, Host`.
- Discover Identity: `1d5c:7102` (Fresco Logic). SVIDs `0xff01` (DP) and
  `0x1d5c` (vendor, skipped).
- DP mode VDO `0x000c0045`: UFP_D, receptacle, pin assignments C and D. The
  hub prefers multi-function, so D is chosen (`C [D]`).
- Enter Mode, DP Status Update and DP Configure are all acknowledged. Then
  Attention with HPD: the hub sees the monitor.
- xHCI on `fc400000` starts as host (buses 5 and 6). A Genesys `05e3:0610`
  "USB2.1 Hub" with 4 ports enumerates at 480M.

### What works and what doesn't

| Function | Result | Why |
|----------|--------|-----|
| USB-A (USB 2) | works: devices enumerate under `05e3:0610` at 480M | |
| HDMI | doesn't work: monitor shows "no signal", `DP-*` `disconnected` | HPD never reaches `dw-dp`; see below |
| USB 3 | works with the cable in normal orientation; nothing with it reversed | USBDP PHY orientation handling; see below |
| Network | works (ASIX AX88179A, `cdc_ncm`) with the cable in normal orientation | only on the hub's SuperSpeed side |

USB-A, tested after the DR_Swap by plugging devices into the hub:

- Port 3: MFG `1234:0201` 4 GB flash drive. `usb-storage` binds, and it shows
  up as `sda` with partition `sda1`.
- Port 4: MacroSilicon `534d:2109` (MS2109) HDMI capture stick. `uvcvideo`,
  `snd-usb-audio` and `usbhid` bind.
- Both are USB 2 devices (the MS2109 calls itself "USB3. 0 capture" but is a
  USB 2 chip), so this says nothing about SuperSpeed.
- With nothing plugged in, the hub just showed no children. The empty hub in
  the first fragment was not an error.

HDMI:

- The `no extcon found for current port` message comes from the
  out-of-tree patch `2601c5e3d3491` ("notify typec dp hpd state through
  extcon"), an RK3399 cdn-dp workaround. It is noise on RK3588.
- In 7.3, neither `dw_dp-rockchip.c` nor the Synopsys `dw-dp` bridge handles
  Type-C out-of-band HPD. The USBDP PHY doesn't register as a DRM bridge.
  The Blade 3 DT has no graph link between `dp1` and `usb_con1`.
- Needs, all unmerged:
  - Reichel's
    ["Synopsys DisplayPort Controller improvements for Rockchip platforms" v11](https://lore.kernel.org/all/20260806-synopsys-dw-dp-improvements-v11-0-0d508505f383@collabora.com/)
    (21 patches). It covers follow-up bridges (USB-C connector),
    [software-triggered OOB HPD](https://lore.kernel.org/all/20260806-synopsys-dw-dp-improvements-v11-12-0d508505f383@collabora.com/),
    runtime PM and audio. The cover letter mentions a Tested-by on v9 for
    the Orange Pi 5 Plus with USB-C DP alt mode.
  - Reichel's USBDP PHY rework ("Clean up the mess"), split into
    [part 1 v15](https://lore.kernel.org/all/20260915-rockchip-usbdp-cleanup-v15-0-80e2c11d1ce8@collabora.com/)
    (16 patches),
    [part 2 v15](https://lore.kernel.org/all/20260915-rockchip-usbdp-cleanup-part2-v15-0-8d507cb1174f@collabora.com/)
    (11) and
    [part 3 v16](https://lore.kernel.org/all/20260930-b4-rockchip-usbdp-cleanup-part3-v16-0-bc144f80afc4@collabora.com/)
    (7). Earlier it was one 36-patch series
    ([v12](https://lore.kernel.org/all/20260710-rockchip-usbdp-cleanup-v12-0-8b41a9a9bef0@collabora.com/)).
    It makes the USBDP PHY a DRM bridge.
  - A new USBDP DT binding with proper ports (still under discussion), then
    a Blade 3 DT graph `dp1` → USBDP PHY → `usb_con1`.

USB 3, cable reversed (`orientation 2`, CC2):

- A known-good USB 3 pendrive in the hub does not show up at all, not even at
  480M. It links SuperSpeed to the hub's SuperSpeed half, and that half has no
  link up to the board, so it never falls back to USB 2.
- xHCI `portsc`: port 1 (USB 2) `Speed=3 Link=U3 CCS PED` (the hub, idle);
  port 2 (SuperSpeed) `Speed=0 Link=RxDetect PP`. Link training never starts:
  the RK3588 sees no SuperSpeed receiver on the lanes it uses.
- The USBDP PHY logs nothing.

USB 3, cable in normal orientation (`orientation 1`, CC1). Same hub, same
pin assignment D, after a power cycle and the DR_Swap:

- `portsc` port 2: `Speed=4 Link=U0 CCS PP PED`.
- Bus 6 at 5000M: Genesys `05e3:0626` "USB3.1 Hub", 4 ports, with:
  - port 1: ASIX AX88179A (`0b95:1790`), `cdc_ncm`, `enx68da73a37456`. This is
    the hub's network adapter.
  - port 2: the hub's built-in SD card reader (`05e3:0749`, `sda`/`sdb`).
  - port 3: SanDisk Extreme Pro USB 3 pendrive (`0781:5588`, 128 GB, `sdc`).
- So the hub, pin assignment D and the lanes are fine. The USBDP PHY puts
  USB 3 on the wrong lanes when the orientation is reversed. Confirmed on
  USB-C0 too; see "Hub on USB-C0, cable reversed" below. Matches
  "Re-init the PHY on orientation change" and "Do not lose USB3 PHY status"
  in part 1 of Reichel's USBDP rework.
- The network adapter only exists on the SuperSpeed side. That is why it was
  missing in the reversed orientation.

### Hub on USB-C0, SyncWire directly on USB-C1

Log: `full-log-syncwire-direct-plus-usb-hub-on-other-type-c-port.txt`. A cold
boot with the SyncWire on USB-C1 and the hub (no charger of its own) on
USB-C0, the OTG port: FUSB302 `6-0022` on i2c6, typec `port1`.

USB-C0 is wired like USB-C1: `usb_host0_xhci` (`fc000000`) with
`usb-role-switch`, `usbdp_phy0` with mode and orientation switching, a DP
alt mode entry, and `dp0`. Its DT has `power-role = "dual"`,
`try-power-role = "sink"` and `source-pdos = <5 V 1 A>`, and its VBUS comes
from `vbus5v0_typec0`. U-Boot does not probe it.

- USB-C1: U-Boot reached 20 V / 1.5 A in 673 ms, with no DR_Swap wait
  because the SyncWire isn't dual-role. Linux took over with the usual
  Soft_Reset; SNK_READY at 3.326 s.
- USB-C0 roles, automatic:
  - The hub is unpowered and shows Rd. tcpm tries sink first (`SNK_TRY`),
    falls back to source (`SRC_ATTACHED`), turns VBUS on at 2.48 s and
    requests `usb-role 1` (host) with `orientation 1`.
  - `port1`: `[source]`, `[host]`, `normal`.
- USB-C0 PD:
  - The first three Source_Caps get `PD retry failed`; the hub's PD
    controller is still starting on the new VBUS.
  - The fourth is answered: SRC_READY at 3.04 s, the hub on our 5 V / 1 A.
- Discovery runs on its own, because we are the DFP: identity `1d5c:7102`,
  SVIDs `0xff01` and `0x1d5c`, DP mode VDO `0x000c0045`. Enter Mode at
  4.41 s, then Status Update and Configure. Attention with HPD at 5.74 s.
- USB: `xhci-hcd.4.auto` (buses 5 and 6). `portsc` port 2 is
  `Speed=4 Link=U0`. On the Genesys `05e3:0626` SuperSpeed hub at 5000M:
  - port 1: the AX88179A network adapter, `cdc_ncm`, `enx68da73a37456`
  - port 2: the SD card reader
  - port 3: the SanDisk Extreme Pro
- Power budget: nothing dropped off or reset at 5 V / 1 A during boot. Not
  tested under load.
- HDMI: both `DP-*` connectors are `disconnected`, with the same
  `no extcon found` line for `port1-partner.0`. Same cause as on USB-C1:
  there is no Type-C HPD path to `dw-dp` (`dp0` here).

Conclusion: USB-C0 is the right port for a hub or dock. With the charger on
USB-C1 and the hub on USB-C0, the board is the source and the host on its
own. No manual DR_Swap is needed, U-Boot's DR_Swap wait never happens, and
USB 2, USB 3 and the network adapter work. HDMI still needs the unmerged
dw-dp and USBDP series.

### Hub on USB-C0, cable reversed

Log: `fragment-flip-cable-on-other-port.txt`. The cable on USB-C0 was flipped
live; the board stayed powered from USB-C1.

- On unplug, tcpm detaches cleanly: VBUS off, xHCI `fc000000` removed. There
  was a short re-attach in the old orientation while the plug was coming out
  (`SRC_SEND_CAPABILITIES` interrupted). Harmless.
- On re-insert, with `CC1: 0 -> 1, CC2: 0 -> 2`: the same `SNK_TRY` fallback
  to `SRC_ATTACHED`, `Requesting mux state 1, usb-role 1, orientation 2`.
  VBUS on, and SRC_READY after three Source_Caps retries again.
- Discovery and DP Enter Mode work exactly as in normal orientation.
- USB 2: Genesys `05e3:0610` at 480M on bus 5.
- USB 3: bus 6 empty. `portsc` port 2 is
  `0x0e0002e0 Speed=0 Link=Polling PP WCE WDE WOE`. No SuperSpeed hub, so no
  network adapter, card reader or pendrive.

| Port   | Orientation | SuperSpeed port 2 | Bus 6                  |
|--------|-------------|-------------------|------------------------|
| USB-C1 | normal      | `U0`              | hub, NIC, card reader, pendrive |
| USB-C1 | reversed    | `RxDetect`        | empty                  |
| USB-C0 | normal      | `U0`              | hub, NIC, card reader, pendrive |
| USB-C0 | reversed    | `Polling`         | empty                  |

Conclusion: SuperSpeed fails in the reversed orientation on both ports. So it
is the USBDP PHY driver (`phy-rockchip-usbdp.c`), not one PHY instance or the
board wiring.

- The two link states differ:
  - `RxDetect`: no far-end receiver termination seen at all.
  - `Polling`: termination seen, but link training never completes.
- USB-C1's attempt came after a DR_Swap, with the PHY already up in device
  mode. USB-C0's came on a fresh attach as host. Either way, the lane mux or
  the orientation is wrong for pin assignment D in the reversed orientation.
- Expected to be fixed by Reichel's USBDP rework, part 1: "Re-init the PHY on
  orientation change", "Factor out lane_mux_sel setup", "Do not lose USB3 PHY
  status". Not verified.
- With a single hub or dock it matters a lot: whether USB 3 and the network
  adapter work depends on which way round the plug goes in.

Next steps:

- Retest the reversed-orientation USB 3 failure on 7.4 (USBDP parts 1 and 2
  should be in it). See the plan below for why not carrying them on 7.3.
- To make the board the host automatically on USB-C1: a udev rule writing
  `host` to `data_role`, or a kernel-side preference for the host data role.
  Less important now that USB-C0 does this on its own.

### Plan (not pursued): carrying Reichel's USBDP / DWC3 / dw-dp series

This plan was written for carrying the series, then dropped; it is kept for
reference. Status checked on lore on 2026-10-23.

| # | Series | Latest | Status | Relevance |
|---|--------|--------|--------|-----------|
| 1 | [USBDP cleanup part 1](https://lore.kernel.org/all/20260915-rockchip-usbdp-cleanup-v15-0-80e2c11d1ce8@collabora.com/) | v15, 16 patches, 2026-09-15 | applied to phy for-next by Vinod Koul, 2026-10-03 (7.4 material) | new USBDP DT ports binding, "Do not lose USB3 PHY status", DP aux bridge |
| 2 | [USBDP cleanup part 2](https://lore.kernel.org/all/20260915-rockchip-usbdp-cleanup-part2-v15-0-8d507cb1174f@collabora.com/) | v15, 11 patches, 2026-09-15 | applied to phy for-next | "Re-init the PHY on orientation change", "Factor out lane_mux_sel setup", SAFE/USB states, avoid xHCI SErrors. The likeliest fix for the reversed-orientation USB 3 failure. |
| 3 | [DWC3 Rockchip glue driver](https://lore.kernel.org/all/20261021-b4-rockchip-dwc3-rockchip-glue-v18-0-60000d03fca2@collabora.com/) | v18, 7 patches, 2026-10-21 | pending | DWC3/USBDP PHY reset quirk against SErrors and PHY start-up failures; includes 2 USBDP patches |
| 4 | [USBDP cleanup part 3](https://lore.kernel.org/all/20260930-b4-rockchip-usbdp-cleanup-part3-v16-0-bc144f80afc4@collabora.com/) | v16, 7 patches, 2026-09-30 | pending, stale against glue v17/v18 | "Re-init PHY on mux change", USB-C state without DP |
| 5 | [Synopsys dw-dp improvements](https://lore.kernel.org/all/20260806-synopsys-dw-dp-improvements-v11-0-0d508505f383@collabora.com/) | v11, 21 patches, 2026-08-06 | pending (drm-misc) | needed for HDMI: follow-up bridges (USB-C connector), software-triggered OOB HPD, runtime PM, audio |

Not needed:

- "Use DP AltMode defines" v2 (cosmetic DT cleanup).
- The combined 36- and 38-patch series
  ([v12](https://lore.kernel.org/all/20260710-rockchip-usbdp-cleanup-v12-0-8b41a9a9bef0@collabora.com/),
  [v14](https://lore.kernel.org/all/20260813-rockchip-usbdp-cleanup-v14-0-b5ad9c68fa11@collabora.com/)),
  superseded by the split.

Problems found:

- Part 3 v16 vs glue v17/v18. In glue v17, Reichel dropped the generic PHY
  reset notifier API: Vinod preferred a local quirk, after a discussion at
  Plumbers. He also moved `sw_mode` from part 3's "Fix power state handling"
  into the glue series. So part 3's 1/7 "Add phy reset notification support"
  contradicts glue v18, and 5/7 will conflict. A part 3 v17 rebased on glue
  v18 had not been posted yet.
- Part 3 also depends on the glue series. dw-dp v11 has a review note from
  Andy Yan about a conflict with another pending patch.
- Existing Armbian `rockchip64-7.3` patches in the same files. This patch
  set is shared by all rockchip64 boards (RK3399, RK356x, RK3576, RK3588), so
  any change here affects all of them:
  - `rk3576-0012-phy-rockchip-usbdp-replay-hpd-on-dp-phy-init.patch`: USBDP
    HPD replay. Conflicts with part 2's "Drop DP HPD handling".
  - `rk3399-usbc-usb-dwc3-Track-the-power-state-of-usb3_generic_phy.patch`
    and `rk3399-usbc-usb-dwc3-Extend-reset-quirk-support-to-include-role-.patch`
    (Ondrej Jirman): a dwc3 core reset quirk, likely overlapping the glue
    driver's "post PHY registration hook" and USBDP reset quirk.
  - `rk3399-usbc-notify-typec-dp-hpd-state-through-extcon.patch`: the extcon
    hack in `typec/altmodes/displayport.c`. Independent of these series.
- HDMI also needs a new Blade 3 DT graph (`dp0`/`dp1` → USBDP PHY →
  `usb_con0`/`usb_con1`) using part 1's ports binding. No Rockchip board
  upstream has that yet.

Approach, had it gone ahead:

1. In `mainline-kernel` (v7.3 + Armbian patches), apply in order 1 → 2 → 3 →
   4 → 5 with `b4 am` and `git am -3`.
2. Build-test, then export one `.patch` per series to
   `patch/kernel/archive/rockchip64-7.3/`.
3. Then the Blade 3 DT.

Why it was dropped: about 62 patches, three of five series still in flux, and
the Armbian patch set is shared by every rockchip64 board. That is a lot of
risk for a side quest. Parts 1 and 2 (and probably the glue driver) should
arrive with 7.4 anyway. Simpler to revisit then, starting with the
reversed-orientation USB 3 test on a 7.4 kernel.
