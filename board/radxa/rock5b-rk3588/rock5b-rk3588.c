// SPDX-License-Identifier: GPL-2.0+
/*
 * Copyright (c) 2023-2024 Collabora Ltd.
 */

#include <adc.h>
#include <env.h>
#include <time.h>
#include <asm/io.h>
#include <asm/arch-rockchip/cru_rk3588.h>
#include <fdtdec.h>
#include <fdt_support.h>
#include <asm/arch-rockchip/sdram.h>
#include <linux/errno.h>

#define PMU1GRF_BASE		0xfd58a000
#define OS_REG2_REG		0x208

#define HW_ID_CHANNEL		5

struct board_model {
	unsigned int dram;
	unsigned int low;
	unsigned int high;
	const char *fdtfile;
};

static const struct board_model board_models[] = {
	{ LPDDR5,  926, 1106, "rockchip/rk3588-rock-5t.dtb" },
	{ LPDDR5, 4005, 4185, "rockchip/rk3588-rock-5b-plus.dtb" },
};

static const struct board_model *get_board_model(void)
{
	unsigned int val, dram_type;
	int i, ret;

	dram_type = rockchip_sdram_type(PMU1GRF_BASE + OS_REG2_REG);

	ret = adc_channel_single_shot("adc@fec10000", HW_ID_CHANNEL, &val);
	if (ret)
		return NULL;

	for (i = 0; i < ARRAY_SIZE(board_models); i++) {
		unsigned int dram = board_models[i].dram;
		unsigned int min = board_models[i].low;
		unsigned int max = board_models[i].high;

		if (dram == dram_type && min <= val && val <= max)
			return &board_models[i];
	}

	return NULL;
}

int rk_board_late_init(void)
{
	const struct board_model *model;

	/*
	 * DEBUG (DO NOT UPSTREAM): 0 means power-on reset (i.e. the board lost
	 * power, e.g. a USB PD hard reset or brown-out); non-zero bits point
	 * to a watchdog / thermal / software global reset.
	 */
	printf("[%7lu] DEBUG: CRU GLB_RST_ST = 0x%08x\n", get_timer(0),
	       readl(CRU_BASE + RK3588_GLB_RST_ST));

	model = get_board_model();

	if (model)
		env_set("fdtfile", model->fdtfile);

	return 0;
}

int board_fit_config_name_match(const char *name)
{
	const struct board_model *model = get_board_model();

	if (model && !strcmp(name, model->fdtfile))
		return 0;

	return -EINVAL;
}

#ifdef CONFIG_OF_BOARD_SETUP
int ft_board_setup(void *blob, struct bd_info *bd)
{
	if (IS_ENABLED(CONFIG_TYPEC_FUSB302))
		fdt_status_okay_by_compatible(blob, "fcs,fusb302");
	return 0;
}
#endif
