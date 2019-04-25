"""
Evaluation of -.tar.gz file.

Yu Fang - March 2019
"""


from eval import *
import os, sys, glob
import shutil
import tarfile
import xml.dom.minidom
from os.path import join as osj

reg_gt_path = os.path.abspath("./annotations/trackA/")
str_gt_path = os.path.abspath("./annotations/trackB/")


# calculate the gt adj_relations of the missing file
# @param: file_lst - list of missing ground truth file
# @param: cur_gt_num - current total of ground truth objects (tables / cells)
def process_missing_files(file_lst, cur_gt_num):
    if track == "-trackA":
        gt_file_lst_full = [osj(reg_gt_path, filename) for filename in gt_file_lst]
        for file in gt_file_lst_full:
            if os.path.split(file)[-1].split(".")[-1] == "xml":
                gt_dom = xml.dom.minidom.parse(file)
                gt_root = gt_dom.documentElement
                # tables = []
                table_elements = gt_root.getElementsByTagName("table")
                for res_table in table_elements:
                    # t = Table(res_table)
                    # tables.append(t)
                    cur_gt_num += 1
        return cur_gt_num
    elif track == "-trackB1" or track == "-trackB2":
        gt_file_lst_full = [osj(str_gt_path, filename) for filename in gt_file_lst]
        for file in gt_file_lst_full:
            if os.path.split(file)[-1].split(".")[-1] == "xml":
                gt_dom = xml.dom.minidom.parse(file)
                gt_root = gt_dom.documentElement
                tables = []
                table_elements = gt_root.getElementsByTagName("table")
                for res_table in table_elements:
                    t = Table(res_table)
                    tables.append(t)
                for table in tables:
                    cur_gt_num += len(table.find_adj_relations())
        return cur_gt_num


if __name__ == '__main__':
    # measure = eval(*sys.argv[1:])
    gt_file_lst = []

    track = sys.argv[1]
    if track == "-trackA":
        gt_file_lst = os.listdir(reg_gt_path)
    elif track == "-trackB1" or track == "-trackB2":
        gt_file_lst = os.listdir(str_gt_path)
    result_path = sys.argv[2]
    untar_path = "./untar_file/"
    if os.path.exists(untar_path):
        shutil.rmtree(untar_path)
    os.makedirs(untar_path)

    try:
        tar = tarfile.open(result_path, "r:gz")
        tar.extractall(path=untar_path)
        tar.close()
    except FileNotFoundError:
        print("Tar.gz file path incorrect, please check your spelling.")

    res_lst = []
    for root, files, dirs in os.walk(untar_path):
        for name in dirs:
            if name.split(".")[-1] == "xml":
                cur_filepath = osj(os.path.abspath(root), name)
                res_lst.append(eval(track, cur_filepath))
    print("\n")

    # note: results are stored as list of each when iou at [0.6, 0.7, 0.8, 0.9, gt_filename]
    # gt number should be the same for all files
    correct_six, gt_six, res_six = 0, 0, 0
    correct_seven, gt_seven = 0, 0
    correct_eight, gt_eight = 0, 0
    correct_nine, gt_nine = 0, 0

    for each_file in res_lst:

        gt_file_lst.remove(each_file.result[-1])
        correct_six += each_file.result[0].truePos
        gt_six += each_file.result[0].gtTotal
        res_six += each_file.result[0].resTotal

        correct_seven += each_file.result[1].truePos
        gt_seven += each_file.result[1].gtTotal

        correct_eight += each_file.result[2].truePos
        gt_eight += each_file.result[2].gtTotal

        correct_nine += each_file.result[3].truePos
        gt_nine += each_file.result[3].gtTotal

    for file in gt_file_lst:
        if file.split(".") != "xml":
            gt_file_lst.remove(file)
        print(gt_file_lst)
    if len(gt_file_lst) > 0:
        print("\nWarning: missing result annotations for file: {}\n".format(gt_file_lst))
        gt_total = process_missing_files(gt_file_lst, gt_six)
    else:
        gt_total = gt_six

    try:
        print("Evaluation of {}".format(track.replace("-", "")))
        # iou @ 0.6
        p_six = correct_six / res_six
        r_six = correct_six / gt_total
        f1_six = 2 * p_six * r_six / (p_six + r_six)
        print("IOU @ 0.6 -\nprecision: {}\nrecall: {}\nf1: {}\n".format(p_six, r_six, f1_six))

        # iou @ 0.7
        p_seven = correct_seven / res_six
        r_seven = correct_seven / gt_total
        f1_seven = 2 * p_seven * r_seven / (p_seven + r_seven)
        print("IOU @ 0.7 -\nprecision: {}\nrecall: {}\nf1: {}\n".format(p_seven, r_seven, f1_seven))

        # iou @ 0.8
        p_eight = correct_eight / res_six
        r_eight = correct_eight / gt_total
        f1_eight = 2 * p_eight * r_eight / (p_eight + r_eight)
        print("IOU @ 0.8 -\nprecision: {}\nrecall: {}\nf1: {}\n".format(p_eight, r_eight, f1_eight))

        # iou @ 0.9
        p_nine = correct_nine / res_six
        r_nine = correct_nine / gt_total
        f1_nine = 2 * p_nine * r_nine / (p_nine + r_nine)
        print("IOU @ 0.9 -\nprecision: {}\nrecall: {}\nf1: {}\n".format(p_nine, r_nine, f1_nine))
    except ZeroDivisionError:
        print("Error: no adjacency relations are found, please check the file input.")



