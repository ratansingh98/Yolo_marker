import sys,csv,os
from PyQt5 import QtCore, QtGui, QtWidgets
from gui import Ui_MainWindow
import glob
import os.path
import cv2

roi_list = []
if os.path.exists("roi.csv"):
	with open('roi.csv','r')as f:
		data = csv.reader(f)
		for row in data:
			roi_list.append(row)

def clear_roi():
	del roi_list[:]	
main_var = ''
filename = ''
label_data =0
label_list = None
class MyWidget(QtWidgets.QWidget):

	def __init__(self):
		super().__init__()
		self.rect_state=1
		self.rect_list = []
		self.rect_list1 = []
		self.ret= True
		self.setGeometry(30,30,200,200)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		#sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
		self.setSizePolicy(sizePolicy)

		self.begin = QtCore.QPoint()
		self.end = QtCore.QPoint()
		self.show()
		self.paintEvent(self)

		global roi_list
		global filename
	    

	def load_prev_box(self,qp):
		global label_list
		for brc in roi_list:
			qp.drawRect(QtCore.QRect(QtCore.QPoint(int(brc[0]),int(brc[1])),QtCore.QPoint(int(brc[2]), int(brc[3]))))
			qp.setPen(QtGui.QPen(QtCore.Qt.red))
			try:
				qp.drawText(QtCore.QPoint(int(brc[0]),int(brc[1])), label_list[brc[4]])
			except:
				QtWidgets.QMessageBox.about(self, "Alert", "Please load names file")

		qp.end()
		

	def clear_boxes(self):
		self.rect_state=0
		self.rect_list = []
		self.rect_list1 = []
		global filename

		# opening the file with w+ mode truncates the file
		os.remove(filename)
		f = open(filename, "w+")
		f.close()
		roi_list = []
		clear_roi()
		#print("cleared")
	    

	def paintEvent(self, event):
		qp = QtGui.QPainter(self)
		#print('painting')
		#painter = QPainter(self)

		try:
			qp.drawPixmap(self.rect(), main_var)
	        

		except Exception as e:
			print(e,'**************',type(main_var))

		if self.rect_state ==1:
				#print('----------------------',self.rect_list,type(self.rect_list),len(self.rect_list))
			br = QtGui.QBrush(QtGui.QColor(255, 0, 0, 30))
			#qp.setPen(Qt.NoPen);
			qp.setBrush(br)
			for brc in range(0,len(self.rect_list) ):
				qp.drawRect(QtCore.QRect( self.rect_list[brc], self.rect_list1[brc] ))
			if self.ret:
				self.load_prev_box(qp)
				#self.ret = False

		#        br1 = QtGui.QBrush(QtGui.QColor(100, 10, 10, 40))
		#        qp.setBrush(br1)
		#        qp.drawRect(QtCore.QRect(self.begin-QtCore.QPoint(10, 10), self.end-QtCore.QPoint(10, 10)))
		qp.end()

	def mousePressEvent(self, event):
		self.begin = event.pos()
		#print(self.begin)

	def mouseMoveEvent(self, event):
		pass

	def mouseReleaseEvent(self, event):
		global label_data
		self.end = event.pos()
		self.rect_list.append(self.begin)
		self.rect_list1.append(self.end)
		self.rect_state =1
		roi_list_temp =list(map(str,str(self.rect_list[-1])[20:-1].split(",")))+list(map(str,str(self.rect_list1[-1])[20:-1].split(",")))
		# Add label to box
		roi_list_temp.append(label_data)
		roi_list.append(roi_list_temp)
		global filename
		print(filename)
		with open('{}'.format(filename), 'a+') as writeFile:
			writer = csv.writer(writeFile)
			writer.writerows([roi_list_temp])
		self.update()

