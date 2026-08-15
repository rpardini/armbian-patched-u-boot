// SPDX-License-Identifier: GPL-2.0+

#include <adc.h>
#include <env.h>
#include <fdt_support.h>
#include <asm/arch-rockchip/bootrom.h>
#include <asm/global_data.h>
#include <asm/io.h>
#include <linux/errno.h>
#include <linux/kernel.h>

DECLARE_GLOBAL_DATA_PTR; // Necessary for gd->fdt_blob access in spl_board_fixup_fdt()

#define HW_ID_CHANNEL	5 // ADC channel used to detect the board model in NanoPi 6 series boards

// RK3588 BootROM boot source ID for SPI flash
#define RK3588_BROM_BOOTSOURCE_FSPI_M0	3

struct board_model {
	unsigned int low;
	unsigned int high;
	const char *fdtfile;
	const char *cmdline_arg;
};

// List of supported board models with their ADC voltage ranges, FDT file names, and kernel command line arguments.
static const struct board_model board_models[] = {
	{  604,  844, "rockchip/rk3588s-nanopi-r6s.dtb", "nanopi6_model=r6s" }, // 8Gb variant
	{  848,  1096, "rockchip/rk3588s-nanopi-r6s.dtb", "nanopi6_model=r6s" }, // 4Gb variant

	{  1100,  1368, "rockchip/rk3588s-nanopi-r6c.dtb", "nanopi6_model=r6c" }, // 8Gb variant
	{  1372,  1644, "rockchip/rk3588s-nanopi-r6c.dtb", "nanopi6_model=r6c" }, // 4Gb variant

	{ 2704, 2932, "rockchip/rk3588s-nanopi-m6.dtb", "nanopi6_model=m6" },
	{ 3184, 3444, "rockchip/rk3588s-nanopi-m6v2.dtb", "nanopi6_model=m6v2" },
};

static const struct board_model *get_board_model(void)
{
	unsigned int val;
	int i, ret;

	ret = adc_channel_single_shot("adc@fec10000", HW_ID_CHANNEL, &val);
	if (ret)
		return NULL;

	for (i = 0; i < ARRAY_SIZE(board_models); i++) {
		unsigned int min = board_models[i].low;
		unsigned int max = board_models[i].high;

		if (min <= val && val <= max)
			return &board_models[i];
	}

	return NULL;
}

// Return the boot source ID from the RK3588 BootROM. This is used to determine if the board booted from SPI or eMMC/SD.
static unsigned int bootrom_boot_source(void)
{
	return readl(BROM_BOOTSOURCE_ID_ADDR);
}

// Return true if the board bootes is NanoPi M6/M6V2, based on the detected board model.
static bool is_m6(const struct board_model *model)
{
	return model && (!strcmp(model->cmdline_arg, "nanopi6_model=m6") || !strcmp(model->cmdline_arg, "nanopi6_model=m6v2"));
}

// Return true if the board booted from SPI, based on the BootROM boot source ID.
static bool booted_from_spi(void)
{
	return bootrom_boot_source() == RK3588_BROM_BOOTSOURCE_FSPI_M0;
}

// Return true if the board booted from M6 with SPI flash, based on the detected board model and BootROM boot source ID.
static bool booted_from_m6_spi(const struct board_model *model)
{
	return is_m6(model) && booted_from_spi();
}

// Board-specific control-FDT fixups which must run before DM discovers it.
// Otherwise, DM may probe the SPI controller and fail if the board booted from eMMC/SD.
void spl_board_fixup_fdt(void)
{
	void *blob = (void *)gd->fdt_blob;
	bool from_spi = booted_from_spi();

	if (!blob)
		return;

	// Only probe the SPI controller if the board booted from it, otherwise disable it in the FDT.
	do_fixup_by_path(blob, "/mmc@fe2e0000", "status",
			 from_spi ? "disabled" : "okay",
			 from_spi ? sizeof("disabled") : sizeof("okay"), 1);
	do_fixup_by_path(blob, "/spi@fe2b0000", "status",
			 from_spi ? "okay" : "disabled",
			 from_spi ? sizeof("okay") : sizeof("disabled"), 1);
}

// Board-specific SPL initialization, called after DM is initialized.
// Left-empty on purpose.
void spl_board_init(void)
{
}

// Set some board-specific environment variables based on the detected model and boot source.
// Used to set kernel FDT file name, bootargs, and boot order for the board.
int rk_board_late_init(void)
{
	const struct board_model *model = get_board_model();
	const char *boot_targets;
	const char *fdtfile;

	// NanoPi R6S/R6C use SD=mmc0 and eMMC=mmc1; M6 uses the opposite aliases.
	if (is_m6(model))
		boot_targets = "mmc1 nvme mmc0 scsi usb pxe dhcp spi";
	else
		boot_targets = "mmc0 nvme mmc1 scsi usb pxe dhcp spi";
	env_set("boot_targets", boot_targets);

	env_set("extraboardargs", model ? model->cmdline_arg : NULL);

	// Set the FDT file name for the board model, if not detected use R6S.
	fdtfile = model ? model->fdtfile : "rockchip/rk3588s-nanopi-r6s.dtb";
	env_set("fdtfile", fdtfile);

	return 0;
}

// Choose the correct FIT configuration name based on the detected board model and boot source.
// Used to choose U-Boot's FIT configuration when loading the image.
int board_fit_config_name_match(const char *name)
{
	const struct board_model *model = get_board_model();
	const char *fit_name;

	if (!model)
		return -EINVAL;

	/* Keep SFC active in U-Boot proper when SPL loaded it from M6 FSPI-M0. */
	if (booted_from_m6_spi(model)) {
		fit_name = !strcmp(model->cmdline_arg, "nanopi6_model=m6v2") ?
			"rockchip/rk3588s-nanopi-m6v2-spi.dtb" : "rockchip/rk3588s-nanopi-m6-spi.dtb";
	} else {
		fit_name = model->fdtfile;
	}
	if (!strcmp(name, fit_name))
		return 0;

	return -EINVAL;
}
