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
    
def _strEval(gt_dom, result_dom, iou_value):
    """
    encapsulate the evaluate_result_str to return ok, err, miss
    """
    o = eval.evaluate_result_str(gt_dom, result_dom, iou_value)
    # print(o)
    return OkErrMiss(o)
    
def _rectangle(w, h, x0=0, y0=0, bClosed=True, sXmlCells=None):
    """
    create a rectangle with bottom left corner at 0,0 or at x,y if given
    
    the list of coordinates is closed (start==end) if bClosed is True
    return the corresponding DOM
    """
    
    assert w > 0
    assert h > 0
        
    sXml = """<?xml version="1.0" encoding="UTF-8"?>
<document filename="table1.jpg">
    %s
</document>
""" % _table_xml(x0, y0, w, h, bClosed, sXmlCells=sXmlCells)
    return xml.dom.minidom.parseString(sXml)

def _multi_rectangle(lxywh):
    """
    return a DOM containing multiple tables
    """
    sXmlTable = ""
    for x,y,w,h in lxywh:
        assert w > 0 and h > 0
        sXmlTable += "\n%s" % _table_xml(x, y, w, h, False)
        
    sXml = """<?xml version="1.0" encoding="UTF-8"?>
<document filename="table1.jpg">
    %s
</document>
""" % sXmlTable

    return xml.dom.minidom.parseString(sXml)    

def _table_xml(x, y, w, h, bClosed=True, sXmlCells=None):
    """
    XML Table element as a string
    """
    if bClosed:
        #close the list of coordinates
        sPoints = "%d,%d %d,%d %d,%d %d,%d %d,%d" % (x,y , x+w,y , x+w,y+h , x,y+h , x,y)
    else:
        sPoints = "%d,%d %d,%d %d,%d %d,%d"       % (x,y , x+w,y , x+w,y+h , x,y+h)
    
    if sXmlCells is None:
        sXmlCells = """<cell start-row='0' start-col='0' end-row='1' end-col='2'>
<Coords points="180,160 177,456 614,456 615,163"/>
</cell>"""

    sXml = """
    <table>
        <Coords points="%s"/>
        %s
    </table>
    """ % (sPoints, sXmlCells)
    return sXml


def _cell_xml(sr, sc, er, ec, sPointXml
              , bFilled=False    # do not put some text by default
              , iShiftRow=0, iShiftCol=0 # shift the whole table
              , bRotate=False   # swap Xs and Ys  (90° rotation)
              ):
    """
    Generate the serialized XML for one cell, possibly shifted, column- or row-wise
    
    """
    if bFilled:
        sContent = "<content><xx>%d_%d_%d_%d_%s</xx></content>"%(sr, sc, er, ec, sPointXml)
    else:
        sContent = ""
    
    if bRotate:
        lt2 = [(sPair.split(',')[0], sPair.split(',')[1]) for sPair in sPointXml.strip().split()]
        sRotatedPointXml = " ".join("%s,%s"%(y, x) for x,y in lt2)
        t6 = (sc+iShiftCol, sr+iShiftRow, ec+iShiftCol, er+iShiftRow, sRotatedPointXml, sContent)
    else:
        t6 = (sr+iShiftRow, sc+iShiftCol, er+iShiftRow, ec+iShiftCol, sPointXml, sContent)
        
    return """<cell start-row='%d' start-col='%d' end-row='%d' end-col='%d'>
<Coords points="%s"/>
%s
</cell>""" % t6

