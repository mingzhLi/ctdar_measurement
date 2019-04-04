"""
Evaluation of single result file.

Yu Fang - March 2019
"""

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

        if self.str:
            self.GTFile = osj(self.str_gt_path, self.inPrefix + "-str.xml")
        elif self.reg:
            self.GTFile = osj(self.reg_gt_path, self.inPrefix + "-reg.xml")
        else:
            print("Not a valid track, please check your spelling.")

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
    
    @staticmethod
    def get_table_list(dom):
        """
        return a list of Table objects corresponding to the table element of the DOM.
        """
        return [Table(_nd) for _nd in dom.documentElement.getElementsByTagName("table")]
        

    @staticmethod
    def evaluate_result_reg(gt_dom, result_dom, iou_value):
        # parse the tables in input elements
        gt_tables     = eval.get_table_list(gt_dom)
        result_tables = eval.get_table_list(result_dom)

        # duplicate result table list
        remaining_tables = result_tables.copy()

        # map the tables in gt and result file
        table_matches = []  # @param: table_matches - list of mapping of tables in gt and res file, in order (gt, res)
        for gtt in gt_tables:
            for rest in remaining_tables:
                if gtt.compute_table_iou(rest) >= iou_value:
                    remaining_tables.remove(rest)
                    table_matches.append((gtt, rest))
                    break

        assert len(table_matches) <= len(gt_tables)
        assert len(table_matches) <= len(result_tables)
        
        retVal = ResultStructure(truePos=len(table_matches), gtTotal=len(gt_tables), resTotal=len(result_tables))
        return retVal

    @staticmethod
    def evaluate_result_str(gt_dom, result_dom, iou_value, table_iou_value=0.8):
        # parse the tables in input elements
        gt_tables     = eval.get_table_list(gt_dom)
        result_tables = eval.get_table_list(result_dom)

        # duplicate result table list
        remaining_tables = result_tables.copy()

        # map the tables in gt and result file
        table_matches = []   # @param: table_matches - list of mapping of tables in gt and res file, in order (gt, res)
        for gtt in gt_tables:
            for rest in remaining_tables:
                # note: for structural analysis, use 0.8 for table mapping
                if gtt.compute_table_iou(rest) >= table_iou_value:
                    table_matches.append((gtt, rest))
                    remaining_tables.remove(rest)   # unsafe... should be ok with the break below
                    break

        total_gt_relation, total_res_relation, total_correct_relation = 0, 0, 0
        for gt_table, ress_table in table_matches:

            # set up the cell mapping for matching tables
            cell_mapping = gt_table.find_cell_mapping(ress_table, iou_value)
            # set up the adj relations, convert the one for result table to a dictionary for faster searching
            gt_AR = gt_table.find_adj_relations()
            total_gt_relation += len(gt_AR)
            
            res_AR = ress_table.find_adj_relations()
            total_res_relation += len(res_AR)
            
            if False:   # for DEBUG 
                Table.printCellMapping(cell_mapping)
                Table.printAdjacencyRelationList(gt_AR, "GT")
                Table.printAdjacencyRelationList(res_AR, "run")
            
            # Now map GT adjacency relations to result
            lMappedAR = []
            for ar in gt_AR:
                try:
                    resFromCell = cell_mapping[ar.fromText]
                    resToCell   = cell_mapping[ar.toText]
                    #make a mapped adjacency relation
                    lMappedAR.append(AdjRelation(resFromCell, resToCell, ar.direction))
                except:
                    # no mapping is possible
                    pass
            
            # compare two list of adjacency relation
            correct_dect = 0
            for ar1 in res_AR:
                for ar2 in lMappedAR:
                    if ar1.isEqual(ar2):
                        correct_dect += 1
                        break

            total_correct_relation += correct_dect

        retVal = ResultStructure(truePos=total_correct_relation, gtTotal=total_gt_relation, resTotal=total_res_relation)
        return retVal
        