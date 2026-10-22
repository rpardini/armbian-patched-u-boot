/* SPDX-License-Identifier: GPL-2.0+ */
/*
 * DEBUG (Armbian, DO NOT UPSTREAM): with CONFIG_TYPEC_TCPM_DEBUG_CONSOLE,
 * print every debug() of the TCPM / FUSB302 drivers on the console, prefixed
 * with the milliseconds since SoC power-on, so the USB PD timeline can be
 * correlated with the source's timeouts.
 *
 * Must be included after <common.h>.
 */

#ifndef __PD_DEBUG_H
#define __PD_DEBUG_H

#include <common.h>

#ifdef CONFIG_TYPEC_TCPM_DEBUG_CONSOLE
#undef debug
#define debug(fmt, ...)						\
	printf("[%7lu] pd: " fmt, get_timer(0), ##__VA_ARGS__)
#endif

/* Always printed, timestamped */
#define pd_info(fmt, ...)					\
	printf("[%7lu] pd: " fmt, get_timer(0), ##__VA_ARGS__)

#endif /* __PD_DEBUG_H */