# -----------------------------------------------------------------------
def test_reg_simple():
    """
    a square compared to itself
    """
    for bClosedCoords in [True, False]:
        for IoU in [0.1, 0.5, 0.9, 1.0]:
            assert _regEval( _rectangle(100, 100, bClosed=bClosedCoords)
                           , _rectangle(100, 100)
                           , 0.9) == (1, 0, 0)
        
        GT = _rectangle(100, 100, bClosed=bClosedCoords)
        assert _regEval( GT, _rectangle(89, 100)
                        , 0.89) == (1, 0, 0)
        assert _regEval( GT, _rectangle(89, 100)
                        , 0.9) == (0, 1, 1)
        assert _regEval( GT, _rectangle(90, 100)
                        , 0.9) == (1, 0, 0)
        assert _regEval( GT, _rectangle(91, 100)
                        , 0.9) == (1, 0, 0)
        
        assert _regEval( GT, _rectangle(100, 89)
                        , 0.9) == (0, 1, 1)
        assert _regEval( GT, _rectangle(100, 90)
                        , 0.9) == (1, 0, 0)
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
                    , 0.25) == (1, 0, 0)


    GT = _rectangle(100, 100, x0=50, y0=50)
    assert _regEval( GT, _rectangle(100, 100)  
                    , 0.9) == (0, 1, 1)
    iou = 50*50 / (7 * 50*50)
    print("expected=", iou)
    assert _regEval( GT, _rectangle(100, 100) 
                    , iou + 0.01) == (0, 1, 1)
    assert _regEval( GT, _rectangle(100, 100) 
                    , iou - 0.01) == (1, 0, 0)
   
    
def test_multi_table():
    """
    what if we have several tables on a page?
    """
    
    GT = _multi_rectangle([(0 ,0 ,100, 100)
                           , (200, 200, 100, 300)])
    assert _regEval( GT, GT  
                    , 1.0) == (2, 0, 0)     
    assert _regEval( GT, GT  
                    , 0.1) == (2, 0, 0)   
    
    # one missing table
    RUN =_multi_rectangle([(0 ,0 ,100, 100)
                           ])
    assert _regEval( GT, RUN  
                    , 1.0) == (1, 0, 1)     
    assert _regEval( GT, RUN  
                    , 0.1) == (1, 0, 1)   
    
    # one extra table
    RUN =_multi_rectangle([(0 ,0 ,100, 100)
                           , (200, 200, 100, 300)
                           , (1000 ,1000 ,1100, 1100)
                           ])
    assert _regEval( GT, RUN  
                    , 1.0) == (2, 1, 0)     
    assert _regEval( GT, RUN  
                    , 0.1) == (2, 1, 0)   
    
    # messy situation with one predicted table in middle overlapping the two GT tables
    # but the 2nd one is "more" overlapped
    RUN =_multi_rectangle([(50 , 50 , 300, 350)
                           ])
    res = _regEval( GT, RUN, 1.0)
    assert res == (0, 1, 2), res
    res = _regEval( GT, RUN, 0.01)
    assert res == (1, 0, 1), res
    
    iou1 = 50*50 / (100*100+300*350-50*50)  # overlap with 1st GT table 
    iou2 = 200*100 / (100*300+300*350-200*100)  # overlap with 2nd GT table 

    # 1st and middle on one in RUN
    RUN =_multi_rectangle([(0 ,0 ,100, 100)
                           , (50 , 50 , 300, 350)
                           ])
    res = _regEval( GT, RUN, 1.0)
    assert res == (1, 1, 1), res
    res = _regEval( GT, RUN, 0.01)
    assert res == (2, 0, 0), res
    res = _regEval( GT, RUN, iou2-0.01)
    assert res == (2, 0, 0), res
    res = _regEval( GT, RUN, iou2+0.01)
    assert res == (1, 1, 1), res

    
    # 2nd and middle on one in RUN
    RUN =_multi_rectangle([(200, 200, 100, 300)
                           , (50 , 50 , 300, 350)
                           ])
    res = _regEval( GT, RUN, 1.0)
    assert res == (1, 1, 1), res
    res = _regEval( GT, RUN, 0.01)
    assert res == (2, 0, 0), res
    res = _regEval( GT, RUN, iou2-0.01)
    assert res == (1, 1, 1), res
    res = _regEval( GT, RUN, iou2+0.01)
    assert res == (1, 1, 1), res  
    # middle one should match the 1st one  
    res = _regEval( GT, RUN, iou1-0.01)
    assert res == (2, 0, 0), res
    res = _regEval( GT, RUN, iou1+0.01)
    assert res == (1, 1, 1), res

    # 1st and 2nd and middle one
    RUN =_multi_rectangle([(0 ,0 ,100, 100)
                           , (200, 200, 100, 300)
                           , (50 , 50 , 300, 350)
                           ])
    res = _regEval( GT, RUN, 1.0)
    assert res == (2, 1, 0), res
    res = _regEval( GT, RUN, 0.01)
    assert res == (2, 1, 0), res
    res = _regEval( GT, RUN, iou2-0.01)
    assert res == (2, 1, 0), res
    res = _regEval( GT, RUN, iou2+0.01)
    assert res == (2, 1, 0), res  
    # middle one should match the 1st one  
    res = _regEval( GT, RUN, iou1-0.01)
    assert res == (2, 1, 0), res
    res = _regEval( GT, RUN, iou1+0.01)
    assert res == (2, 1, 0), res

