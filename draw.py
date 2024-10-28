import pyqtgraph as pg
from PyQt5 import QtWidgets
from typing import Optional, Union


class Draw:

    def __init__(self, root, widget, title="", label_horizontal="", label_vertical="",
                 label_horizontal_units="", label_vertical_units="", background_color="w"):
        self.plot_widget = pg.PlotWidget()
        self.root = root
        self.__title = title
        self.__label_horizontal = label_horizontal
        self.__label_vertical = label_vertical
        self.__label_horizontal_units = label_horizontal_units
        self.__label_vertical_units = label_vertical_units
        self.__background_color = background_color
        self.pens = []
        self.data = []
        self.settings()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.plot_widget)
        self.root.setLayout(layout)
        self.root.gridlayout = QtWidgets.QGridLayout(widget)
        self.root.gridlayout.addWidget(self.plot_widget, 0, 1)

    def settings(self):
        self.plot_widget.setLabels(title=self.__title)
        self.plot_widget.setLabel('bottom', self.__label_horizontal, units=self.__label_horizontal_units)
        self.plot_widget.setLabel('left', self.__label_vertical, units=self.__label_vertical_units )
        self.plot_widget.setBackground(self.__background_color)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setMouseEnabled(x=False, y=False)

    def pen(self, color: Union[list, tuple], width: Union[list, int]):
        if type(color) is list and type(width) is list and len(color) == len(width):
            for clr, wdt in zip(color, width):
                if type(clr) == tuple and len(clr) == 3:
                    self.pens.append(pg.mkPen(color=clr, width=wdt))
                else:
                    raise "Color tuple don't have length 3!"
        elif type(color) is tuple and len(color) == 3 and type(width) is int:
            self.pens.append(pg.mkPen(color=color, width=width))

    def create_data(self, x: Optional[list], y: Union[Optional[list], list]):
        if x and y:
            if type(y[0]) is list:
                if len(self.pens) == len(y):
                    for i in range(len(y)):
                        self.data.append(self.plot_widget.plot(x, y[i], pen=self.pens[i]))
            else:
                if len(self.pens) > 0:
                    self.data.append(self.plot_widget.plot(x, y, pen=self.pens[0]))

    def update_data(self, x: Optional[list], y: Union[Optional[list], list]):
        if x and y:
            if type(y[0]) is list:
                if len(self.pens) == len(y):
                    if len(self.data) == len(y):
                        for i in range(len(y)):
                            self.data[i].setData(x, y[i])
            else:
                if len(self.pens) > 0 and len(self.data) == 1:
                    self.data[0].setData(x, y)
