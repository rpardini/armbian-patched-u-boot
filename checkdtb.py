#!/usr/bin/env python

from pyfdt import *
import argparse

END = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
CYAN = '\033[96m'

def open_config(filename):
    lines = set()
    with open('.config', 'r') as f:
        for line in f.readlines():
            line = line.rstrip()
            if 'CONFIG' in line:
                lines.add(line)
    return lines

def open_dtb(filename):
    with open(filename, 'rb') as f:
        dtb = FdtBlobParse(f)
        rootnode = dtb.to_fdt().get_rootnode()

    phandles = set()
    enabled = set()
    for name, node in rootnode.walk():
        if isinstance(node, FdtNode):
            compatibles = None
            status = 'okay'
            phandle = None
            dr_mode = None
            for subnode in node:
                prop = subnode.get_name()
                if prop == 'compatible':
                    compatibles = subnode.strings
                elif prop == 'status':
                    status = subnode.strings[0]
                elif prop == 'phandle':
                    phandle = subnode.words[0]
                elif prop == 'dr_mode':
                    dr_mode = subnode.strings[0]
            if status == 'okay':
                if phandle is not None:
                    phandles.add(phandle)
                if compatibles is not None:
                    for compatible in compatibles:
                        enabled.add(compatible)
                if dr_mode is not None:
                    enabled.add(f'dr_mode={dr_mode}')

    return rootnode, phandles, enabled

def check_required_configs(configs, lines, prefix):
    for config in configs:
        if config not in lines:
            print('%sWARNING: %s: missing required config \'%s\'%s' % (YELLOW, prefix, config, END))

def check_phandles(rootnode, phandles, prefix):
    pinctrls = pins = gpios = 0
    for name, node in rootnode.walk():
        if isinstance(node, FdtProperty):
            prop = node.get_name()
            if prop in ['pinctrl-0', 'pinctrl-1', 'pinctrl-2']:
                for phandle in node.words:
                    if phandle not in phandles:
                        print('%sERROR: %s: missing phandle %s at %s%s' % (RED, prefix, phandle, name, END))
                    else:
                        pinctrls += 1
            elif prop == 'rockchip,pins':
                for i in range(0, int(len(node.words) / 4)):
                    phandle = node.words[(i * 4) + 3]
                    if phandle not in phandles:
                        print('%sERROR: %s: missing phandle %s at %s%s' % (RED, prefix, phandle, name, END))
                    else:
                        pins += 1
            elif prop in ['gpio', 'gpios', 'reset-gpios', 'mux-gpios']:
                for i in range(0, int(len(node.words) / 3)):
                    phandle = node.words[i * 3]
                    if phandle not in phandles:
                        print('%sERROR: %s: missing phandle %s at %s%s' % (RED, prefix, phandle, name, END))
                    else:
                        gpios += 1
            elif prop in ['interrupt-parent', 'rockchip,cru', 'rockchip,grf', 'rockchip,pmu', 'rockchip,noc', 'rockchip,msch', 'rockchip,sram', 'rockchip,sgrf', 'rockchip,usbgrf', 'rockchip,pipe-grf', 'rockchip,pipe-phy-grf', 'rockchip,php-grf']:
                for phandle in node.words:
                    if phandle not in phandles:
                        print('%sWARNING: %s: missing phandle %s at %s%s' % (YELLOW, prefix, phandle, name, END))
            elif prop == 'dr_mode' and node.strings[0] != 'host':
                print('%sINFO: %s: dr_mode=%s at %s%s' % (PURPLE, prefix, node.strings[0], name, END))

    message = '%s: pinctrls: %d, pins: %d, gpios: %d, phandles: %d' % (prefix, pinctrls, pins, gpios, len(phandles))
    if pinctrls == 0 or pins == 0:
        print('%sWARNING: %s%s' % (YELLOW, message, END))
    else:
        print(message)

