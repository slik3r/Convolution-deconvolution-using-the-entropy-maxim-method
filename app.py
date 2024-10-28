import random
import sys
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer, QThread
import draw
import sig

signal = sig.Signal()


class Worker(QThread):
    def __init__(self, li, output_arr, impulse_arr, N, step, input_arr, root, parent=None):
        self.li = li
        self.output_arr = output_arr
        self.impulse_arr = impulse_arr
        self.N = N
        self.step = step
        self.input_arr = input_arr
        self.root = root
        super(Worker, self).__init__(parent)

    def run(self):
        signal.deconvolution(self.li, self.output_arr, self.impulse_arr, self.N, self.step)
        signal.energy_delta(self.input_arr, signal.xr)
        self.root.edit_x_energy_delta.setText(str(round(signal.ed, 5)))

    def __del__(self):
        pass

class App(QMainWindow):
    def __init__(self, template_filename):
        super(App, self).__init__()
        self.app = QtWidgets.QApplication([])
        self.root = uic.loadUi(template_filename)

        self.signal = sig.Signal()
        self.run = False

        self.root.start_btn.clicked.connect(self.execute)

        self.x = [0, 1]
        self.y = [0, 0]
        self.y2 = [0, 0]
        self.keh=[]



        self.gi = draw.Draw(self.root, self.root.graph_input, title="Исходный и восстановленный сигналы", label_horizontal="t", label_vertical="A")
        self.gi.pen([(255, 0, 0), (0, 0, 255)], [2, 2])
        self.gi.create_data(self.x, [self.y, self.y2])

        self.gimp = draw.Draw(self.root, self.root.graph_impulse, title="Импульсная характеристика", label_horizontal="t", label_vertical="h")
        self.gimp.pen((255, 0, 0), 2)
        self.gimp.create_data(self.x, self.y)

        self.go = draw.Draw(self.root, self.root.graph_output, title="Выходной сигнал", label_horizontal="t", label_vertical="h")
        self.go.pen((255, 0, 0), 2)
        self.go.create_data(self.x, self.y)


        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot_data)



        self.root.show()

    def update_plot_data(self):
        self.gi.update_data(self.t_arr, [self.input_arr, signal.xr])
        if self.keh==signal.xr:
            self.timer.stop()
        else:
            self.keh=signal.xr
        #print(signal.xr)

    def execute(self):
        self.N = int(self.root.edit_N.text())
        self.fd = float(self.root.edit_fd.text())
        self.A1 = float(self.root.edit_A1.text())
        self.n1 = float(self.root.edit_n1.text())
        self.q1 = float(self.root.edit_q1.text())
        self.A2 = float(self.root.edit_A2.text())
        self.n2 = float(self.root.edit_n2.text())
        self.q2 = float(self.root.edit_q2.text())
        self.A3 = float(self.root.edit_A3.text())
        self.n3 = float(self.root.edit_n3.text())
        self.q3 = float(self.root.edit_q3.text())
        self.An = float(self.root.edit_An.text())
        self.qn = float(self.root.edit_qn.text())
        self.a = int(self.root.shym.text())/1000

        self.init_value = float(self.root.edit_x0.text())
        self.step = float(self.root.edit_delta_x.text())

        self.l = [self.init_value] * self.N

        self.t_arr = [i/self.fd for i in range(self.N)]

        self.input_arr = self.signal.noise(self.signal.create_gauss(self.N, self.fd, A=[self.A1, self.A2, self.A3], q=[self.q1, self.q2, self.q3],
                                        n=[self.n1, self.n2, self.n3], count=3),self.a)#Гаусовые купола

        self.x = [i for i in range(self.N)]

        self.impulse_arr = self.signal.create_impulse(self.N, self.fd, A=[self.An], q=[self.qn], n=[0])#Импульсная характеристика

        self.output_arr = (self.signal.convolution(self.input_arr, self.impulse_arr))
        self.gimp.update_data(self.t_arr, self.impulse_arr)#Вывод импульсной характеристики
        self.go.update_data(self.t_arr, self.output_arr)#Вывод выходного сигнала


        self.thread = Worker(self.l, self.output_arr, self.impulse_arr, self.N, self.step, self.input_arr, self.root)# забываем про входной сигнал, остается только импульсная характеристика и выходной
        self.thread.start()
        self.timer.start()
        #self.gi.update_data(self.t_arr, self.input_arr)



        # self.signal.deconvolution(self.l, self.output_arr, self.impulse_arr, self.N, self.step)

        # x_energy_delta = 0
        # for val1, val2 in zip(self.input_arr, signal.xr):
        #     x_energy_delta += (val1-val2)**2
        #
        # print(x_energy_delta)
        #
        # self.gir.update_values([i for i in range(len(self.impulse_arr))], [self.impulse_arr], ["#123EAB"])
        # self.go.update_values([i for i in range(len(self.output_arr))], [self.output_arr], ["#123EAB"])
        # self.gi.update_values([i for i in range(len(self.input_arr))], [self.input_arr, self.xr], ["#123EAB", "#A30008"])


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    window = App(template_filename="template.ui")
    sys.exit(app.exec_())
