import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QGroupBox, QRadioButton
, QCheckBox, QPushButton, QMenu, QGridLayout, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QTextEdit, QFormLayout, QComboBox)
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
# from odesf import eq_to_pyfunc
from ode_parser import func_from_string
from ode import *

__AVAILABLE_SOLVERS__ = [ForwardEuler(), ForwardEulerCromer(), RungeKutta4(), RungeKuttaFehlberg(), BackwardEuler()]

"""
dx/dt = sigma * (y - x)
dy/dt = rho * x - y - x * z
dz/dt = x * y - beta * z 

sigma = 10e0
rho = 28e0
beta = 8e0 / 3e0 


"""

class Solver(QWidget):

    def __init__(self):
        super().__init__()
        self.active_plot_items = []
        self.active_legend_items = []
        self.xaxis = []
        self.yaxis = []
        self.cbs = []
        self.initUI()
        self.solve_button.clicked.connect(self.solve_equations)
        # self.hbox_cb.clicked.connect(self.reset)
        # self.checkbox2.clicked.connect(self.help)
        self.reset_button.clicked.connect(self.plot_reset)
        self.plot_button.clicked.connect(self.plot_lines)

    def initUI(self):
        self.resize(1600,800)
        self.grid = QGridLayout()
        self.grid.addWidget(self.createInformationBoard(), 0, 0)
        self.grid.addWidget(self.createConditions(), 1, 0)
        self.grid.addWidget(self.createEquations(), 2, 0)
        self.grid.addWidget(self.createButtons(), 3, 0)
        self.grid.addWidget(self.createPlotArea(), 0, 1, 4, 3)


        self.setLayout(self.grid)
        self.setWindowTitle('pyODEqSolver')
        self.setGeometry(200, 200, 1400, 700)
        self.show()

    def info_reset(self):
        item_list = list(range(self.info_form.count()))
        item_list.reverse()

        for i in item_list:
            item = self.info_form.itemAt(i)
            self.info_form.removeItem(item)
            if item.widget():
                item.widget().deleteLater()

    def reset(self):

        item_list = list(range(self.hbox_cb_x.count()))
        item_list.reverse()

        for i in item_list:
            item = self.hbox_cb_x.itemAt(i)
            self.hbox_cb_x.removeItem(item)
            if item.widget():
                item.widget().deleteLater()

        item_list = list(range(self.hbox_cb_y.count()))
        item_list.reverse()

        for i in item_list:
            item = self.hbox_cb_y.itemAt(i)
            self.hbox_cb_y.removeItem(item)
            if item.widget():
                item.widget().deleteLater()

    def add_cbx(self):
        for dp_var in self.dep_ls:
            cb = QCheckBox(dp_var)
            self.hbox_cb_x.addWidget(cb)
            cb = QCheckBox(dp_var)
            self.hbox_cb_y.addWidget(cb)

        for idp_var in self.indep_ls:
            cb = QCheckBox(idp_var)
            # cb.clicked.connect(lambda : self.help())
            self.hbox_cb_x.addWidget(cb)


    def solve_equations(self):
        self.reset()
        self.plot_reset()
        self.info_reset()
        _a = float(self.edit_a.text())
        _b = float(self.edit_b.text())
        _h = float(self.edit_h.text())

        ivp_str = self.edit_ivp.text().split(",")
        _ivp = [float(i) for i in ivp_str]

        eq_str = self.equation_edit.toPlainText().replace("\n", "")
        eq_str = eq_str.split(";")
        eq_ls = [eq for eq in eq_str if len(eq) > 2]

        co_str = self.constant_edit.toPlainText().replace("\n", "")
        co_str = co_str.split(";")
        co_ls = [c for c in co_str if len(c) > 2]

        func, dep_dict, indep_dict = func_from_string(equations=eq_ls, constants=co_ls)
        self.dep_dict = dep_dict
        self.indep_dict = indep_dict
        self.dep_ls = list(dep_dict.values())
        self.indep_ls = list(indep_dict.keys())

        self.add_cbx()

        _n = len(eq_ls)

        solver_idx = self.solver_method.currentIndex()
        solver = __AVAILABLE_SOLVERS__[solver_idx]
        name_solver = solver.__class__.__name__
        self.info_form.addRow('Solver Method: ', QLabel(f"{name_solver}"))

        solver.init(a=_a, b=_b, h=_h, ivp=_ivp, func=func, n=_n)
        solver.solve()

        self.plot_t = solver.x
        self.plot_y = solver.y

        self.info_form.addRow('Solving Steps: ', QLabel(f"{solver.x.shape[0] - 1}"))

        var_data_dict = {}
        for i in range(len(self.dep_ls)):
            var_data_dict[self.dep_ls[i]] = self.plot_y[:,i]
        for i in range(len(self.indep_ls)):
            var_data_dict[self.indep_ls[i]] = self.plot_t
        self.var_data_dict = var_data_dict


        self.info_form.addRow('Solvering Time: ', QLabel(f"{solver.solving_time:.4f} s"))
        self.info_form.addRow('Solved Results (Last): ', QLabel(f"{solver.y[-1]}"))

        print("Finished Solving")

    def createInformationBoard(self):
        groupbox = QGroupBox('Information')
        groupbox.setFlat(True)
        self.info_form = QFormLayout()
        self.info_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        self.info_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)


        groupbox.setLayout(self.info_form)

        return groupbox



    def createConditions(self):
        groupbox = QGroupBox('Conditions')
        groupbox.setFlat(True)

        groupbox.setMaximumWidth(500)

        # groupbox.setFlat(True)

        hbox_a = QHBoxLayout()
        hbox_b = QHBoxLayout()
        hbox_h = QHBoxLayout()
        hbox_ivp = QHBoxLayout()
        hbox_solvers = QHBoxLayout()


        label_a = QLabel("Interval start: ")
        self.edit_a = QLineEdit('0')
        hbox_a.addWidget(label_a)
        hbox_a.addWidget(self.edit_a)

        label_b = QLabel("Interval end: ")
        self.edit_b = QLineEdit('10')
        hbox_b.addWidget(label_b)
        hbox_b.addWidget(self.edit_b)

        label_h = QLabel("Step size: ")
        self.edit_h = QLineEdit('0.01')
        hbox_h.addWidget(label_h)
        hbox_h.addWidget(self.edit_h)

        label_ivp = QLabel("Initial values: ")
        self.edit_ivp = QLineEdit('0,1,0')
        hbox_ivp.addWidget(label_ivp)
        hbox_ivp.addWidget(self.edit_ivp)

        label_solver_methods = QLabel("Chose Methods: ")
        self.solver_method = QComboBox()
        self.solver_method.addItems([solver.__class__.__name__ for solver in __AVAILABLE_SOLVERS__])
        self.solver_method.setCurrentIndex(2)
        hbox_solvers.addWidget(label_solver_methods)
        hbox_solvers.addWidget(self.solver_method)


        vbox = QVBoxLayout()
        vbox.addLayout(hbox_a)
        vbox.addLayout(hbox_b)
        vbox.addLayout(hbox_h)
        vbox.addLayout(hbox_ivp)
        vbox.addLayout(hbox_solvers)

        vbox.addStretch(1)
        groupbox.setLayout(vbox)

        return groupbox

    def createEquations(self):
        
        groupbox = QGroupBox('Equations')
        groupbox.setFlat(True)

        groupbox.setMaximumWidth(500)

        # groupbox.setFlat(True)

        eq_example = """
        dx/dt = sigma * (y - x);
        dy/dt = rho * x - y - x * z;
        dz/dt = x * y - beta * z;
        """

        con_example = """
        sigma = 10e0;
        rho = 28e0;
        beta = 8e0 / 3e0;
        """
        self.equation_edit = QTextEdit(eq_example)
        self.constant_edit = QTextEdit(con_example)

        vbox = QVBoxLayout()
        vbox.addWidget(self.equation_edit)
        vbox.addWidget(self.constant_edit)

        vbox.addStretch(1)
        groupbox.setLayout(vbox)

        return groupbox

    def createButtons(self):
        groupbox = QGroupBox()
        groupbox.setFlat(True)

        self.check_button = QPushButton("Check")
        self.solve_button = QPushButton("Solve")
        self.reset_button = QPushButton("Reset")
        self.plot_button = QPushButton("Plot")


        hbox = QHBoxLayout()
        hbox.addWidget(self.check_button)
        hbox.addWidget(self.solve_button)
        hbox.addWidget(self.reset_button)
        hbox.addWidget(self.plot_button)

        groupbox.setLayout(hbox)

        return groupbox


    def createPlotArea(self):
        plotbox = QGroupBox("Plot")
        plotbox.setFlat(True)

        self.graphWidget = pg.PlotWidget()

        self.graphWidget.setBackground('#000000')
        # self.graphWidget.setTitle("Your Title Here", color="b", size="30pt")
        self.graphWidget.showGrid(x=True, y=True)

        hbox_graph = QHBoxLayout()
        hbox_graph.addWidget(self.graphWidget)

        self.group_cb = QHBoxLayout()
        self.hbox_cb_x = QHBoxLayout()
        self.hbox_cb_x.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hbox_cb_y = QHBoxLayout()
        self.hbox_cb_y.setAlignment(Qt.AlignmentFlag.AlignLeft)
        x_label = QLabel("X Axis: ")
        x_label.setMaximumWidth(50)
        self.group_cb.addWidget(x_label)
        y_label = QLabel("Y Axis: ")
        y_label.setMaximumWidth(50)

        self.group_cb.addLayout(self.hbox_cb_x)
        self.group_cb.addWidget(y_label)
        self.group_cb.addLayout(self.hbox_cb_y)

        vbox_plot = QVBoxLayout()
        vbox_plot.addLayout(hbox_graph)
        vbox_plot.addLayout(self.group_cb)

        plotbox.setLayout(vbox_plot)


        return plotbox

    def plot(self, x, y, plotname, color):
        # styles = {'color':'r', 'font-size':'20px'}
        # self.graphWidget.setLabel('left', 'Temperature (°C)', **styles)
        # self.graphWidget.setLabel('bottom', 'Hour (H)', **styles)
        # self.graphWidget.setLabel('left', "<span style=\"color:red;font-size:20px\">Temperature (°C)</span>")
        # self.graphWidget.setLabel('bottom', "<span style=\"color:red;font-size:20px\">Hour (H)</span>")
        pen = pg.mkPen(color=color)
        plot = self.graphWidget.plot(x, y, name=plotname, pen=pen, symbolSize=5, symbolBrush=(color))
        self.active_plot_items.append(plot)

    def plot_lines(self):
        self.clear_plot_items()

        legend = self.graphWidget.addLegend()
        self.active_legend_items.append(legend)

        plot_x_text = []
        plot_y_text = []
        for i in range(self.hbox_cb_x.count()):
            item = self.hbox_cb_x.itemAt(i)
            w = item.widget()
            if w.isChecked():
                plot_x_text.append(w.text())

        for i in range(self.hbox_cb_y.count()):
            item = self.hbox_cb_y.itemAt(i)
            w = item.widget()
            if w.isChecked():
                plot_y_text.append(w.text())
        
        n = 0
        colors = ["#FFFFFF", "#FF0000", "#00FFFF", "#00FF00", "#FF99FF", "#FFFF00"]
        for xd in plot_x_text:
            for yd in plot_y_text:
                self.plot(self.var_data_dict[xd], self.var_data_dict[yd], plotname = xd + "-" + yd, color=colors[n])
                if n < len(colors) - 1:
                    n += 1
                else:
                    n = 0

    def plot_reset(self):
        self.clear_plot_items()
        self.clear_checkbox_checked()


    def clear_plot_items(self):
        for active_item in self.active_plot_items:
            active_item.clear()

        for active_legend in self.active_legend_items:
            active_legend.clear()

    def clear_checkbox_checked(self):

        for i in range(self.hbox_cb_x.count()):
            item = self.hbox_cb_x.itemAt(i)
            w = item.widget()
            # print(w.isChecked())
            if w.isChecked():
                w.setChecked(False)


        for i in range(self.hbox_cb_y.count()):
            item = self.hbox_cb_y.itemAt(i)
            w = item.widget()
            if w.isChecked():
                w.setChecked(False)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Solver()
    sys.exit(app.exec())