# ----------------------------------------------------------------------
# table recognition
def test_table_recognition_obvious():
    
    sXmlCells = " ".join([  _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70")
                         , _cell_xml(0,1,0,1,"60,60 70,60 70,70 60,70")
                         ])
    GT  = _rectangle(100, 100, sXmlCells=sXmlCells)
    res = _strEval(GT, GT, 0.85)
    assert res == (1, 0, 0), res

    
def test_table_recognition_simple_horizontal():
    # in the run, we might have no content in the cells
    sXmlCells = " ".join([  _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70")
                         , _cell_xml(0,1,0,1,"60,60 70,60 70,70 60,70")
                         ])
    GT  = _rectangle(100, 100, sXmlCells=sXmlCells)

    for bCellContent in [True, False]:
        for iShiftRow in range(0, 3):
            for iShiftCol in range(0, 3):
                sXmlRunCells = " ".join([ _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70", bCellContent, iShiftRow=iShiftRow, iShiftCol=iShiftCol)
                                        , _cell_xml(0,1,0,1,"60,60 70,60 70,70 60,70", bCellContent, iShiftRow=iShiftRow, iShiftCol=iShiftCol)
                                     ])
                RUN = _rectangle(90 , 100, sXmlCells=sXmlRunCells) # width=90
                res = _strEval(GT, RUN, 0.95)
                assert res == (1, 0, 0), (bCellContent, res)    # 0.95 is for cells not table!
                res = _strEval(GT, RUN, 0.85)
                assert res == (1, 0, 0), (bCellContent, res)
            
                # 2nd cell slightly badly positionated
                sXmlRunCells = " ".join([ _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70", bCellContent, iShiftRow=iShiftRow, iShiftCol=iShiftCol)
                                        , _cell_xml(0,1,0,1,"64,60 70,60 70,70 64,70", bCellContent, iShiftRow=iShiftRow, iShiftCol=iShiftCol)
                                     ])
                RUN = _rectangle(90 , 100, sXmlCells=sXmlRunCells) # width=90
                res = _strEval(GT, RUN, 0.95)
                assert res == (0, 1, 1), (bCellContent, res)    # 0.95 is for cells not table!
                res = _strEval(GT, RUN, 0.50)
                assert res == (1, 0, 0), (bCellContent, res)
         
                # one big cell overlapping both
                sXmlRunCells = " ".join([ _cell_xml(0,0,0,0,"10,60 70,60 70,70 10,70", bCellContent, iShiftRow=iShiftRow, iShiftCol=iShiftCol)
                                     ])
                RUN = _rectangle(90 , 100, sXmlCells=sXmlRunCells) # width=90
                res = _strEval(GT, RUN, 0.85)
                assert res == (0, 0, 1), (bCellContent, res)
        
                # one big cell overlapping both +  one in 0,1 but far
                sXmlRunCells = " ".join([ _cell_xml(0,0,0,0,"10,60 70,60 70,70 10,70", bCellContent, iShiftRow=iShiftRow, iShiftCol=iShiftCol)
                                        , _cell_xml(0,1,0,1,"260,60 270,60 270,70 260,70", bCellContent, iShiftRow=iShiftRow, iShiftCol=iShiftCol)
                                     ])
                RUN = _rectangle(90 , 100, sXmlCells=sXmlRunCells) # width=90
                res = _strEval(GT, RUN, 0.85)
                assert res == (0, 1, 1), (bCellContent, res)

