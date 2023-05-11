CDT is Qualcomm Configuration Data Table.

## Linux
Install python2.7 and switch to python2.7.
```
git clone https://github.com/lgs2007m/cdt-ipq60xx-generate
cd cdt-ipq60xx-generate/meta-tools/
python2.7 prepareSingleImage.py --arch ipq6018 --fltype emmc --gencdt
```

## Windows
Install python2.7.
```
cd cdt-ipq60xx-generate/meta-tools/
prepareSingleImage.py --arch ipq6018 --fltype emmc --gencdt
```

The cdt binary will be: 

cdt-ipq60xx-generate/meta-tools/ipq6018/in/cdt-AP-CP03-C2_Arthur_512M16(1G)_DDR3.bin
