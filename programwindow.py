import math

from PyQt5.QtWidgets import QMainWindow

from constants import *
from programui import Ui_MainWindow
from plottrajectory import *
import locale


class ProgramWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.buildTrajectoriesBtn.clicked.connect(self.build_trajectories)
        self.n = 500

        # стандартные значения величин (массы, скорости и т.д.)
        self.x = math.nan
        self.y = math.nan
        self.m = math.nan
        self.alpha = math.nan
        self.v0 = math.nan
        self.cf = math.nan
        self.rho = math.nan
        self.s = math.nan
        self.g = math.nan
        self.delta_t = math.nan
        self.build_with_resistance = None
        self.build_without_resistance = None
        # self.graphicsView.getPlotItem().sigRangeChanged.connect(
        #     lambda *args, **kwargs: print(args, kwargs)
        # )

    def read_data(self):
        try:
            self.x = locale.atof(self.xEdit.text())
            self.y = locale.atof(self.yEdit.text())
            self.m = locale.atof(self.mEdit.text())
            self.alpha = locale.atof(self.alphaEdit.text())
            self.v0 = locale.atof(self.v0Edit.text())
            self.cf = locale.atof(self.CfEdit.text())
            self.rho = locale.atof(self.rhoEdit.text())
            self.s = locale.atof(self.SEdit.text())
            self.g = locale.atof(self.gEdit.text())
            self.delta_t = locale.atof(self.delta_tEdit.text())
            self.build_with_resistance = self.withAirResistanceCheck.isChecked()
            self.build_without_resistance = \
                self.withoutAirResistanceCheck.isChecked()
            self.errorMessage.setText('')

        except ValueError:
            self.errorMessage.setText('Неверно введены данные')

    def build_trajectory_with_resistance(self, x, y, vx, vy):
        xx = [x]
        yy = [y]
        for i in range(self.n):
            try:
                x, y, vx, vy = trajectory_point_with_resistance(
                    x=x, y=y, vx=vx, vy=vy, m=self.m, cf=self.cf, s=self.s,
                    rho=self.rho, g=self.g, delta_t=self.delta_t
                )
            except OverflowError:
                break
            xx += [x]
            yy += [y]
        self.graphicsView.plot(xx, yy, pen='r')

    def build_trajectory_without_resistance(self, x, y, vx, vy):
        xx = [x]
        yy = [y]
        for i in range(self.n):
            try:
                xi, yi = trajectory_point_without_resistance(
                    x=x, y=y, vx=vx, vy=vy, g=self.g, t=i * self.delta_t
                )
            except OverflowError:
                break
            xx += [xi]
            yy += [yi]
        self.graphicsView.plot(xx, yy, pen='b')

    def build_trajectories(self):
        self.graphicsView.clear()
        self.read_data()
        x, y = self.x, self.y
        vx0 = self.v0 * math.cos(math.radians(self.alpha))
        vy0 = self.v0 * math.sin(math.radians(self.alpha))
        if self.build_with_resistance:
            self.build_trajectory_with_resistance(x, y, vx0, vy0)
        if self.build_without_resistance:
            self.build_trajectory_without_resistance(x, y, vx0, vy0)
        self.graphicsView.getPlotItem().showGrid(True, True)

