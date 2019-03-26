# -*- coding: utf-8 -*-

"""
Some unit test for the evaluate_result_reg and evaluate_result_str of the eval 
class from eval.py

Usage: 
pytest test_eval.py
    or
python -mpytest test_eval.py

(you need to add pytest to your Python installation)

JL Meunier - March 2019
Naver Labs Europe
"""
import xml.dom.minidom

from eval import eval
from data_structure import ResultStructure


# ---  Utilities  -------------------------------------------------------
def OkErrMiss(o):
    """
    compute Ok, errors, missed from the ResultStructure object
    return a triple (ok, err, miss)
    """
    ok = o.truePos
    err = o.resTotal - ok
    miss = o.gtTotal - ok
    return ok, err, miss

def _regEval(gt_dom, result_dom, iou_value):
    """
    encapsulate the evaluate_result_reg to return ok, err, miss
    """
    o = eval.evaluate_result_reg(gt_dom, result_dom, iou_value)
    # print(o)
    return OkErrMiss(o)
    
def _rectangle(w, h, x0=0, y0=0):
    """
    create a rectangle with bottom left corner at 0,0 or at x,y if given
    
    the list of coordinates is closed (start==end)
    return the corresponding DOM
    """
    
    assert w > 0
    assert h > 0
    sXml = """<?xml version="1.0" encoding="UTF-8"?>
<document filename="table1.jpg">
    <table>
        <Coords points="%d,%d %d,%d %d,%d %d,%d  %d,%d"/>
    </table>
</document>
""" % (x0,y0 , x0+w,y0 , x0+w,y0+h , x0,y0+h, x0,y0)
    return xml.dom.minidom.parseString(sXml)

# -----------------------------------------------------------------------
def test_reg_simple():
    """
    a square compared to itself
    """
    for IoU in [0.1, 0.5, 0.9, 1.0]:
        assert _regEval( _rectangle(100, 100)
                       , _rectangle(100, 100)
                       , 0.9) == (1, 0, 0)
    
    GT = _rectangle(100, 100)
    assert _regEval( GT, _rectangle(89, 100)  # NOTE: why > instead of >= ?
                    , 0.9) == (0, 1, 1)
    assert _regEval( GT, _rectangle(90, 100)  # NOTE: why > instead of >= ?
                    , 0.9) == (0, 1, 1)
    assert _regEval( GT, _rectangle(91, 100)
                    , 0.9) == (1, 0, 0)
    
    assert _regEval( GT, _rectangle(100, 89)  # NOTE: why > instead of >= ?
                    , 0.9) == (0, 1, 1)
    assert _regEval( GT, _rectangle(100, 90)  # NOTE: why > instead of >= ?
                    , 0.9) == (0, 1, 1)
    assert _regEval( GT, _rectangle(100, 91)  
                    , 0.9) == (1, 0, 0)
                    
def test_reg_quarter():
    """
    a square compared to its quarter
    """
    GT = _rectangle(100, 100)
    assert _regEval( GT, _rectangle(50, 50)  
                    , 0.9) == (0, 1, 1)
    assert _regEval( GT, _rectangle(50, 50)  
                    , 0.24) == (1, 0, 0)
    assert _regEval( GT, _rectangle(50, 50)  
                    , 0.25) == (0, 1, 1)

#     assert _regEval( GT, _rectangle(100, 100, x0=-50, y0=-50)  
#                     , 0.9) == (0, 1, 1)
#     assert _regEval( GT, _rectangle(100, 100, x0=-50, y0=-50)  
#                     , 0.20) == (1, 0, 0)
#     assert _regEval( GT, _rectangle(100, 100, x0=-50, y0=-50)  
#                     , 0.25) == (0, 1, 1)

    GT = _rectangle(100, 100, x0=50, y0=50)
    assert _regEval( GT, _rectangle(100, 100)  
                    , 0.9) == (0, 1, 1)
    assert _regEval( GT, _rectangle(100, 100)  # BUG maybe??
                    , 0.20) == (1, 0, 0)
    assert _regEval( GT, _rectangle(100, 100)  # BUG maybe??
                    , 0.24) == (1, 0, 0)
    assert _regEval( GT, _rectangle(100, 100)  
                    , 0.25) == (0, 1, 1)
    GT = _rectangle(100, 100)
    
    

if __name__ == "__main__":
    # to test manually some code...
    test_reg()
    
    
    
    
    
    