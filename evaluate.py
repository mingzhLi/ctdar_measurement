from eval import *
import os, sys, glob
import tarfile
from os.path import join as osj

if __name__ == '__main__':
    # measure = eval(*sys.argv[1:])

    track = sys.argv[1]
    result_path = sys.argv[2]
    untar_path = "./untar_file/"
    if not os.path.exists(untar_path):
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

    # note: results are stored as list of each when iou at [0.6, 0.7, 0.8, 0.9]
    correct_six, gt_six, res_six = 0, 0, 0
    correct_seven, gt_seven, res_seven = 0, 0, 0
    correct_eight, gt_eight, res_eight = 0, 0, 0
    correct_nine, gt_nine, res_nine = 0, 0, 0

    for each_file in res_lst:
        # print(each_file.result)
        # for el in each_file.result:
        #     print(el)

        correct_six += each_file.result[0].truePos
        gt_six += each_file.result[0].gtTotal
        res_six += each_file.result[0].resTotal

        correct_seven += each_file.result[1].truePos
        gt_seven += each_file.result[1].gtTotal
        res_seven += each_file.result[1].resTotal

        correct_eight += each_file.result[2].truePos
        gt_eight += each_file.result[2].gtTotal
        res_eight += each_file.result[2].resTotal

        correct_nine += each_file.result[3].truePos
        gt_nine += each_file.result[3].gtTotal
        res_nine += each_file.result[3].resTotal

    print("Evaluation of {}".format(track.replace("-", "")))
    # iou @ 0.6
    p_six = correct_six / res_six
    r_six = correct_six / gt_six
    f1_six = 2 * p_six * r_six / (p_six + r_six)
    print("IOU @ 0.6 :\nprecision: {}\nrecall: {}\nf1: {}\n".format(p_six, r_six, f1_six))

    # iou @ 0.7
    p_seven = correct_seven / res_seven
    r_seven = correct_seven / gt_seven
    f1_seven = 2 * p_seven * r_seven / (p_seven + r_seven)
    print("IOU @ 0.7 :\nprecision: {}\nrecall: {}\nf1: {}\n".format(p_seven, r_seven, f1_seven))

    # iou @ 0.8
    p_eight = correct_eight / res_eight
    r_eight = correct_eight / gt_eight
    f1_eight = 2 * p_eight * r_eight / (p_eight + r_eight)
    print("IOU @ 0.8 :\nprecision: {}\nrecall: {}\nf1: {}\n".format(p_eight, r_eight, f1_eight))

    # iou @ 0.9
    p_nine = correct_nine / res_nine
    r_nine = correct_nine / gt_nine
    f1_nine = 2 * p_nine * r_nine / (p_nine + r_nine)
    print("IOU @ 0.9 :\nprecision: {}\nrecall: {}\nf1: {}\n".format(p_nine, r_nine, f1_nine))



