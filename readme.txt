Evaluation Tool for the ICDAR 2019 Competition on Table Detection and Recognition
This tool relies on Numpy and Shapely package.

Usage:
The command line takes 4 parameters as input.
Specify your track with 3rd parameter as flag: -trackA, -trackB1 or -trackB2
Specify your result file (must be a .tar.gz file) with the 4th parameter.


Example:
1. python evaluate.py -trackA ./your-file-path/you-file-name.tar.gz

2. python evaluate.py -trackB1 ./your-file-path/you-file-name.tar.gz

3. python evaluate.py -trackB2 ./your-file-path/you-file-name.tar.gz


Additional Notes:
python evaluate.py -trackA ./result-files/reg.tar.gz
run the above command for a example test.

