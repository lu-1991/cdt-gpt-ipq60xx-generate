You will also like to see https://github.com/lgs2007m/uboot-ipq60xx-build

CDT is Qualcomm Configuration Data Table.

GPT is GUID Partition Table.

# CDT and GPT generate
## Linux
Install python2.7 and switch to python2.7.
```
git clone https://github.com/lgs2007m/cdt-gpt-ipq60xx-generate
cd cdt-gpt-ipq60xx-generate/meta-tools/
python2.7 prepareSingleImage.py --arch ipq6018 --fltype emmc --gencdt --genpart
```

## Windows
Install python2.7.
```
cd cdt-gpt-ipq60xx-generate/meta-tools/
prepareSingleImage.py --arch ipq6018 --fltype emmc --gencdt --genpart
```

The 1G SDRAM cdt binary will be: 

meta-tools/ipq6018/in/cdt-AP-CP03-C2_Arthur_512M16(1G)_DDR3.bin

The original FSEIASLD-64G-J02 eMMC gpt binary will be: 

meta-tools/ipq6018/in/gpt_main0.bin