def test_table_recognition_simple_vertical():

        sXmlCells    = " ".join([ _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70")
                                , _cell_xml(1,0,1,0,"10,70 20,70 20,80 10,90")
                         ])
        GT  = _rectangle(100, 100, sXmlCells=sXmlCells)

        # no adjacency
        sXmlRunCells = " ".join([ _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70")
                                , _cell_xml(1,1,1,1,"10,70 20,70 20,80 10,90")
                             ])
        RUN = _rectangle(90 , 100, sXmlCells=sXmlRunCells) # width=90
        res = _strEval(GT, RUN, 0.50)
        assert res == (0, 0, 1), res  
         
        # 2nd cells side-by-side vertically
        sXmlRunCells = " ".join([ _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70")
                                , _cell_xml(1,0,1,0,"10,70 20,70 20,80 10,90")
                             ])
        RUN = _rectangle(90 , 100, sXmlCells=sXmlRunCells) # width=90
        res = _strEval(GT, RUN, 0.95)
        assert res == (1, 0, 0), res    # 0.95 is for cells not table!
        res = _strEval(GT, RUN, 0.51)
        assert res == (1, 0, 0), res
        
        # 2nd cells side-by-side vertically - changed order in XML
        sXmlRunCells = " ".join([ 
                                  _cell_xml(1,0,1,0,"10,70 20,70 20,80 10,90")
                                , _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70")
                             ])
        RUN = _rectangle(90 , 100, sXmlCells=sXmlRunCells) # width=90
        res = _strEval(GT, RUN, 0.95)
        assert res == (1, 0, 0), res    # 0.95 is for cells not table!
        res = _strEval(GT, RUN, 0.51)
        assert res == (1, 0, 0), res

        # 1st cell halved
        sXmlRunCells = " ".join([ _cell_xml(0,0,0,0,"10,60 20,60 20,66 10,66")
                                , _cell_xml(1,0,1,0,"10,70 20,70 20,80 10,90")
                             ])
        RUN = _rectangle(90 , 100, sXmlCells=sXmlRunCells) # width=90
        res = _strEval(GT, RUN, 0.95)
        assert res == (0, 1, 1), res    # 0.95 is for cells not table!
        res = _strEval(GT, RUN, 0.51)
        assert res == (1, 0, 0), res

        # 1st cell halved and placed in 1,1
        sXmlRunCells = " ".join([ _cell_xml(0,0,0,0,"10,60 20,60 20,66 10,66")
                                , _cell_xml(1,1,1,1,"10,70 20,70 20,80 10,90")
                             ])
        RUN = _rectangle(90 , 100, sXmlCells=sXmlRunCells) # width=90
        res = _strEval(GT, RUN, 0.95)
        assert res == (0, 0, 1), res    # 0.95 is for cells not table!
        res = _strEval(GT, RUN, 0.51)
        assert res == (0, 0, 1), res

        # 2nd cell placed in 0,0 (INCONSISTENT prediction)
        sXmlRunCells = " ".join([ _cell_xml(0,0,0,0,"10,60 20,60 20,66 10,66")
                                , _cell_xml(0,0,0,0,"10,70 20,70 20,80 10,90")
                             ])
        RUN = _rectangle(90 , 100, sXmlCells=sXmlRunCells) # width=90
        res = _strEval(GT, RUN, 0.95)
        assert res == (0, 0, 1), res    # 0.95 is for cells not table!
        res = _strEval(GT, RUN, 0.51)
        assert res == (0, 0, 1), res

        # 2nd cell extended to cover part of the top of 1st cell
        sXmlRunCells = " ".join([ _cell_xml(0,0,0,0,"10,60 20,60 20,66 10,66")
                                , _cell_xml(1,0,1,0,"10,66 20,66 20,80 10,90")
                             ])
        RUN = _rectangle(90 , 100, sXmlCells=sXmlRunCells) # width=90
        res = _strEval(GT, RUN, 0.95)
        assert res == (0, 1, 1), res    # 0.95 is for cells not table!
        res = _strEval(GT, RUN, 0.51)
        assert res == (1, 0, 0), res

