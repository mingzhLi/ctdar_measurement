import os, glob, sys
import xml.dom.minidom
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
            self.evaluate_result_str(gt_dom, result_dom)

    @staticmethod
    # @param: gt_AR: Adj relations for the ground truth file
    # @param: result_AR: Adj relations for the result file
    def compare_AR(gt_AR, result_AR):
        retVal = 0
        dupGTAR = gt_AR.copy()
        dupResAR = result_AR.copy()

        # while len(dupGTAR) != 0:
        #     gt_ar = dupGTAR[0]
        for a, gt_ar in enumerate(dupGTAR, 0):
            for b, res_ar in enumerate(dupResAR, 0):
                if gt_ar.isEqual(res_ar):
                    # print("equal relation found")
                    retVal += 1
                    # dupGTAR.remove(gt_ar)
                    dupResAR.remove(res_ar)
                    break
            else:
                continue

        # print("el in dupRes:")
        # for el in dupResAR:
        #     print(el)
        # print('\nel in dupAR')
        # for el in dupGTAR:
        #     print(el)

        return retVal

    @staticmethod
    def evaluate_result_str(gt_dom, result_dom):
        # parse the tables in input elements
        gt_tables = []    # @param: gt_tables - Tables in Ground Truth File
        gt_root = gt_dom.documentElement
        gt_table_nodes = gt_root.getElementsByTagName("table")
        for tab in gt_table_nodes:
            gt_tables.append(Table(tab))
        # for aa in gt_tables:
        #     print(aa)
        #     print('\n')

        # parse the tables in result elements
        result_tables = []    # @param: result_tables - Tables in Result File
        result_root = result_dom.documentElement
        res_table_nodes = result_root.getElementsByTagName("table")
        for tab in res_table_nodes:
            result_tables.append(Table(tab))
        # for bb in result_tables:
        #     bb.find_aj_relations()
        #     print(bb)
        #     print('\n')

        # duplicate result table list
        remaining_tables = result_tables.copy()
        # for cc in remaining_tables:
        #     print(cc)
        #     print('\n')

        index = -1
        for gt_tab in gt_tables:
            index += 1
            # obtain list of tables on same page
            result_on_page = []
            for res_tab in remaining_tables:
                if res_tab.page == gt_tab.page:
                    result_on_page.append(res_tab)

            gtAR = gt_tab.find_aj_relations()
            # print(len(gtAR))
            resARs = []    # @param: resARs - list of ARs for result tables
            hashTable = {}    # init a dictionary for searching and removing according tables
            for result_table in result_on_page:
                resultAR = result_table.find_aj_relations()
                resARs.append(resultAR)
                hashTable.update({tuple(resultAR): result_table})    # use tuple of resultAR for hashing
            # for sth in resARs:
            #     print(len(sth))
            # print(resARs)

            # find best matching result table
            matchingResult = []    # save the matched table's AR list
            highestCorr = -1
            numHighest = 0
            for resultAr in resARs:    # @param: resultAr - current AR being compared
                correctDec = eval.compare_AR(gtAR, resultAr)
                if correctDec > highestCorr:
                    highestCorr = correctDec
                    numHighest = 1
                    matchingResult = resultAr
                elif correctDec == highestCorr:
                    numHighest += 1

            if len(matchingResult) != 0:
                resARs.remove(matchingResult)
                try:
                    # hashTable.pop(tuple(matchingResult))
                    remaining_tables.remove(hashTable.pop(tuple(matchingResult)))
                    # print("remaing: {}".format(len(remaining_tables)))
                except KeyError:
                    print("Table(key) not found.")

            # if (debug):

            # output result
            print("\nTable {} :".format(index+1))

            if len(matchingResult) != 0:
                corrDect = eval.compare_AR(gtAR, matchingResult)
                print("GT size: {}  corrDet: {}  detected: {}".format(len(gtAR), corrDect, len(matchingResult)))
                prec = corrDect / len(matchingResult)
                print("Precision: {}".format(prec))
                rec = corrDect / len(gtAR)
                print("Recall: {}".format(rec))
            else:
                print("No matching result found.")

            if len(remaining_tables) > 0:
                print("False positive table found.")
                # for el in remaining_tables:
                #     print(el)


if __name__ == "__main__":
    # resultFile = "./test2-result.xml"
    # result = "test2"
    eval("us-001")
