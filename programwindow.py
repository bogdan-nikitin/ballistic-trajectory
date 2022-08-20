# WAR - with air resistance
# WoAR - without air resistance

import sys
import locale
import math

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QDoubleValidator, QValidator

from constants import *
from calculate_flight import *
from programui import Ui_MainWindow


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
        self.setup_validators()
        self.buildTrajectoriesBtn.clicked.connect(self.build_trajectories)

        # обнуляем значения величин (массы, скорости и т.д.)
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

        # флаги, отвечающие за необходимость построения соотвествующего графика
        self.build_with_resistance = None
        self.build_without_resistance = None

        self.gEdit.setText(locale.format_string('%g', G))
        self.WoARCheck.stateChanged.connect(
            self.switch_without_resistance_state
        )
        self.WARCheck.stateChanged.connect(
            self.switch_with_resistance_state
        )
        # устанавливаем форму тела по умолчанию
        self.shape_changed(0)
        self.shapeBox.currentIndexChanged.connect(self.shape_changed)

        self.graphicsView.setBackground('w')
        # TODO: сделать заблокированное соотношение опциональным и добавить
        #  возможность выбора в GUI (или хотя бы закоммитить что есть)
        self.graphicsView.getPlotItem().setAspectLocked()

    def setup_validators(self):
        positive_num_validator = QDoubleValidator(self)
        positive_num_validator.setBottom(sys.float_info.min)
        for field in [self.mEdit, self.gEdit, self.delta_tEdit, self.SEdit]:
            field.setValidator(positive_num_validator)
        not_negative_validator = QDoubleValidator(self)
        not_negative_validator.setBottom(0)
        for field in [self.yEdit, self.rhoEdit, self.CfEdit, self.v0Edit]:
            field.setValidator(not_negative_validator)
        angle_validator = QDoubleValidator(self)
        angle_validator.setBottom(0)
        angle_validator.setTop(180)
        self.alphaEdit.setValidator(angle_validator)
        self.xEdit.setValidator(QDoubleValidator(self))

    def validate_data(self):
        for field in [
            self.xEdit, self.yEdit, self.v0Edit, self.mEdit, self.alphaEdit,
            self.gEdit, self.delta_tEdit, self.CfEdit, self.rhoEdit, self.SEdit
        ]:
            state, *_ = field.validator().validate(field.text(), 0)
            if state != QValidator.Acceptable:
                return False, field
        return True, None

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

        is_valid, _ = self.validate_data()
        if is_valid:
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
        else:
            self.errorMessage.setText('Неверно введены данные')
            return False
        return True

    def display_iterations_limit_error(self):
        self.errorMessage.setText('Превышен лимит итераций')

    def build_trajectory_with_resistance(self, x0, y0, vx, vy):
        xn, yn, s, h, t, i = trajectory_with_resistance(
            x0, y0, vx, vy, self.g, self.m, self.cf, self.s, self.rho,
            self.delta_t
        )
        if i >= ITERATIONS_LIMIT:
            self.display_iterations_limit_error()
        plot = self.graphicsView.plot(xn, yn, pen='r')
        # plot.getViewBox().setAspectLocked()
        plot.getViewBox().enableAutoRange(axis='xy')
        legend = self.graphicsView.getPlotItem().addLegend(offset=LEGEND_OFFSET)
        legend.addItem(plot, 'с сопротивлением силы воздуха')
        self.HWAREdit.setText(locale.format_string('%.2f', h))
        self.SWAREdit.setText(locale.format_string('%.2f', s))
        self.tWAREdit.setText(locale.format_string('%.2f', t))

    def build_trajectory_without_resistance(self, x0, y0, vx, vy):
        xn, yn, s, h, t, i = trajectory_without_resistance(
            x0, y0, vx, vy, self.g, self.delta_t
        )
        if i >= ITERATIONS_LIMIT:
            self.display_iterations_limit_error()
        plot = self.graphicsView.plot(xn, yn, pen='b')
        plot.getViewBox().enableAutoRange(axis='xy')
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
        self.graphicsView.getPlotItem().showGrid(True, True)
        self.graphicsView.getPlotItem().setTitle(
            'Траектория(и) баллистического движения тела'
        )
        if self.build_with_resistance:
            self.build_trajectory_with_resistance(x, y, vx0, vy0)
        if self.build_without_resistance:
            self.build_trajectory_without_resistance(x, y, vx0, vy0)
