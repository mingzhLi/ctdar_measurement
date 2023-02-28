"""
Evaluation of -.tar.gz file.

Yu Fang - March 2019
"""


from eval import *
import os, sys, glob
from os import getcwd
import shutil
import tarfile
import xml.dom.minidom
from os.path import join as osj
import time
reg_gt_path = os.path.abspath("./annotations/trackA/")
reg_gt_path_archival = os.path.abspath("./annotations/trackA_archival/")
reg_gt_path_modern = os.path.abspath("./annotations/trackA_modern/")
str_gt_path_1 = os.path.abspath("./annotations/trackB1/")
str_gt_path_2 = os.path.abspath("./annotations/trackB2/")
str_gt_path_archival = os.path.abspath("./annotations/trackB2_archival/")
str_gt_path_modern = os.path.abspath("./annotations/trackB2_modern/")

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
    elif track == "-trackB1":
        gt_file_lst_full = [osj(str_gt_path_1, filename) for filename in gt_file_lst]
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
    elif track == "-trackB2":
        gt_file_lst_full = [osj(str_gt_path_2, filename) for filename in gt_file_lst]
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

    t1 = time.time()
    track = sys.argv[1]
    if track == "-trackA":
        gt_file_lst = os.listdir(reg_gt_path)
    elif track == "-trackA1":
        gt_file_lst = os.listdir(reg_gt_path_archival)
    elif track == "-trackA2":
        gt_file_lst = os.listdir(reg_gt_path_modern)
    elif track == "-trackB1":
        gt_file_lst = os.listdir(str_gt_path_1)
    elif track == "-trackB2":
        # print(str_gt_path_2)
        gt_file_lst = os.listdir(str_gt_path_2)
    elif track == "-trackB2_a":
        gt_file_lst = os.listdir(str_gt_path_archival)
    elif track == "-trackB2_m":
        gt_file_lst = os.listdir(str_gt_path_modern)
    result_path = sys.argv[2]
    untar_path = "./untar_file"
    if os.path.exists(untar_path):
        shutil.rmtree(untar_path)
    os.makedirs(untar_path)
    print("unzipped!")

    try:
        tar = tarfile.open(result_path, "r:gz")
        tar.extractall(path=untar_path)
        tar.close()
    except FileNotFoundError:
        print("Tar.gz file path incorrect, please check your spelling.")
    # str_gt_path_2 = os.path.abspath("./SciTSR/ctdar_measurement_tool/annotations/trackB2/")
    # for roots,dirs,files in os.walk(str_gt_path_2):
    #     xml_root = roots
    #     xml_ids =  files
    import json
  
    res_lst = []
    score_lst = {}
    check = []
    p_total,r_total,f_total = 0,0,0
    for root, files, dirs in os.walk(untar_path):

        for name in dirs:
            print(name)
            # if name not in xml_ids: continue

            if name.split(".")[-1] == "xml":
                cur_filepath = osj(os.path.abspath(root), name)
                a = eval(track, cur_filepath)
                res_lst.append(a)

                correct_num,gt_num,pre_num = res_lst[-1].result[0].truePos,res_lst[-1].result[0].gtTotal,res_lst[-1].result[0].resTotal
                if(gt_num==0) : check.append(res_lst[-1].result[-1])
                else: 
                    if(correct_num == 0): 
                        p,r,f1 =0,0,0
                    else:  
                        p = correct_num / pre_num
                        r = correct_num / gt_num
                        f1 = 2 * p * r / (p + r)
                    if(p>1 ): 
                        p = 1
                        check.append(res_lst[-1].result[-1])#or f1 <0.1
                    # else:
                    if True:
                        p_total+=p
                        r_total+=r
                        f_total+=f1
                        score_lst[res_lst[-1].result[-1]]=[p,r,f1,correct_num,gt_num,pre_num]
                    
                # printing for debug
                # print(a.result[0].truePos)
                # print(res_lst[-1].result)
                print("Processing... {}".format(name))
              

            # break
    # print("DONE WITH FILE PROCESSING\n")
    # note: results are stored as list of each when iou at [0.6, 0.7, 0.8, 0.9, gt_filename]
    # gt number should be the same for all files
    gt_num = 0
    correct_six, res_six = 0, 0
    correct_seven, res_seven = 0, 0
    correct_eight, res_eight = 0, 0
    correct_nine, res_nine = 0, 0
    import json
    
    for each_file in res_lst:

        try:
            # print(each_file,'ssssssssssssssss')
            # print("{} {} {}".format(each_file.result[0].truePos, each_file.result[0].gtTotal, each_file.result[0].resTotal))
            gt_file_lst.remove(each_file.result[-1])
            if(each_file.result[-1] in check): continue
            correct_six += each_file.result[0].truePos
            gt_num += each_file.result[0].gtTotal
            res_six += each_file.result[0].resTotal
            # print("{} {} {}".format(each_file.result[0].truePos, each_file.result[0].gtTotal, each_file.result[0].resTotal))
            # result.append()
            # correct_seven += each_file.result[1].truePos
            # res_seven += each_file.result[1].resTotal

            # correct_eight += each_file.result[2].truePos
            # res_eight += each_file.result[2].resTotal

            # correct_nine += each_file.result[3].truePos
            # res_nine += each_file.result[3].resTotal

            # if (each_file.result[3].truePos / each_file.result[3].resTotal < 0.8):
            #     badcase_list.append(each_file.result[-1])
        except:
            print("Error occur in processing result list.")
            print(each_file.result[-1])
            break
 
    if len(gt_file_lst) > 0:
        print("\nWarning: missing result annotations for file: {}\n".format(gt_file_lst))
        gt_total = process_missing_files(gt_file_lst, gt_num)
    else:
        gt_total = gt_num

    print(gt_num,gt_total)
    try:
        print("Evaluation of {}".format(track.replace("-", "")))
        # iou @ 0.6
        print(correct_six,res_six,gt_total)
        p_six = correct_six / res_six
        r_six = correct_six / gt_total
        f1_six = 2 * p_six * r_six / (p_six + r_six)
        print("IOU @ 0.6 -\nprecision: {}\nrecall: {}\nf1: {}".format(p_six, r_six, f1_six))
        print("correct: {}, gt: {}, res: {}".format(correct_six, gt_total, res_six))
        length = len(score_lst)
        score_lst["average"] = [p_total/length,r_total/length,f_total/length,p_six,r_six,f1_six]    
        # # iou @ 0.7
        # p_seven = correct_seven / res_seven
        # r_seven = correct_seven / gt_total
        # f1_seven = 2 * p_seven * r_seven / (p_seven + r_seven)
        # print("IOU @ 0.7 -\nprecision: {}\nrecall: {}\nf1: {}".format(p_seven, r_seven, f1_seven))
        # print("correct: {}, gt: {}, res: {}\n".format(correct_seven, gt_total, res_seven))

        # # iou @ 0.8
        # p_eight = correct_eight / res_eight
        # r_eight = correct_eight / gt_total
        # f1_eight = 2 * p_eight * r_eight / (p_eight + r_eight)
        # print("IOU @ 0.8 -\nprecision: {}\nrecall: {}\nf1: {}".format(p_eight, r_eight, f1_eight))
        # print("correct: {}, gt: {}, res: {}".format(correct_eight, gt_total, res_eight))

        # # iou @ 0.9
        # p_nine = correct_nine / res_nine
        # r_nine = correct_nine / gt_total
        # f1_nine = 2 * p_nine * r_nine / (p_nine + r_nine)
        # print("IOU @ 0.9 -\nprecision: {}\nrecall: {}\nf1: {}".format(p_nine, r_nine, f1_nine))
        # print("correct: {}, gt: {}, res: {}".format(correct_nine, gt_total, res_nine))
        
        # print(badcase_list)
    except ZeroDivisionError:
        print("Error: zero devision error found, (possible that no adjacency relations are found), please check the file input.")
    t2 = time.time()
    print((t2-t1))