def check_compatible_configs(compatible_configs, enabled, prefix):
    all_compatibles = {}
    for config, compatibles in compatible_configs.items():
        for compatible in compatibles:
            if not compatible in all_compatibles:
                all_compatibles[compatible] = set()
            all_compatibles[compatible].add(config)

    found_compatibles = set(all_compatibles.keys()).intersection(enabled)
    for compatible in found_compatibles:
        for config in all_compatibles[compatible]:
            val = '%s=y' % config
            if val not in all_lines:
                print('%sWARNING: %s: maybe missing %s (%s)%s' % (YELLOW, prefix, val, compatible, END))

    for config in compatible_configs:
        if not enabled.intersection(compatible_configs[config]):
            val = '%s=y' % config
            if val in all_lines:
                print('%sWARNING: %s: maybe unneeded %s%s' % (YELLOW, prefix, val, END))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='u-boot.dtb')
    parser.add_argument('--spl', help='spl/u-boot-spl.dtb')
    parser.add_argument('--tpl', help='tpl/u-boot-tpl.dtb')
    args = parser.parse_args()

    all_lines = open_config('.config')
    all_rootnode, all_phandles, all_enabled = open_dtb(args.filename)

    print('MODEL: %s%s%s' % (UNDERLINE, all_rootnode['model'].strings[0], END))
    print('COMPATIBLE: %s' % (', '.join(all_rootnode['compatible'].strings)))

    clk_compatibles = ['fixed-clock','rockchip,rk3288-cru','rockchip,rk3308-cru','rockchip,rk3328-cru','rockchip,rk3399-cru','rockchip,rk3399-pmucru']
    pinctrl_compatibles = ['rockchip,rk3288-pinctrl','rockchip,rk3308-pinctrl','rockchip,rk3328-pinctrl','rockchip,rk3399-pinctrl','rockchip,rk3568-pinctrl','rockchip,rk3588-pinctrl']
    rk8xx_compatibles = ['rockchip,rk805','rockchip,rk806','rockchip,rk808','rockchip,rk809','rockchip,rk816','rockchip,rk817','rockchip,rk818']
    dwmmc_compatibles = ['rockchip,rk3288-dw-mshc']
    sdhci_compatibles = ['rockchip,rk3399-sdhci-5.1','rockchip,rk3568-dwcmshc','rockchip,rk3588-dwcmshc']
    spi_flash_compatibles = ['jedec,spi-nor']
    spi_compatibles = ['rockchip,rk3066-spi','rockchip,rk3288-spi','rockchip,rk3328-spi','rockchip,rk3368-spi','rockchip,rk3399-spi']
    sfc_compatibles = ['rockchip,sfc']
    gmac_compatibles = ['rockchip,rk3288-gmac','rockchip,rk3328-gmac','rockchip,rk3399-gmac']
    gmac_100_compatibles = ['rockchip,rk3308-gmac']
    gmac_qos_compatibles = ['rockchip,rk3568-gmac','rockchip,rk3588-gmac']
    net_compatibles = gmac_compatibles + gmac_100_compatibles + gmac_qos_compatibles
    pcie_compatibles = ['rockchip,rk3399-pcie','rockchip,rk3568-pcie']
    iodomain_compatibles = ['rockchip,rk3288-io-voltage-domain','rockchip,rk3308-io-voltage-domain','rockchip,rk3328-io-voltage-domain','rockchip,rk3399-io-voltage-domain', 'rockchip,rk3399-pmu-io-voltage-domain','rockchip,rk3568-pmu-io-voltage-domain']
    dwc3_compatibles = ['rockchip,rk3328-dwc3','rockchip,rk3399-dwc3','rockchip,rk3568-dwc3','rockchip,rk3588-dwc3']
    rng_compatibles = ['rockchip,rk3288-crypto','rockchip,rk3328-crypto','rockchip,rk3399-crypto','rockchip,cryptov2-rng','rockchip,trngv1']
    efuse_compatibles = ['rockchip,rk3036-efuse','rockchip,rk3066a-efuse','rockchip,rk3128-efuse','rockchip,rk3188-efuse','rockchip,rk3228-efuse','rockchip,rk3288-efuse','rockchip,rk3328-efuse','rockchip,rk3399-efuse']
    otp_compatibles = ['rockchip,px30-otp','rockchip,rk3308-otp','rockchip,rk3568-otp','rockchip,rk3588-otp','rockchip,rv1126-otp']
    regulators_compatibles = ['pwm-regulator','regulator-fixed'] + rk8xx_compatibles
    misc_drivers_compatibles = iodomain_compatibles + efuse_compatibles + otp_compatibles + ['google,cros-ec-spi','google,cros-ec-i2c']
    saradc_compatibles = ['rockchip,saradc','rockchip,rk3066-tsadc','rockchip,rk3399-saradc','rockchip,rk3588-saradc']
    gadget_compatibles = ['dr_mode=otg', 'dr_mode=peripheral']

    if args.tpl and 'CONFIG_TPL=y' in all_lines:
        tpl_rootnode, tpl_phandles, tpl_enabled = open_dtb(args.tpl)

        tpl_configs = [
            'CONFIG_TPL_BOOTROM_SUPPORT=y',
            'CONFIG_TPL_LIBCOMMON_SUPPORT=y',
            'CONFIG_TPL_LIBGENERIC_SUPPORT=y',
            'CONFIG_TPL_ROCKCHIP_BACK_TO_BROM=y',
            'CONFIG_TPL_ROCKCHIP_COMMON_BOARD=y',
            'CONFIG_TPL_OF_CONTROL=y',
            'CONFIG_TPL_RAM=y',
            'CONFIG_TPL_SERIAL=y',
        ]
        check_required_configs(tpl_configs, all_lines, 'TPL')

        if set(pinctrl_compatibles).intersection(all_enabled) and not set(pinctrl_compatibles).intersection(tpl_enabled):
            print('%sWARNING: TPL: missing pinctrl support%s' % (YELLOW, END))
        if set(dwmmc_compatibles).intersection(tpl_enabled):
            print('%sERROR: TPL: DW MMC support enabled%s' % (RED, END))
        if set(sdhci_compatibles).intersection(tpl_enabled):
            print('%sERROR: TPL: SDHCI support enabled%s' % (RED, END))
        if set(spi_flash_compatibles).intersection(tpl_enabled):
            print('%sERROR: TPL: SPI flash support enabled%s' % (RED, END))

        check_phandles(tpl_rootnode, tpl_phandles, 'TPL')

        tpl_compatible_configs = {
            'CONFIG_TPL_CLK': set(clk_compatibles),
            'CONFIG_TPL_DM_SERIAL': set(['snps,dw-apb-uart']),
            'CONFIG_TPL_DRIVERS_MISC': set(misc_drivers_compatibles),
            'CONFIG_TPL_REGMAP': set(['syscon']),
            'CONFIG_TPL_SYSCON': set(['syscon']),
        }
        check_compatible_configs(tpl_compatible_configs, tpl_enabled, 'TPL')


    if args.spl:
        spl_rootnode, spl_phandles, spl_enabled = open_dtb(args.spl)

        spl_configs = [
            '# CONFIG_SPL_RAW_IMAGE_SUPPORT is not set',
            '# CONFIG_SPL_ROCKCHIP_BACK_TO_BROM is not set',
            '# CONFIG_SPL_TINY_MEMSET is not set',
            'CONFIG_SPL_DM_SEQ_ALIAS=y',
            'CONFIG_SPL_FIT_SIGNATURE=y',
            'CONFIG_SPL_FIT=y',
            'CONFIG_SPL_LIBCOMMON_SUPPORT=y',
            'CONFIG_SPL_LIBGENERIC_SUPPORT=y',
            'CONFIG_SPL_LOAD_FIT=y',
            'CONFIG_SPL_MAX_SIZE=0x40000',
            'CONFIG_SPL_OF_CONTROL=y',
            'CONFIG_SPL_ROCKCHIP_COMMON_BOARD=y',
            'CONFIG_SPL_SERIAL=y',
        ]
        if 'CONFIG_ARM64=y' in all_lines:
            spl_configs.append('CONFIG_SPL_ATF=y')
        check_required_configs(spl_configs, all_lines, 'SPL')

        if set(pinctrl_compatibles).intersection(all_enabled) and not set(pinctrl_compatibles).intersection(spl_enabled):
            print('%sWARNING: SPL: missing pinctrl support%s' % (YELLOW, END))
        if set(dwmmc_compatibles).intersection(all_enabled) and not set(dwmmc_compatibles).intersection(spl_enabled):
            print('%sWARNING: SPL: missing DW MMC support%s' % (YELLOW, END))
        if set(sdhci_compatibles).intersection(all_enabled) and not set(sdhci_compatibles).intersection(spl_enabled):
            print('%sWARNING: SPL: missing SDHCI support%s' % (YELLOW, END))
        if set(spi_flash_compatibles).intersection(all_enabled) and not set(spi_flash_compatibles).intersection(spl_enabled):
            print('%sWARNING: SPL: missing SPI flash support%s' % (YELLOW, END))

        check_phandles(spl_rootnode, spl_phandles, 'SPL')

        spl_compatible_configs = {
            'CONFIG_SPL_CLK': set(clk_compatibles),
            'CONFIG_SPL_DM_GPIO': set(['rockchip,gpio-bank']),
            'CONFIG_SPL_DM_REGULATOR_FIXED': set(['regulator-fixed']),
            'CONFIG_SPL_DM_SERIAL': set(['snps,dw-apb-uart']),
            'CONFIG_SPL_GPIO': set(['rockchip,gpio-bank']),
            'CONFIG_SPL_MMC_SDHCI_SDMA': set(sdhci_compatibles),
            'CONFIG_SPL_MMC': set(dwmmc_compatibles + sdhci_compatibles),
            'CONFIG_SPL_PINCTRL_ROCKCHIP': set(pinctrl_compatibles),
            'CONFIG_SPL_PINCTRL': set(pinctrl_compatibles),
            'CONFIG_SPL_PMIC_RK8XX': set(rk8xx_compatibles),
            'CONFIG_SPL_REGMAP': set(['syscon']),
            'CONFIG_SPL_SPI': set(spi_flash_compatibles),
            'CONFIG_SPL_SPI_FLASH_SUPPORT': set(spi_flash_compatibles),
            'CONFIG_SPL_SPI_LOAD': set(spi_flash_compatibles),
            'CONFIG_SPL_DRIVERS_MISC': set(misc_drivers_compatibles),
            'CONFIG_SPL_SYSCON': set(['syscon']),
        }
        check_compatible_configs(spl_compatible_configs, spl_enabled, 'SPL')


    proper_configs = [
        '# CONFIG_USE_PREBOOT is not set',
        'CONFIG_DM_RESET=y',
        'CONFIG_OF_CONTROL=y',
        'CONFIG_OF_LIVE=y',
        'CONFIG_OF_LIBFDT_OVERLAY=y',
        'CONFIG_SYS_NS16550_MEM32=y',
        'CONFIG_SYS_RELOC_GD_ENV_ADDR=y',
        #'CONFIG_SYSINFO=y',
        'CONFIG_SERIAL=y',
    ]
    #if 'CONFIG_NET=y' in all_lines:
    #    proper_configs.append('# CONFIG_NET_RANDOM_ETHADDR is not set')
    if 'CONFIG_SYSRESET_PSCI=y' in all_lines:
        proper_configs.append('# CONFIG_CMD_POWEROFF is not set')
    if 'CONFIG_USB_XHCI_HCD=y' in all_lines:
        proper_configs.append('# CONFIG_USB_XHCI_DWC3 is not set')

    if set(spi_flash_compatibles).intersection(all_enabled):
        spinode = all_rootnode['spi@ff1d0000']
        spiflash = spinode['flash@0'] if spinode else None
        if spiflash:
            proper_configs.append('CONFIG_SF_DEFAULT_BUS=1')
            proper_configs.append('CONFIG_SYS_SPI_U_BOOT_OFFS=0xE0000')
            proper_configs.append('CONFIG_ROCKCHIP_SPI_IMAGE=y')
            spi_max_frequency = spiflash['spi-max-frequency']
            if spi_max_frequency:
                proper_configs.append('CONFIG_SF_DEFAULT_SPEED=%d' % spi_max_frequency.words[0])

    check_required_configs(proper_configs, all_lines, 'U-Boot')

    check_phandles(all_rootnode, all_phandles, 'U-Boot')

    proper_compatible_configs = {
        #'CONFIG_ARM_PSCI_FW': set(['arm,psci-1.0']),
        #'CONFIG_BUTTON': set(['adc-keys', 'gpio-keys']),
        #'CONFIG_LED': set(['gpio-leds']),
        'CONFIG_CLK': set(clk_compatibles),
        #'CONFIG_CMD_GPIO': set(['rockchip,gpio-bank']),
        #'CONFIG_CMD_KASLRSEED': set(rng_compatibles),
        'CONFIG_CMD_PCI': set(pcie_compatibles),
        #'CONFIG_CMD_REGULATOR': set(regulators_compatibles),
        #'CONFIG_CMD_RNG': set(rng_compatibles),
        'CONFIG_CMD_ROCKUSB': set(gadget_compatibles),
        'CONFIG_CMD_USB_MASS_STORAGE': set(gadget_compatibles),
        'CONFIG_DM_ETH_PHY': set(net_compatibles),
        'CONFIG_DM_REGULATOR_FIXED': set(['regulator-fixed']),
        'CONFIG_DM_REGULATOR_GPIO': set(['regulator-gpio']),
        'CONFIG_DM_RNG': set(rng_compatibles),
        'CONFIG_DWC_ETH_QOS_ROCKCHIP': set(gmac_qos_compatibles),
        'CONFIG_DWC_ETH_QOS': set(gmac_qos_compatibles),
        'CONFIG_ETH_DESIGNWARE': set(gmac_compatibles + gmac_100_compatibles),
        'CONFIG_GMAC_ROCKCHIP': set(gmac_compatibles + gmac_100_compatibles),
        'CONFIG_MMC_DW_ROCKCHIP': set(dwmmc_compatibles),
        'CONFIG_MMC_DW': set(dwmmc_compatibles),
        'CONFIG_MMC_SDHCI_ROCKCHIP': set(sdhci_compatibles),
        'CONFIG_MMC_SDHCI_SDMA': set(sdhci_compatibles),
        'CONFIG_MMC_SDHCI': set(sdhci_compatibles),
        'CONFIG_NVME_PCI': set(pcie_compatibles),
        'CONFIG_PCI': set(pcie_compatibles),
        'CONFIG_PCIE_DW_ROCKCHIP': set(['rockchip,rk3568-pcie']),
        'CONFIG_PCIE_ROCKCHIP': set(['rockchip,rk3399-pcie']),
        'CONFIG_PHY_GIGE': set(gmac_compatibles + gmac_qos_compatibles),
        'CONFIG_PHY_ROCKCHIP_INNO_USB2': set(['rockchip,rk3308-usb2phy','rockchip,rk3328-usb2phy','rockchip,rk3399-usb2phy','rockchip,rk3568-usb2phy','rockchip,rk3588-usb2phy']),
        'CONFIG_PHY_ROCKCHIP_NANENG_COMBOPHY': set(['rockchip,rk3568-naneng-combphy','rockchip,rk3588-naneng-combphy']),
        'CONFIG_PHY_ROCKCHIP_PCIE': set(['rockchip,rk3399-pcie-phy']),
        'CONFIG_PHY_ROCKCHIP_SNPS_PCIE3': set(['rockchip,rk3568-pcie3-phy','rockchip,rk3588-pcie3-phy']),
        'CONFIG_PHY_ROCKCHIP_TYPEC': set(['rockchip,rk3399-typec-phy']),
        'CONFIG_PHY_ROCKCHIP_USBDP': set(['rockchip,rk3588-usbdp-phy']),
        'CONFIG_PMIC_RK8XX': set(rk8xx_compatibles),
        'CONFIG_REGULATOR_PWM': set(['pwm-regulator']),
        'CONFIG_REGULATOR_RK8XX': set(rk8xx_compatibles),
        'CONFIG_RNG_ROCKCHIP': set(rng_compatibles),
        'CONFIG_ROCKCHIP_EFUSE': set(efuse_compatibles),
        'CONFIG_ROCKCHIP_GPIO': set(['rockchip,gpio-bank']),
        'CONFIG_ROCKCHIP_IODOMAIN': set(iodomain_compatibles),
        'CONFIG_ROCKCHIP_OTP': set(otp_compatibles),
        'CONFIG_ROCKCHIP_SFC': set(sfc_compatibles),
        'CONFIG_ROCKCHIP_SPI': set(spi_compatibles),
        'CONFIG_PWM_ROCKCHIP': set(['rockchip,rk2928-pwm', 'rockchip,rk3288-pwm', 'rockchip,rk3328-pwm']),
        'CONFIG_SARADC_ROCKCHIP': set(saradc_compatibles),
        'CONFIG_SPI_FLASH_SFDP_SUPPORT': set(spi_flash_compatibles),
        'CONFIG_USB_DWC3_GENERIC': set(dwc3_compatibles),
        'CONFIG_USB_DWC3': set(dwc3_compatibles),
        'CONFIG_USB_EHCI_GENERIC': set(['generic-ehci']),
        'CONFIG_USB_EHCI_HCD': set(['generic-ehci']),
        #'CONFIG_USB_OHCI_GENERIC': set(['generic-ohci']),
        #'CONFIG_USB_OHCI_HCD': set(['generic-ohci']),
        'CONFIG_USB_XHCI_HCD': set(dwc3_compatibles),
        'CONFIG_USB_GADGET': set(gadget_compatibles),
        'CONFIG_USB_GADGET_DOWNLOAD': set(gadget_compatibles),
        'CONFIG_USB_FUNCTION_ROCKUSB': set(gadget_compatibles),
        'CONFIG_DM_PMIC_FAN53555': set(['fcs,fan53555','rockchip,rk8600','rockchip,rk8602','silergy,syr827','silergy,syr828','tcs,tcs4525']),
        'CONFIG_CLK_GPIO': set(['gpio-gate-clock']),
        'CONFIG_BUTTON': set(['adc-keys', 'gpio-keys']),
        'CONFIG_LED': set(['gpio-leds']),
    }
    if 'CONFIG_PHY_MICREL=y' not in all_lines and 'CONFIG_PHY_MOTORCOMM=y' not in all_lines:
        proper_compatible_configs.update({
            'CONFIG_PHY_REALTEK': set(net_compatibles),
        })
    if 'CONFIG_BUTTON=y' in all_lines:
        proper_compatible_configs.update({
            'CONFIG_BUTTON_ADC': set(['adc-keys']),
            'CONFIG_BUTTON_GPIO': set(['gpio-keys']),
        })
    if 'CONFIG_LED=y' in all_lines:
        proper_compatible_configs.update({
            'CONFIG_LED_GPIO': set(['gpio-leds']),
        })
    if 'CONFIG_USB_KEYBOARD=y' in all_lines and 'CONFIG_DISPLAY=y' in all_lines:
        proper_compatible_configs.update({
            'CONFIG_USB_OHCI_GENERIC': set(['generic-ohci']),
            'CONFIG_USB_OHCI_HCD': set(['generic-ohci']),
        })
    #if 'CONFIG_USB=y' in all_lines and 'CONFIG_PCI=y' in all_lines:
    #    proper_compatible_configs.update({
    #        'CONFIG_USB_XHCI_PCI': set(pcie_compatibles),
    #        'CONFIG_USB_EHCI_PCI': set(pcie_compatibles),
    #    })
    if 'CONFIG_AHCI=y' in all_lines and 'CONFIG_PCI=y' in all_lines:
        proper_compatible_configs.update({
            'CONFIG_SCSI': set(pcie_compatibles),
            'CONFIG_AHCI_PCI': set(pcie_compatibles),
            'CONFIG_SCSI_AHCI': set(pcie_compatibles),
        })
    check_compatible_configs(proper_compatible_configs, all_enabled, 'U-Boot')
