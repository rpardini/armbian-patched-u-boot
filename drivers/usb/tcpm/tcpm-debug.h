/* SPDX-License-Identifier: GPL-2.0+ */
/*
 * DEBUG (DO NOT UPSTREAM): force all TCPM / FUSB302 dev_*() output to the
 * console, regardless of CONFIG_LOG / CONFIG_LOGLEVEL, and prefix every line
 * with the milliseconds since SoC power-on (arch timer), so the USB PD
 * timeline can be correlated with the ~5 s source capability deadline.
 *
 * Register write tracing and PD message / PDO dumps are only printed with
 * CONFIG_TYPEC_TCPM_DEBUG_VERBOSE, as they are slow enough to break PD timing.
 *
 * Must be included after <dm/device_compat.h>.
 */

#ifndef __TCPM_DEBUG_H
#define __TCPM_DEBUG_H

#include <dm/device.h>
#include <dm/device_compat.h>
#include <time.h>
#include <usb/tcpm.h>

/* Both FUSB302s are usb-typec@22, so also print the I2C bus they sit on */
#define __tcpm_dbg_printk(lvl, dev, fmt, ...)				\
	printf("[%7lu] " lvl " %s %s/%s: " fmt, get_timer(0),		\
	       (dev)->driver->name, (dev)->parent->name, (dev)->name,	\
	       ##__VA_ARGS__)

#undef dev_err
#undef dev_warn
#undef dev_info
#undef dev_dbg
#define dev_err(dev, fmt, ...)	__tcpm_dbg_printk("E", dev, fmt, ##__VA_ARGS__)
#define dev_warn(dev, fmt, ...)	__tcpm_dbg_printk("W", dev, fmt, ##__VA_ARGS__)
#define dev_info(dev, fmt, ...)	__tcpm_dbg_printk("I", dev, fmt, ##__VA_ARGS__)
#define dev_dbg(dev, fmt, ...)	__tcpm_dbg_printk("D", dev, fmt, ##__VA_ARGS__)

/* Decode a PD message header and dump its data objects */
static inline void tcpm_dbg_dump_msg(struct udevice *dev, const char *dir,
				     const struct pd_message *msg)
{
	u16 header = le16_to_cpu(msg->header);
	unsigned int cnt = pd_header_cnt(header);
	unsigned int i;

	if (!IS_ENABLED(CONFIG_TYPEC_TCPM_DEBUG_VERBOSE))
		return;

	dev_dbg(dev, "PD %s hdr=0x%04x %s type=%u cnt=%u id=%u rev=%u pwr=%s data=%s\n",
		dir, header, cnt ? "DATA" : "CTRL", pd_header_type(header),
		cnt, pd_header_msgid(header), pd_header_rev(header) + 1,
		header & PD_HEADER_PWR_ROLE ? "src" : "snk",
		header & PD_HEADER_DATA_ROLE ? "dfp" : "ufp");
	for (i = 0; i < cnt; i++)
		dev_dbg(dev, "PD %s   obj[%u]=0x%08x\n", dir, i,
			le32_to_cpu(msg->payload[i]));
}

/* Human readable dump of a PDO */
static inline void tcpm_dbg_dump_pdo(struct udevice *dev, const char *what,
				     unsigned int idx, u32 pdo)
{
	if (!IS_ENABLED(CONFIG_TYPEC_TCPM_DEBUG_VERBOSE))
		return;

	switch (pdo_type(pdo)) {
	case PDO_TYPE_FIXED:
		dev_dbg(dev, "%s PDO %u: 0x%08x FIXED %u mV %u mA%s%s%s%s\n",
			what, idx, pdo, pdo_fixed_voltage(pdo),
			pdo_max_current(pdo),
			pdo & PDO_FIXED_DUAL_ROLE ? " DRP" : "",
			pdo & PDO_FIXED_EXTPOWER ? " EXTPWR" : "",
			pdo & PDO_FIXED_USB_COMM ? " USBCOMM" : "",
			pdo & PDO_FIXED_DATA_SWAP ? " DRSWAP" : "");
		break;
	case PDO_TYPE_VAR:
		dev_dbg(dev, "%s PDO %u: 0x%08x VAR %u-%u mV %u mA\n",
			what, idx, pdo, pdo_min_voltage(pdo),
			pdo_max_voltage(pdo), pdo_max_current(pdo));
		break;
	case PDO_TYPE_BATT:
		dev_dbg(dev, "%s PDO %u: 0x%08x BATT %u-%u mV %u mW\n",
			what, idx, pdo, pdo_min_voltage(pdo),
			pdo_max_voltage(pdo), pdo_max_power(pdo));
		break;
	default:
		dev_dbg(dev, "%s PDO %u: 0x%08x APDO\n", what, idx, pdo);
		break;
	}
}

#endif /* __TCPM_DEBUG_H */