def test_table_recognition_simple_horizontal_vertical():
    
        # some row and col displacement of the precited table...
        for iRgt, iCgt in [(i,j) for i in range(6) for j in range(6)]:
    
            #    # #
            #    #
            sXmlCells = " ".join([  _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70", iShiftRow=iRgt, iShiftCol=iCgt)
                                  , _cell_xml(0,1,0,1,"60,60 70,60 70,70 60,70", iShiftRow=iRgt, iShiftCol=iCgt)
                                  , _cell_xml(1,0,1,0,"10,70 20,70 20,80 10,90", iShiftRow=iRgt, iShiftCol=iCgt)
                             ])
            GT  = _rectangle(100, 100 , sXmlCells=sXmlCells)
    
            # RUN same as GT
            RUN = _rectangle(100 , 100, sXmlCells=sXmlCells)
            res = _strEval(GT, RUN, 0.95)
            assert res == (2, 0, 0), res
            
            # some row and col displacement of the precited table...
            for iR, iC in [(i,j) for i in range(3) for j in range(3)]:
                # Now some cells get reduced by half
                sXmlCells = " ".join([  _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70", iShiftRow=iR, iShiftCol=iC)
                              , _cell_xml(0,1,0,1,"60,60 70,60 70,70 60,70", iShiftRow=iR, iShiftCol=iC)
                              , _cell_xml(1,0,1,0,"10,70 20,70 20,76 10,86", iShiftRow=iR, iShiftCol=iC)  # here!
                         ])
                RUN = _rectangle(100 , 100, sXmlCells=sXmlCells)
                res = _strEval(GT, RUN, 0.95)
                assert res == (1, 1, 1), res
                res = _strEval(GT, RUN, 0.51)
                assert res == (2, 0, 0), res
        
                sXmlCells = " ".join([  _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70", iShiftRow=iR, iShiftCol=iC)
                                      , _cell_xml(0,1,0,1,"60,60 70,60 70,66 60,66", iShiftRow=iR, iShiftCol=iC) #here
                                      , _cell_xml(1,0,1,0,"10,70 20,70 20,80 10,90", iShiftRow=iR, iShiftCol=iC)
                                 ])
                RUN = _rectangle(100 , 100, sXmlCells=sXmlCells)
                res = _strEval(GT, RUN, 0.95)
                assert res == (1, 1, 1), res
                res = _strEval(GT, RUN, 0.51)
                assert res == (2, 0, 0), res

                # some extra cell
                sXmlCells = " ".join([  _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70", iShiftRow=iRgt, iShiftCol=iCgt)
                                      , _cell_xml(0,1,0,1,"60,60 70,60 70,70 60,70", iShiftRow=iRgt, iShiftCol=iCgt)
                                      , _cell_xml(1,0,1,0,"10,70 20,70 20,80 10,90", iShiftRow=iRgt, iShiftCol=iCgt)
                                      , _cell_xml(1,1,1,1,"30,70 40,70 40,80 50,90", iShiftRow=iRgt, iShiftCol=iCgt)
                                 ])
                RUN = _rectangle(100 , 100, sXmlCells=sXmlCells)
                res = _strEval(GT, RUN, 0.95)
                assert res == (2, 2, 0), res
                res = _strEval(GT, RUN, 0.51)
                assert res == (2, 2, 0), res
                
                # with some reduced size
                sXmlCells = " ".join([  _cell_xml(0,0,0,0,"10,60 20,60 20,70 10,70", iShiftRow=iRgt, iShiftCol=iCgt)
                                      , _cell_xml(0,1,0,1,"60,60 70,60 70,66 60,66", iShiftRow=iRgt, iShiftCol=iCgt) # here
                                      , _cell_xml(1,0,1,0,"10,70 20,70 20,76 10,86", iShiftRow=iRgt, iShiftCol=iCgt) # here
                                      , _cell_xml(1,1,1,1,"30,70 40,70 40,80 50,90", iShiftRow=iRgt, iShiftCol=iCgt)
                                 ])
                RUN = _rectangle(100 , 100, sXmlCells=sXmlCells)
                res = _strEval(GT, RUN, 0.95)
                assert res == (0, 4, 2), res
                res = _strEval(GT, RUN, 0.51)
                assert res == (2, 2, 0), res

