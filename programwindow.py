import locale
import math

from PyQt5.QtWidgets import QMainWindow

from plottrajectory import *
from programui import Ui_MainWindow
from constants import *

LEGEND_OFFSET = (10, -10)
ITERATION_LIMIT = 1e4


def layout_children_set_enabled(layout, enabled):
    i = 0
    while layout.itemAt(i) is not None:
        layout.itemAt(i).widget().setEnabled(enabled)
        i += 1


class ProgramWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.buildTrajectoriesBtn.clicked.connect(self.build_trajectories)

        # стандартные значения величин (массы, скорости и т.д.)
        self.x = math.nan
        self.y = math.nan
        self.m = math.nan
        self.alpha = math.nan
        self.v0 = math.nan
        self.cf = math.nan
        self.rho = math.nan
        self.s = math.nan
        self.delta_t = math.nan

        self.g = math.nan

        self.build_with_resistance = None
        self.build_without_resistance = None

        self.gEdit.setText(locale.format_string('%.2f', G))
        self.WoARCheck.stateChanged.connect(
            self.switch_without_resistance_state
        )
        self.WARCheck.stateChanged.connect(
            self.switch_with_resistance_state
        )

    def switch_without_resistance_state(self, state):
        layout_children_set_enabled(self.WoARPropsLayout, state)

    def switch_with_resistance_state(self, state):
        layout_children_set_enabled(self.WARPropsLayout, state)
        layout_children_set_enabled(self.WARParamsLayout, state)

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
            self.build_with_resistance = self.WARCheck.isChecked()
            self.build_without_resistance = self.WoARCheck.isChecked()
            self.errorMessage.setText('')

        except ValueError:
            self.errorMessage.setText('Неверно введены данные')

    def build_trajectory_with_resistance(self, x, y, vx, vy):
        xx = [x]
        yy = [y]
        i = 1
        h = y
        while (y > 0 or i == 1) and i < ITERATION_LIMIT:
            try:
                x, y, vx, vy = trajectory_point_with_resistance(
                    x=x, y=y, vx=vx, vy=vy, m=self.m, cf=self.cf, s=self.s,
                    rho=self.rho, g=self.g, delta_t=self.delta_t
                )

            except OverflowError:
                break
            h = max(y, h)
            xx += [x]
            yy += [y]
            i += 1
        plot = self.graphicsView.plot(xx, yy, pen='r')
        legend = self.graphicsView.getPlotItem().addLegend(offset=LEGEND_OFFSET)
        legend.addItem(plot, 'траектория с сопротивлением силы воздуха')
        self.HWAREdit.setText(locale.format_string('%.2f', h))
        self.SWAREdit.setText(locale.format_string('%.2f', x))

    def build_trajectory_without_resistance(self, x0, y0, vx, vy):
        xx = [x0]
        yy = [y0]
        i = 1
        x, y = x0, y0
        h = y
        while (y > 0 or i == 1) and i < ITERATION_LIMIT:
            try:
                x, y = trajectory_point_without_resistance(
                    x=x0, y=y0, vx=vx, vy=vy, g=self.g, t=i * self.delta_t
                )

            except OverflowError:
                break
            h = max(y, h)
            xx += [x]
            yy += [y]
            i += 1
        plot = self.graphicsView.plot(xx, yy, pen='b')
        legend = self.graphicsView.getPlotItem().addLegend(offset=LEGEND_OFFSET)
        legend.addItem(plot, 'траектория без сопротивления силы воздуха')
        self.HWoAREdit.setText(locale.format_string('%.2f', h))
        self.SWoAREdit.setText(locale.format_string('%.2f', x))

    def build_trajectories(self):

        self.graphicsView.clear()
        self.HWAREdit.clear()
        self.HWoAREdit.clear()
        self.SWAREdit.clear()
        self.SWoAREdit.clear()

        self.read_data()
        x, y = self.x, self.y
        vx0 = self.v0 * math.cos(math.radians(self.alpha))
        vy0 = self.v0 * math.sin(math.radians(self.alpha))
        if self.build_with_resistance:
            self.build_trajectory_with_resistance(x, y, vx0, vy0)
        if self.build_without_resistance:
            self.build_trajectory_without_resistance(x, y, vx0, vy0)
        self.graphicsView.getPlotItem().showGrid(True, True)
