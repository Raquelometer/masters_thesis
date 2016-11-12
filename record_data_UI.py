import sys
import redis

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import *


class App(QWidget):
	def __init__(self, redis_client):
		self.redis_client = redis_client
		super(QWidget, self).__init__()
		self.initUI()

	def initUI(self):
		self.setWindowTitle('Data Recorder')

		startBtn = QPushButton('Start', self)
		stopBtn = QPushButton('Stop', self)

		stopBtn.move(80,0)

		startBtn.clicked.connect(self.on_click_Start)
		stopBtn.clicked.connect(self.on_click_Stop)

		self.show()

	@pyqtSlot()
	def on_click_Start(self):
		print('start')
		self.redis_client.rpush('sensor', 'START')
	def on_click_Stop(self):
		print('stop')
		self.redis_client.rpush('sensor', 'STOP')


if __name__ == '__main__':
	redis_client = redis.StrictRedis(host='localhost', port=6379)
	app = QApplication(sys.argv)

	ex = App(redis_client)
	sys.exit(app.exec_())

"""

app = QApplication(sys.argv)
w = QWidget()
w.setWindowTitle('Stop and start')

btn = QPushButton('Stop', w)
btn2 = QPushButton('Start', w)

btn.move(0, 30)

@pyqtSlot()
def on_click_Stop():
	print('clicked')
def on_click_Start():
	print('start')

btn.clicked.connect(on_click_Stop)
btn2.clicked.connect(on_click_Start)

w.show()
app.exec_()
"""