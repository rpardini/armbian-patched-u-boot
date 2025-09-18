/* SPDX-License-Identifier: GPL-2.0+ */
/*
 * Configuration for MT8391 based boards
 *
 * Copyright (C) 2025 MediaTek Inc.
 * Author: Chris-QJ Chen <chris-qj.chen@mediatek.com>
 */

#ifndef __MT8391_H
#define __MT8391_H

#include <linux/sizes.h>

#define CONFIG_SYS_NS16550_SERIAL
#define CONFIG_SYS_NS16550_REG_SIZE	-4
#define CONFIG_SYS_NS16550_MEM32
#define CONFIG_SYS_NS16550_COM1		0x11002000
#define CONFIG_SYS_NS16550_CLK		26000000

#define GENIO_720_EVK_FIT_IMAGE_GUID \
	EFI_GUID(0x085DDE70, 0x7863, 0x40F7, 0x86, 0x4F, \
		 0x7E, 0xD4, 0xCA, 0x53, 0x21, 0x78)
#define GENIO_720_EVK_FIP_IMAGE_GUID \
	EFI_GUID(0x3DCBF27F, 0x9E63, 0x49FC, 0x93, 0x74, \
		 0x5A, 0x62, 0x47, 0x21, 0xAD, 0x88)
#define GENIO_720_EVK_BL2_IMAGE_GUID \
	EFI_GUID(0x9EC54F9F, 0x077A, 0x4688, 0xBD, 0xBB, \
		 0xB0, 0xC9, 0xD6, 0x59, 0x47, 0x78)
#define GENIO_720_EVK_FW_IMAGE_GUID \
	EFI_GUID(0x94089703, 0xE6C2, 0x4526, 0xB3, 0xE3, \
		 0x2D, 0x76, 0xA6, 0x5D, 0x0E, 0xC9)
#define GENIO_720_EVK_ENV_IMAGE_GUID \
	EFI_GUID(0x1C56492E, 0xBE13, 0x4E8F, 0x83, 0xAC, \
		 0x45, 0x0A, 0x0B, 0xBA, 0xB5, 0x48)

/* Environment settings */
#include <config_distro_bootcmd.h>

#ifdef CONFIG_CMD_MMC
#define BOOT_TARGET_MMC(func) \
	func(MMC, mmc, 0) \
	func(MMC, mmc, 1)
#else
#define BOOT_TARGET_MMC(func)
#endif

#ifdef CONFIG_CMD_USB
#define BOOT_TARGET_USB(func) func(USB, usb, 0)
#else
#define BOOT_TARGET_USB(func)
#endif

#ifdef CONFIG_CMD_SCSI
#define BOOT_TARGET_SCSI(func) func(SCSI, scsi, 2)
#else
#define BOOT_TARGET_SCSI(func)
#endif

#define BOOT_TARGET_DEVICES(func) \
	BOOT_TARGET_MMC(func) \
	BOOT_TARGET_USB(func) \
	BOOT_TARGET_SCSI(func)

#if !defined(CONFIG_EXTRA_ENV_SETTINGS)
#define CONFIG_EXTRA_ENV_SETTINGS \
	"scriptaddr=0x40000000\0" \
	"fdt_addr_r=0x44000000\0" \
	"fdtoverlay_addr_r=0x44c00000\0" \
	"fdt_resize=0x3000\0" \
	"kernel_addr_r=0x45000000\0" \
	"ramdisk_addr_r=0x46000000\0" \
	"fdtfile=" CONFIG_DEFAULT_FDT_FILE ".dtb\0" \
	"splashimage=" __stringify(CONFIG_SYS_LOAD_ADDR) "\0" \
	"splashsource=mmc_fs\0" \
	"splashfile=logo.bmp\0" \
	"splashdevpart=0#bootassets\0" \
	"splashpos=m,m\0" \
	BOOTENV
#endif

#ifdef CONFIG_ARM64
#define MTK_SIP_PLAT_BINFO		0xC2000529
#endif

/* DRAM */
#define CONFIG_SYS_SDRAM_BASE		0x40000000

#endif