class MainWindow_exec(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		QtWidgets.QMainWindow.__init__(self, parent)
		self.u = 0
		self.v = 0
		self.res= []
		#print(roi_list)
		self.setupUi(self)
		print("*"*40,self.image_view.height(),self.image_view.width())
		self.gridLayout_4.removeWidget(self.image_view)
		self.image_view.close()
		self.image_view = MyWidget()
		self.image_view.setStyleSheet("border: 10px solid black;")
		self.gridLayout_4.addWidget(self.image_view,1,1,1,1)

		self.image_view.setMinimumSize(200,200)
		self.img_browse.clicked.connect(self.getImagefolder)
		self.annotation_browse.clicked.connect(self.getAnnotationfolder)
		self.prev_btn.clicked.connect(self.prevImage)
		self.next_btn.clicked.connect(self.nextImage)
		self.names_browse.clicked.connect(self.browseName)
		self.names_table.cellClicked.connect(self.selectedLabel)
		self.counter =0
		self.image_list = None
		self.annotation_list  =None
		self.Dname = None
		self.label_data = []

	def selectedLabel(self,row, column):
		global label_data,label_list
		label_data = row
		label_list = self.label_data

	def prevImage(self):
		if self.counter >=0:
			if self.counter !=0:
				self.counter -=1
			currIamge=self.image_list[self.counter]
			pix = QtGui.QPixmap(str(currIamge))
			global main_var 
			annotationName = self.Dname+"/"+str(currIamge.split(".")[-2].split("/")[-1])+".txt"
			self.load_Annotation(annotationName)
			main_var = pix
			self.image_view.update()
			self.label_index.setText("{}/{}".format(self.counter,len(self.image_list)-1))
			

	def nextImage(self):
		if self.counter < len(self.image_list)-1:
			self.counter +=1
			currIamge=self.image_list[self.counter]
			pix = QtGui.QPixmap(str(currIamge))
			global main_var 
			annotationName = self.Dname+"/"+str(currIamge.split(".")[-2].split("/")[-1])+".txt"
			self.load_Annotation(annotationName)
			main_var = pix
			self.image_view.update()
			self.label_index.setText("{}/{}".format(self.counter,len(self.image_list)-1))


	def getImagefolder(self):
		self.Dname = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory')
		self.label_4.setText(self.Dname)
		self.image_list = [item for i in [glob.glob('{}/*.{}'.format(self.Dname,ext)) for ext in ["jpg","gif","png","tga"]] for item in i]
		self.counter =0
		pix = QtGui.QPixmap(str(self.image_list[self.counter]))
		global main_var 
		main_var = pix
		self.image_view.update()
		self.label_index.setText("{}/{}".format(self.counter,len(self.image_list)-1))
		

	def getAnnotationfolder(self):
		self.Dname = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory',"")
		if len(self.label_data) == 0:
			QtWidgets.QMessageBox.about(self, "Alert", "Please load names file")
		if self.Dname == "":
			return
		self.label_5.setText(self.Dname)
		self.annotation_list = glob.glob('{}/*.txt'.format(self.Dname))
		annotationName = self.Dname+"/"+str(self.image_list[self.counter].split(".")[-2].split("/")[-1])+".txt"
		self.load_Annotation(annotationName)


	def load_Annotation(self,annotationName):
		global filename
		global roi_list
		load_roi = []
		roi_list =[]
		self.image_view.rect_list =[]
		self.image_view.rect_list1 =[]
		if os.path.isfile(annotationName):
			filename = annotationName
			with open(filename) as fp:
				line = fp.readline()
				while line:
					load_roi.append([i for  i in map(int,line.strip().split(","))])
					line = fp.readline()
			roi_list = load_roi
			self.image_view.update()
		else:
			filename = annotationName
			self.image_view.update()

	def browseName(self):		
		filename = QtWidgets.QFileDialog.getOpenFileNames(self, "Select File", "", "*.names")[0][0]
		self.label_data = []
		with open(filename) as fp:
			line = fp.readline()
			while line:
				self.res.append(line.strip())
				line = fp.readline()
			self.names_table.setRowCount(0)
			self.names_table.setColumnCount(1)
			for row_number, row_data in enumerate(self.res):
				self.names_table.insertRow(row_number)
				item = QtWidgets.QTableWidgetItem(str(row_data))
				self.label_data.append(str(row_data))
				self.names_table.setItem(row_number,0, item)
				self.names_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
				self.names_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
				header = self.names_table.horizontalHeader()        
				stylesheet = "::section{Background-color:rgb(43,59,88);color:rgb(255,255,255);font-size:18px;font-weight: bold   }"
				header.setStyleSheet(stylesheet)
				header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
				self.products_header= ['Labels']
				self.names_table.setHorizontalHeaderLabels(self.products_header)
		#        self.names_table.hideColumn(0)
				self.names_table.verticalHeader().setDefaultSectionSize(50)
				self.names_table.verticalHeader().hide()
				self.names_table.setStyleSheet('font-size:18px')
		global label_data,label_list
		label_data = 0
		label_list = self.label_data



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindow_exec()
    MainWindow.showMaximized()
    sys.exit(app.exec_())