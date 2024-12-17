/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Copyright (C) 2018 MediaTek Inc.
 */

#ifndef __MEDIATEK_MISC_H_
#define __MEDIATEK_MISC_H_

#define VER_BASE		0x08000000
#define VER_SIZE		0x10

#define APHW_CODE		0x00
#define APHW_SUBCODE		0x04
#define APHW_VER		0x08
#define APSW_VER		0x0c

#define BOOT_ARGUMENT_LOCATION	(0x40000100)
#define BOOT_ARGUMENT_MAGIC	0x504c504c
#define BOOT_ARGUMENT		((struct boot_argument *)BOOT_ARGUMENT_LOCATION)

struct boot_argument {
	unsigned int magic_number;
	unsigned long long dram_size;
};

void mediatek_capsule_update_board_setup(void);

#endif /* __MEDIATEK_MISC_H_ */
