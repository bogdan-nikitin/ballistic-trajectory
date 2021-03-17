import locale
import math

from PyQt5.QtWidgets import QMainWindow

from constants import *
from calculate_flight import *
from programui import Ui_MainWindow

ITERATION_LIMIT = 1e4
LEGEND_OFFSET = (10, -10)
CF_SHAPES = [
    0.47,
    0.50,
    1.05,
    0.82,
    0.04
]


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

        self.gEdit.setText(locale.format_string('%g', G))
        self.WoARCheck.stateChanged.connect(
            self.switch_without_resistance_state
        )
        self.WARCheck.stateChanged.connect(
            self.switch_with_resistance_state
        )
        self.shape_changed(0)
        self.shapeBox.currentIndexChanged.connect(self.shape_changed)

    def shape_changed(self, index):
        if index < len(CF_SHAPES):
            self.CfEdit.setText(locale.format_string('%g', CF_SHAPES[index]))
            self.CfEdit.setDisabled(True)
        else:
            self.CfEdit.setEnabled(True)

    def switch_without_resistance_state(self, state):
        layout_children_set_enabled(self.WoARPropsLayout, state)

    def switch_with_resistance_state(self, state):
        layout_children_set_enabled(self.WARPropsLayout, state)
        layout_children_set_enabled(self.WARParamsLayout, state)
        self.CfEdit.setEnabled(
            state and self.shapeBox.currentIndex() == len(CF_SHAPES)
        )

    def read_data(self):

        self.graphicsView.clear()
        self.HWAREdit.clear()
        self.HWoAREdit.clear()
        self.SWAREdit.clear()
        self.SWoAREdit.clear()
        self.tWAREdit.clear()
        self.tWoAREdit.clear()

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
            return False
        return True

    def build_trajectory_with_resistance(self, x0, y0, vx, vy):
        xx = [x0]
        yy = [y0]
        vx_val = [vx]
        vy_val = [vy]
        h = y0
        i = 1
        x, y = x0, y0
        ax, ay = 0, -self.g
        while (y > 0 or i == 1) and i < ITERATION_LIMIT:
            try:
                x, y, vx, vy, ax, ay = trajectory_point_with_resistance(
                    x=x, y=y, vx=vx, vy=vy, m=self.m, cf=self.cf, s=self.s,
                    rho=self.rho, g=self.g, delta_t=self.delta_t
                )

            except OverflowError:
                break
            # if y < yy[i - 1] and h == y0:
            if vy < 0 and h == y0:
                h = fly_height(y0=yy[i - 1], vy=vy_val[i - 1], ay=ay)
            xx += [x]
            yy += [y]
            vx_val += [vx]
            vy_val += [vy]
            i += 1
        s = fly_distance(x0=xx[i - 2], y0=yy[i - 2],
                         vx=vx_val[i - 2], vy=vy_val[i - 2], ax=ax, ay=ay)
        t = self.delta_t * (i - 2)
        t += flight_time(yy[i - 2], vy_val[i - 2], ay)
        if type(s) == complex:
            s = x
        elif abs(s - xx[i - 1]) > abs(vx):
            s = x
        else:
            xx[i - 1], yy[i - 1] = s, 0
        h = max(y, h)
        plot = self.graphicsView.plot(xx, yy, pen='r')
        legend = self.graphicsView.getPlotItem().addLegend(offset=LEGEND_OFFSET)
        legend.addItem(plot, 'с сопротивлением силы воздуха')
        self.HWAREdit.setText(locale.format_string('%.2f', h))
        self.SWAREdit.setText(locale.format_string('%.2f', s))
        self.tWAREdit.setText(locale.format_string('%.2f', t))

    def build_trajectory_without_resistance(self, x0, y0, vx, vy):
        xx = [x0]
        yy = [y0]
        h = fly_height(y0=y0, vy=vy, ay=-self.g) if vy > 0 else y0
        s = fly_distance(x0=x0, y0=y0, vx=vx, vy=vy, ax=0, ay=-self.g)
        i = 1
        x, y = x0, y0
        while (y > 0 or i == 1) and i < ITERATION_LIMIT:
            try:
                x, y = trajectory_point_without_resistance(
                    x=x0, y=y0, vx=vx, vy=vy, g=self.g, t=i * self.delta_t
                )

            except OverflowError:
                break
            xx += [x]
            yy += [y]
            i += 1
        if type(s) == complex:
            s = x
        elif abs(s - xx[i - 1]) > abs(vx):
            s = x
        else:
            xx[i - 1], yy[i - 1] = s, 0
        h = max(y, h)
        t = flight_time(y0, vy, -self.g)
        plot = self.graphicsView.plot(xx, yy, pen='b')
        legend = self.graphicsView.getPlotItem().addLegend(offset=LEGEND_OFFSET)
        legend.addItem(plot, 'без сопротивления силы воздуха')
        self.HWoAREdit.setText(locale.format_string('%.2f', h))
        self.SWoAREdit.setText(locale.format_string('%.2f', s))
        self.tWoAREdit.setText(locale.format_string('%.2f', t))

    def build_trajectories(self):

        if not self.read_data():
            return
        x, y = self.x, self.y
        vx0 = self.v0 * math.cos(math.radians(self.alpha))
        vy0 = self.v0 * math.sin(math.radians(self.alpha))
        if self.build_with_resistance:
            self.build_trajectory_with_resistance(x, y, vx0, vy0)
        if self.build_without_resistance:
            self.build_trajectory_without_resistance(x, y, vx0, vy0)
        self.graphicsView.getPlotItem().showGrid(True, True)
        self.graphicsView.getPlotItem().setTitle(
            'Траектория(и) баллистического движения тела'
        )
