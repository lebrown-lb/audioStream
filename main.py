# Print out realtime audio volume as ascii bars
import pyqtgraph as pg

import sounddevice as sd
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

CHUNK = 4096


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.plot_graph = pg.PlotWidget()
        self.counter = 0

        layout0 = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()

        self.lbl = QLabel("Start")
        self.b0 = QPushButton("Record")
        self.b0.pressed.connect(self.record_run)
        self.b1 = QPushButton("START")
        self.b1.pressed.connect(self.start_stop)
        self.b2 = QPushButton("PLAYBACK")
        self.b2.pressed.connect(self.playback)
        self.b3 = QPushButton("SAVE")
        self.b3.pressed.connect(self.save_file)
        self.b4 = QPushButton("LOAD")
        self.b4.pressed.connect(self.load_file)

        self.lbl0 = QLabel("Device:")
        self.cb0 = QComboBox()
        self.cb0.currentIndexChanged.connect(self.device_change)
        layout3.addWidget(self.lbl0)
        layout3.addWidget(self.cb0)




        self.sp = QSlider(Qt.Horizontal)
        self.sp.setMaximum(50)
        self.sp.setMinimum(1)

        layout0.addWidget(self.lbl)
        layout1.addWidget(self.b0)
        layout1.addWidget(self.b1)
        layout1.addWidget(self.b2)
        layout0.addLayout(layout1)
        layout0.addLayout(layout3)
        layout0.addWidget(self.plot_graph)
        layout2.addWidget(self.b3)
        layout2.addWidget(self.b4)
        layout0.addLayout(layout2)
        layout0.addWidget(self.sp)

        w = QWidget()
        w.setLayout(layout0)
        self.setCentralWidget(w)
        self.show()
        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.recurring_timer)
        #self.stream = sd.Stream(samplerate=44100, channels=1, device=5, blocksize=CHUNK)
        self.stream = None
        #self.stream.start()
        self.ydata = np.array(0)
        self.xdata = np.array(0)
        self.plot_graph.setYRange(-0.8, 0.8)
        self.plot_graph.showGrid(True, True)
        self.record = 0
        self.run = 0

        self.dl = []
        for x in sd.query_devices():
            if (x['max_input_channels'] >= 1) and (x['max_output_channels'] >= 1):
                self.dl.append(x)

        self.cb0.addItems([x['name'] for x in self.dl])
        self.device = self.dl[0]['index']


    def device_change(self):

        if self.stream:
            self.stream.stop()
        self.device = self.dl[self.cb0.currentIndex()]['index']
        self.stream = sd.Stream(samplerate=44100, channels=1, device=self.device, blocksize=CHUNK)
        self.stream.start()

    def save_file(self):
        filename = QFileDialog.getSaveFileName()
        print(filename)
        print(type(self.xdata[0]))
        file_obj2 = open(filename[0], mode='wb')
        self.ydata.tofile(file_obj2)
        file_obj2.close()

    def load_file(self):
        filename = QFileDialog.getOpenFileName()
        print(filename)
        file_obj2 = open(filename[0], mode='rb')
        self.ydata = np.fromfile(file_obj2, dtype=float)
        file_obj2.close()
        self.plot_graph.clear()
        self.xdata = np.arange(self.ydata.size) * 1 / 44100
        self.plot_graph.plot(self.xdata, self.ydata)
        self.b1.setText('START')
        self.run = 0
        self.timer.stop()

    def playback(self):
        sd.play(self.ydata * self.sp.value(), 44100, device=self.device)

    def record_run(self):
        if self.record:
            self.b0.setText('Record')
            self.record = 0
        else:
            self.b0.setText('Recording')
            self.record = 1

    def start_stop(self):
        if self.run:
            self.b1.setText('START')
            self.run = 0
            self.timer.stop()
        else:
            self.b1.setText('STOP')
            self.run = 1
            self.timer.start()

    def recurring_timer(self):
        self.counter += 1
        self.lbl.setText("Counter: %d" % self.counter)
        if not self.record:
            self.ydata = np.array(0)
        for i in range(2):
            indata, overflowed = self.stream.read(CHUNK)
            self.ydata = np.append(self.ydata, indata)
        self.xdata = np.arange(self.ydata.size) * 1/44100
        self.plot_graph.clear()
        self.plot_graph.plot(self.xdata, self.ydata)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec_()
