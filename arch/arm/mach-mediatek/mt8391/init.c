// SPDX-License-Identifier: GPL-2.0
/*
 * Copyright (C) 2025 MediaTek Inc.
 * Author: Chris-QJ Chen <chris-qj.chen@mediatek.com>
 */

#include <clk.h>
#include <common.h>
#include <dm.h>
#include <fdtdec.h>
#include <ram.h>
#include <asm/arch/misc.h>
#include <asm/armv8/mmu.h>
#include <asm/sections.h>
#include <asm/system.h>
#include <dm/uclass.h>

DECLARE_GLOBAL_DATA_PTR;

int dram_init(void)
{
	int ret;

	if (BOOT_ARGUMENT->magic_number == BOOT_ARGUMENT_MAGIC) {
		gd->ram_base = CONFIG_SYS_SDRAM_BASE;
		gd->ram_size = BOOT_ARGUMENT->dram_size;
		debug("Boot argument DRAM size: %lluGB\n", gd->ram_size >> 30);
	} else {
		ret = fdtdec_setup_mem_size_base();
		if (ret)
			return ret;
	}

	mem_map[0].size = gd->ram_size;
	mem_map[0].phys = gd->ram_base;
	mem_map[0].virt = gd->ram_base;

	/*
	 * Limit gd->ram_top not exceeding SZ_4G.
	 * Because some periphals like mmc requires DMA buffer
	 * allocaed below SZ_4G.
	 *
	 * Note: SZ_1M is for adjusting gd->relocaddr,
	 *       the reserved memory for u-boot itself.
	 */
	if (gd->ram_base + gd->ram_size >= SZ_4G)
		gd->mon_len = (gd->ram_base + gd->ram_size + SZ_1M) - SZ_4G;

	return 0;
}

int dram_init_banksize(void)
{
	gd->bd->bi_dram[0].start = gd->ram_base;
	gd->bd->bi_dram[0].size = gd->ram_size;

	return 0;
}

int mtk_pll_early_init(void)
{
	return 0;
}

int mtk_soc_early_init(void)
{
	return 0;
}

#if !IS_ENABLED(CONFIG_SYSRESET)
void reset_cpu(ulong addr)
{
	psci_system_reset();
}
#endif

const char *query_mediatek_soc_part_name_string(void)
{
	u32 seg = mediatek_sip_segm_name();
	const char *seg_name = NULL;

	switch (seg) {
	case 0x80:
		seg_name = "MT8391AV/AZA";
		break;
	case 0x88:
		seg_name = "MT8391IV/AZA";
		break;
	case 0x81:
		seg_name = "MT8371AV/AZA";
		break;
	case 0x89:
		seg_name = "MT8371IV/AZA";
		break;
	case 0x82:
		seg_name = "MT8371LV/AZA";
		break;
	default:
		seg_name = NULL;
		break;
	}

	return seg_name;
}

int print_cpuinfo(void)
{
	u32 part = mediatek_sip_part_name();
	const char *seg_name = query_mediatek_soc_part_name_string();

	if (seg_name)
		printf("CPU:   MediaTek %s\n", seg_name);
	else if (part)
		printf("CPU:   MediaTek MT%.4x\n", part);
	else
		printf("CPU:   MediaTek MT8391\n");
	return 0;
}

static struct mm_region mt8391_mem_map[] = {
	{
		/* DDR */
		.attrs = PTE_BLOCK_MEMTYPE(MT_NORMAL) | PTE_BLOCK_OUTER_SHARE,
	}, {
		.virt = 0x00000000UL,
		.phys = 0x00000000UL,
		.size = 0x20000000UL,
		.attrs = PTE_BLOCK_MEMTYPE(MT_DEVICE_NGNRNE) |
			 PTE_BLOCK_NON_SHARE |
			 PTE_BLOCK_PXN | PTE_BLOCK_UXN
	}, {
		0,
	}
};

struct mm_region *mem_map = mt8391_mem_map;
