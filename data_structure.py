import xml.dom.minidom
# from bs4 import BeautifulSoup
import os


class Cell(object):

    def __init__(self, start_row, start_col, b_box, end_row, end_col, content=''):
        self._start_row = int(start_row)
        self._start_col = int(start_col)
        self._b_box = b_box
        self._content = content
        # self._region = region

        # check for end-row and end-col special case
        if end_row == -1:
            self._end_row = self.start_row
        else:
            self._end_row = int(end_row)
        if end_col == -1:
            self._end_col = self._start_col
        else:
            self._end_col = int(end_col)

    @property
    def start_row(self):
        return self._start_row

    @property
    def start_col(self):
        return self._start_col

    @property
    def end_row(self):
        return self._end_row

    @property
    def end_col(self):
        return self._end_col

    @property
    def b_box(self):
        return self._b_box

    @property
    def content(self):
        return self._content

    def __str__(self):
        return 'start_row: ' + str(self.start_row) + ' end_row: ' + str(self.end_row) + ' start_col: ' + \
               str(self.start_col) + ' end_col: ' + str(self.end_col) + '    ' + self.content


class AdjRelation:

    DIR_HORIZ = 1
    DIR_VERT = 2

    def __init__(self, fromText, toText, direction):
        # @param: fromText, toText are Cell objects
        self._fromText = fromText
        self._toText = toText
        self._direction = direction

    @property
    def fromText(self):
        return self._fromText

    @property
    def toText(self):
        return self._toText

    @property
    def direction(self):
        return self._direction

    def __str__(self):
        if self.direction == self.DIR_VERT:
            dir = "vertical"
        else:
            dir = "horizontal"
        return self._fromText.content + '  ' + self._toText.content + '    ' + dir

    def isEqual(self, otherRelation):
        # if self.fromText != otherRelation.fromText:
        #     print("fromText not equal {} and {}".format(self.fromText.content, otherRelation.fromText.content))
        # elif self.toText != otherRelation.toText:
        #     print("toText not equal")
        # elif self.direction != otherRelation.direction:
        #     print("direction not equal")

        return self.fromText.content == otherRelation.fromText.content and \
               self.toText.content == otherRelation.toText.content and self.direction == otherRelation.direction


class Table:

    def __init__(self, tableNode):
        self._root = tableNode
        self._id = tableNode.getAttribute("id")
        self._page = tableNode.getElementsByTagName("region")[0].getAttribute("page")
        self._page = tableNode.getAttribute("page")
        self._b_box = 0
        # self._tab_coords = tableNode.getElementsByTagName("tab_coords")[0].getAttribute("points")
        self._maxRow = 0    # PS: indexing from 0
        self._maxCol = 0
        # self._crosspage = False  # if the table contains multiple regions
        self.cells = []
        self.adj_relations = []    # save the adj_relations for the table
        self.found = False    # check if the find_aj_relations() has been called once

        self.parse_table()

    def __str__(self):
        return "page: " + str(self.page) + "   " + str(self._maxRow) + " / " + str(self._maxCol) + " " + str(self.found)
        # return self._tab_coords

    @property
    def page(self):
        return self._page

    @property
    def id(self):
        return self._id

    # parse input xml to cell lists
    def parse_table(self):
        # regions = self._root.getElementsByTagName("region")
        # if len(regions) != 1:
        #     self._crosspage = True

        cells = self._root.getElementsByTagName("cell")
        max_row = max_col = 0
        for cell in cells:
            sr = cell.getAttribute("start-row")
            sc = cell.getAttribute("start-col")

            b_box = cell.getElementsByTagName("bounding-box")[0]
            b_value = b_box.getAttribute("x1") + "," + b_box.getAttribute("y1") + "," + \
                      b_box.getAttribute("x2") + "," + b_box.getAttribute("y2")
            # # TODO: why it does not split
            # b_points = cell.getElementsByTagName("coords")[0].getAttribute("points")

            text = cell.getElementsByTagName("content")[0].firstChild.nodeValue
            er = cell.getAttribute("end-row") if cell.hasAttribute("end-row") else -1
            ec = cell.getAttribute("end-col") if cell.hasAttribute("end-col") else -1
            new_cell = Cell(start_row=sr, start_col=sc, b_box=b_value, content=text, end_row=er, end_col=ec)
            # new_cell = Cell(start_row=sr, start_col=sc, b_box=b_points, content=text, end_row=er, end_col=ec)
            max_row = max(max_row, int(sr), int(er))
            max_col = max(max_col, int(sc), int(ec))
            self.cells.append(new_cell)
        self._maxCol = max_col
        self._maxRow = max_row
        # print(max_row, max_col)

    # generate a table-like structure for finding adj_relations
    def convert_2d(self):
        table = [[0 for x in range(self._maxCol+1)] for y in range(self._maxRow+1)]
        # print(table[self._maxRow][self._maxCol])
        for cell in self.cells:
            # print(cell)

            cur_row = cell.start_row
            while cur_row <= cell.end_row:
                cur_col = cell.start_col
                while cur_col <= cell.end_col:
                    table[cur_row][cur_col] = cell
                    cur_col += 1
                cur_row += 1

        # # print out table for test
        # for x in range(self._maxRow+1):
        #     for y in range(self._maxCol+1):
        #         print(table[x][y])
        #     print("\n")

        return table

    # todo: fix blank cell relations
    def find_aj_relations(self):
        if self.found:
            return self.adj_relations

        else:
            if len(self.cells) == 0:
                print("table is not parsed for further steps.")
                self.parse_table()
                self.find_aj_relations()
            else:
                retVal = []
                tab = self.convert_2d()

                # find horizontal relations
                for r in range(self._maxRow+1):
                    for c_from in range(self._maxCol):
                        c_to = c_from + 1
                        if tab[r][c_from] != tab[r][c_to] and tab[r][c_from] != '' and tab[r][c_to] != '':
                            adj_relation = AdjRelation(tab[r][c_from], tab[r][c_to], AdjRelation.DIR_HORIZ)
                            retVal.append(adj_relation)

                # find vertical relations
                for c in range(self._maxCol+1):
                    for r_from in range(self._maxRow):
                        r_to = r_from + 1
                        if tab[r_from][c] != tab[r_to][c] and tab[r_from][c] != '' and tab[r_to][c] != '':
                            adj_relation = AdjRelation(tab[r_from][c], tab[r_to][c], AdjRelation.DIR_VERT)
                            retVal.append(adj_relation)

                # eliminate duplicates
                repeat = True
                while repeat:
                    repeat = False
                    duplicates = []

                    for ar1 in retVal:
                        for ar2 in retVal:
                            if ar1 != ar2:
                                if ar1.direction == ar2.direction and ar1.fromText == ar2.fromText and\
                                        ar1.toText == ar2.toText:
                                    duplicates.append(ar2)
                                    break
                        else:
                            continue
                        break

                    if len(duplicates) > 0:
                        repeat = True
                        retVal.remove(duplicates[0])

                # # print out the relations for test
                # print("found {} relations in table {}:".format(len(retVal), self.id))
                # for ret in retVal:
                #     print(ret)

                self.found = True
                self.adj_relations = retVal
                return self.adj_relations


if __name__ == "__main__":
    resultFile = "./annotations/test2.xml"
    # res_tables = []
    res_dom = xml.dom.minidom.parse(resultFile)
    res_root = res_dom.documentElement
    tables = res_root.getElementsByTagName("table")
    for res_table in tables:
        t = Table(res_table)
        print(t)
        t.convert_2d()
        # res_tables.append(t)
        # t.find_aj_relations()