def test_table_recognition_spanning_cells_simple():
    #    ###
    #    # #
    for bRotate in [False, True]:
        # bRotate allows to swap Xs and Ys"
        sXmlCells = " ".join([  _cell_xml(0,0,0,2,"10,60 100,60 100,70 10,70", bRotate=bRotate)  # flat horizontal rectangle spanning over 3 cols
                              , _cell_xml(1,0,1,0,"10,80  50,80  50,90 10,90", bRotate=bRotate)
                              , _cell_xml(1,2,1,2,"60,80 100,80 100,90 60,90", bRotate=bRotate)
                         ])
        GT  = _rectangle(100, 100 , sXmlCells=sXmlCells)
    
        # RUN same as GT
        RUN = _rectangle(100 , 100, sXmlCells=sXmlCells)
        res = _strEval(GT, RUN, 0.95)
        assert res == (3, 0, 0), res
    
        
        #    ###
        #    ##
        # showing that empty cells are ignored
        sXmlCells = " ".join([  _cell_xml(0,0,0,2,"10,60 100,60 100,70 10,70", bRotate=bRotate)  # flat horizontal rectangle spanning over 3 cols
                              , _cell_xml(1,0,1,0,"10,80  50,80  50,90 10,90", bRotate=bRotate)
                              , _cell_xml(1,1,1,1,"60,80 100,80 100,90 60,90", bRotate=bRotate)
                         ])
        RUN = _rectangle(100 , 100, sXmlCells=sXmlCells)
        res = _strEval(GT, RUN, 0.95)
        assert res == (3, 0, 0), res
        
        #    ###
        #    ###
        sXmlCells = " ".join([  _cell_xml(0,0,0,2,"10,60 100,60 100,70 10,70", bRotate=bRotate)  # flat horizontal rectangle spanning over 3 cols
                              , _cell_xml(1,0,1,0,"10,80  90,80  90,90 10,90", bRotate=bRotate)  # another long flat rectangle
                         ])
        RUN = _rectangle(100 , 100, sXmlCells=sXmlCells)
        res = _strEval(GT, RUN, 0.95)
        assert res == (0, 1, 3), res
        res = _strEval(GT, RUN, 0.31)
        assert res == (1, 0, 2), res

                
def test_table_recognition_spanning_cells_less_simple():
    #    ### #
    #    # ###
    for bRotate in [False, True]:
        # bRotate allows to swap Xs and Ys"
        sXmlCells = " ".join([  _cell_xml(0,0,0,2,"10,60  100,60 100,70  10,70", bRotate=bRotate)  # flat horizontal rectangle spanning over 3 cols
                              , _cell_xml(0,3,0,3,"210,60 250,60 250,70 210,70", bRotate=bRotate)
                              , _cell_xml(1,0,1,0,"10,80   50,80  50,90  10,90", bRotate=bRotate)
                              , _cell_xml(1,1,1,3,"60,80  260,80 260,90  60,90", bRotate=bRotate)
                         ])
        GT  = _rectangle(100, 100 , sXmlCells=sXmlCells)
    
        # RUN same as GT
        RUN = _rectangle(100 , 100, sXmlCells=sXmlCells)
        res = _strEval(GT, RUN, 0.95)
        assert res == (5, 0, 0), res

        #    ### #
        #    #   #
        sXmlCells = " ".join([  _cell_xml(0,0,0,2,"10,60  100,60 100,70  10,70", bRotate=bRotate)  # flat horizontal rectangle spanning over 3 cols
                              , _cell_xml(0,3,0,3,"210,60 250,60 250,70 210,70", bRotate=bRotate)
                              , _cell_xml(1,0,1,0,"10,80   50,80  50,90  10,90", bRotate=bRotate)
                              , _cell_xml(1,3,1,3,"210,80  260,80 260,90 210,90", bRotate=bRotate)
                         ])
        # RUN same as GT
        RUN = _rectangle(100 , 100, sXmlCells=sXmlCells)
        res = _strEval(GT, RUN, 0.95)
        assert res == (2, 2, 3), res
        res = _strEval(GT, RUN, 0.1)
        assert res == (4, 0, 1), res
 

# ----------------------------------------------------------------------
if __name__ == "__main__":
    # to test manually some code...
    # test_reg_quarter()
    # test_multi_table()
    # test_table_recognition_obvious()
    # test_table_recognition_simple_horizontal()
    # test_table_recognition_simple_vertical()
    # test_table_recognition_simple_horizontal_vertical()
    # test_table_recognition_spanning_cells_simple()
    test_table_recognition_spanning_cells_less_simple()
    print("ok, test(s) done")

    
    
    