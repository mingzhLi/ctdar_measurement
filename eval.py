import os, glob, sys
import xml.dom.minidom
# from functools import cmp_to_key
from itertools import groupby
from data_structure import *
from os.path import join as osj


class eval:

    STR = "-str"
    REG = "-reg"
    DEFAULT_ENCODING = "UTF-8"
    # reg_gt_path = "./annotations/trackA/"
    # str_gt_path = "./annotations/trackB/"
    reg_gt_path = os.path.abspath("./annotations/trackA/")
    str_gt_path = os.path.abspath("./annotations/trackB/")

    def __init__(self, track, res_path):
        self.return_result = None
        self.reg = False
        self.str = False

        if track == "-trackA":
            self.reg = True
        elif track == "-trackB1":
            self.str = True
        elif track == "-trackB2":
            self.str = True
        # elif track == "-trackB":
        #     self.str = True

        self.resultFile = res_path
        self.inPrefix = os.path.split(res_path)[-1].split("-")[0]
        # print(inPrefix)

        if self.str:
            self.GTFile = osj(self.str_gt_path, self.inPrefix + "-str.xml")
        elif self.reg:
            self.GTFile = osj(self.reg_gt_path, self.inPrefix + "-reg.xml")
        else:
            print("Not a valid track, please check your spelling.")

        # print("Using GTFile    : " + self.GTFile)
        # print("Using resultFile: " + self.resultFile)
        self.gene_ret_lst()

    @property
    def result(self):
        return self.return_result

    def gene_ret_lst(self):
        ret_lst = []
        for iou in [0.6, 0.7, 0.8, 0.9]:
            ret_lst.append(self.compute_retVal(iou))
        if self.str:
            ret_lst.append(self.inPrefix + "-str.xml")
        elif self.reg:
            ret_lst.append(self.inPrefix + "-reg.xml")
        print("done processing {}".format(self.resultFile))
        self.return_result = ret_lst

    def compute_retVal(self, iou):
        gt_dom = xml.dom.minidom.parse(self.GTFile)
        result_dom = xml.dom.minidom.parse(self.resultFile)
        if self.reg:
            ret = self.evaluate_result_reg(gt_dom, result_dom, iou)
            return ret
        if self.str:
            ret = self.evaluate_result_str(gt_dom, result_dom, iou)
            return ret

    # @staticmethod
    # # @param: gt_AR: Adj relations list for the ground truth file
    # # @param: result_AR: Adj relations list for the result file
    # def compare_AR(gt_AR, result_AR):
    #     retVal = 0
    #     dupGTAR = gt_AR.copy()
    #     dupResAR = result_AR.copy()
    #
    #     # while len(dupGTAR) != 0:
    #     #     gt_ar = dupGTAR[0]
    #     for a, gt_ar in enumerate(dupGTAR, 0):
    #         for b, res_ar in enumerate(dupResAR, 0):
    #             if gt_ar.isEqual(res_ar):
    #                 # print("equal relation found")
    #                 retVal += 1
    #                 # dupGTAR.remove(gt_ar)
    #                 dupResAR.remove(res_ar)
    #                 break
    #         else:
    #             continue
    #
    #     # print("el in dupRes:")
    #     # for el in dupResAR:
    #     #     print(el)
    #     # print('\nel in dupAR')
    #     # for el in dupGTAR:
    #     #     print(el)
    #
    #     return retVal

    @staticmethod
    def evaluate_result_reg(gt_dom, result_dom, iou_value):
        # parse the tables in input elements
        gt_tables = []  # @param: gt_tables - Tables in Ground Truth File
        gt_root = gt_dom.documentElement
        gt_table_nodes = gt_root.getElementsByTagName("table")
        for tab in gt_table_nodes:
            gt_tables.append(Table(tab))

        # parse the tables in result elements
        result_tables = []  # @param: result_tables - Tables in Result File
        result_root = result_dom.documentElement
        res_table_nodes = result_root.getElementsByTagName("table")
        for tab in res_table_nodes:
            result_tables.append(Table(tab))

        # duplicate result table list
        remaining_tables = result_tables.copy()

        # map the tables in gt and result file
        table_matches = []  # @param: table_matches - list of mapping of tables in gt and res file, in order (gt, res)
        for gtt in gt_tables:
            for rest in remaining_tables:
                if gtt.compute_table_iou(rest) > iou_value:
                    table_matches.append((gtt, rest))
                    remaining_tables.remove(rest)
        # print("\nfound matched table pairs: {}".format(len(table_matches)))

        retVal = ResultStructure(truePos=len(table_matches), gtTotal=len(gt_tables), resTotal=len(result_tables))
        return retVal

    @staticmethod
    def evaluate_result_str(gt_dom, result_dom, iou_value):
        # parse the tables in input elements
        gt_tables = []    # @param: gt_tables - Tables in Ground Truth File
        gt_root = gt_dom.documentElement
        gt_table_nodes = gt_root.getElementsByTagName("table")
        for tab in gt_table_nodes:
            gt_tables.append(Table(tab))

        # parse the tables in result elements
        result_tables = []    # @param: result_tables - Tables in Result File
        result_root = result_dom.documentElement
        res_table_nodes = result_root.getElementsByTagName("table")
        for tab in res_table_nodes:
            result_tables.append(Table(tab))

        # duplicate result table list
        remaining_tables = result_tables.copy()

        # map the tables in gt and result file
        table_matches = []   # @param: table_matches - list of mapping of tables in gt and res file, in order (gt, res)
        for gtt in gt_tables:
            for rest in remaining_tables:
                # note: for structural analysis, use 0.8 for table mapping
                if gtt.compute_table_iou(rest) > 0.8:
                    table_matches.append((gtt, rest))
                    remaining_tables.remove(rest)
        # print("\nfound matched table pairs: {}".format(len(table_matches)))
        # print("False positive tables: {}\n".format(remaining_tables))

        total_gt_relation, total_res_relation, total_correct_relation = 0, 0, 0
        for el in table_matches:
            gt_table = el[0]
            ress_table = el[1]

            # set up the cell mapping for matching tables
            cell_mapping = gt_table.find_cell_mapping(ress_table, iou_value)

            # set up the adj relations, convert the one for result table to a dictionary for faster searching
            gt_AR = gt_table.find_adj_relations()
            total_gt_relation += len(gt_AR)
            res_AR = ress_table.find_adj_relations()
            total_res_relation += len(res_AR)
            res_AR.sort(key=lambda x: [x.fromText.start_row, x.fromText.start_col])
            res_ar_dict = {}
            for key, group in groupby(res_AR, key=lambda x: x.fromText):
                # print(key)
                res_ar_dict[key] = tuple(group)
            # print(res_ar_dict)
            # print("", gt_AR, "\n", res_AR, "\n", cell_mapping, "\n")

            correct_dect = 0
            # count the matched adj relations
            for ar in gt_AR:
                target_cell_from = cell_mapping.get(ar.fromText)
                target_cell_to = cell_mapping.get(ar.toText)
                direction = ar.direction    # DIR_HORIZ = 1 / DIR_VERT = 2
                if (target_cell_from is None) or (target_cell_to is None):
                    continue
                for target_relation in res_ar_dict.get(target_cell_from):
                    if target_relation.toText == target_cell_to and target_relation.direction == direction:
                        correct_dect += 1
                        break
            # print("found correct detection: {} for table {}".format(correct_dect, gt_table))
            total_correct_relation += correct_dect

        # print("total gt, res, corrrct: {}, {}, {}".format(total_gt_relation, total_res_relation, total_correct_relation))
        retVal = ResultStructure(truePos=total_correct_relation, gtTotal=total_gt_relation, resTotal=total_res_relation)
        return retVal

        # ==========================================================================================================
        # index = -1
        # for gt_tab in gt_tables:
        #     index += 1
        #     # # obtain list of tables on same page
        #     # result_on_page = []
        #     # for res_tab in remaining_tables:
        #     #     if res_tab.page == gt_tab.page:
        #     #         result_on_page.append(res_tab)
        #
        #     gtAR = gt_tab.find_adj_relations()
        #     # print(len(gtAR))
        #     resARs = []    # @param: resARs - list of ARs for result tables
        #     hashTable = {}    # init a dictionary for searching and removing according tables
        #     for result_table in remaining_tables:
        #         resultAR = result_table.find_adj_relations()
        #         resARs.append(resultAR)
        #         hashTable.update({tuple(resultAR): result_table})    # use tuple of resultAR for hashing
        #     # for sth in resARs:
        #     #     print(len(sth))
        #     # print(resARs)
        #
        #
        #     # find best matching result table
        #     matchingResult = []    # save the matched table's AR list
        #     highestCorr = -1
        #     numHighest = 0
        #     for resultAr in resARs:    # @param: resultAr - current AR being compared
        #         correctDec = eval.compare_AR(gtAR, resultAr)
        #         if correctDec > highestCorr:
        #             highestCorr = correctDec
        #             numHighest = 1
        #             matchingResult = resultAr
        #         elif correctDec == highestCorr:
        #             numHighest += 1
        #
        #     if len(matchingResult) != 0:
        #         resARs.remove(matchingResult)
        #         try:
        #             # hashTable.pop(tuple(matchingResult))
        #             remaining_tables.remove(hashTable.pop(tuple(matchingResult)))
        #             # print("remaing: {}".format(len(remaining_tables)))
        #         except KeyError:
        #             print("Table(key) not found.")
        #
        #     # output result
        #     print("\nTable {} :".format(index+1))
        #
        #     if len(matchingResult) != 0:
        #         corrDect = eval.compare_AR(gtAR, matchingResult)
        #         print("GT size: {}  corrDet: {}  detected: {}".format(len(gtAR), corrDect, len(matchingResult)))
        #         prec = corrDect / len(matchingResult)
        #         print("Precision: {}".format(prec))
        #         rec = corrDect / len(gtAR)
        #         print("Recall: {}".format(rec))
        #     else:
        #         print("No matching result found.")
        #
        #     if len(remaining_tables) > 0:
        #         print("False positive table found.")


# if __name__ == "__main__":
#     eval("-trackB1", "/Users/fang/PycharmProjects/performanceMeasure/annotations/test_files/test3-str-result.xml")
