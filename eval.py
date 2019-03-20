import os, glob, sys
import xml.dom.minidom
import numpy as np
import shapely
# from functools import cmp_to_key
from itertools import groupby
from data_structure import *
from os.path import join as osj


class eval:

    STR = "-str"
    REG = "-reg"
    DEFAULT_ENCODING = "UTF-8"
    NO_PAGE = "-nopage"
    DEBUG = "-debug"
    COMPARE = "-compare"
    IGNORE_CHARS = "-ignorechars"
    STR_IGNORE = "-strignore"

    def __init__(self, *args):
        inPrefix = None
        resultFile = None
        GTFile = None
        PDFFile = None
        rulingLines = True
        processSpaces = False
        compare = False
        currentArgumentIndex = 0
        password = ""
        encoding = self.DEFAULT_ENCODING
        startPage = 1
        endPage = sys.maxsize
        toConsole = False
        str = False
        reg = False
        debug = False
        pageCheck = True
        normRule = 0

        for arg in args:
            if arg == self.STR:
                str = True
            elif arg == self.REG:
                reg = True
            elif arg == self.DEBUG:
                debug = True
            elif arg == self.COMPARE:
                compare = True
            elif arg == self.NO_PAGE:
                pageCheck = False
            elif arg == self.IGNORE_CHARS:
                normRule = 1
            elif arg == self.STR_IGNORE:
                str = True
                normRule = 1
            else:
                if inPrefix is None:
                    inPrefix = arg
                    # print(format("inPrefix set, %s\n" % arg))
                elif resultFile is None:
                    resultFile = arg
                else:
                    PDFFile = arg

        if inPrefix is None:
            print("invalid arguments entered")
            return
            # self.usage()

        if resultFile is None:
            PDFFile = inPrefix + ".pdf"
            if str:
                resultFile = inPrefix + "-str-result.xml"
                GTFile = inPrefix + "-str.xml"
            elif reg:
                resultFile = inPrefix + "-reg-result.xml"
                GTFile = inPrefix + "-reg.xml"
            else:
                resultFile = inPrefix + "-result.xml"
                GTFile = inPrefix + ".xml"
        else:
            if str:
                GTFile = inPrefix + "-str.xml"
            elif reg:
                GTFile = inPrefix + "-reg.xml"
            else:
                GTFile = inPrefix + ".xml"

            if PDFFile is None:
                PDFFile = inPrefix + ".pdf"

        print("Using     GTFile: " + GTFile)
        print("Using resultFile: " + resultFile)
        print("Using    PDFFile: " + PDFFile)

        final_gt_file = "./annotations/" + GTFile
        gt_dom = xml.dom.minidom.parse(final_gt_file)
        result_dom = xml.dom.minidom.parse(resultFile)
        if not reg:
            # TODO: pass-in iou value
            self.evaluate_result_str(gt_dom, result_dom, 0.6)

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

    # TODO: complete F1 calculation
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
        print("\nfound matched table pairs: {}".format(len(table_matches)))
        print("remaining_tables: {}\n".format(remaining_tables))

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
                if gtt.compute_table_iou(rest) > iou_value:
                    table_matches.append((gtt, rest))
                    remaining_tables.remove(rest)
        print("\nfound matched table pairs: {}".format(len(table_matches)))
        print("remaining_tables: {}\n".format(remaining_tables))

        for el in table_matches:
            correct_dect = 0
            gt_table = el[0]
            ress_table = el[1]

            # set up the cell mapping for matching tables
            cell_mapping = gt_table.find_cell_mapping(ress_table, iou_value)

            # set up the adj relations, convert the one for result table to a dictionary
            gt_AR = gt_table.find_adj_relations()
            res_AR = ress_table.find_adj_relations()
            res_AR.sort(key=lambda x: [x.fromText.start_row, x.fromText.start_col])
            res_ar_dict = {}
            for key, group in groupby(res_AR, key=lambda x: x.fromText):
                # print(key)
                res_ar_dict[key] = tuple(group)
            # print(res_ar_dict)
            # print("", gt_AR, "\n", res_AR, "\n", cell_mapping, "\n")

            # count the matched adj relations
            for ar in gt_AR:
                target_cell_from = cell_mapping.get(ar.fromText)
                target_cell_to = cell_mapping.get(ar.toText)
                direction = ar.direction    # DIR_HORIZ = 1 / DIR_VERT = 2

                for target_relation in res_ar_dict.get(target_cell_from):
                    if target_relation.toText == target_cell_to and target_relation.direction == direction:
                        correct_dect += 1
                        break
            print(correct_dect)

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


if __name__ == "__main__":
    # resultFile = "./test2-result.xml"
    # result = "test2"
    eval("test1")
