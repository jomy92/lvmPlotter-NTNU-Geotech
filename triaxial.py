# TODO: Handle extension tests as well! Currently just for compression.

from PyQt4.uic import loadUiType
from PyQt4 import QtGui, QtCore

from readLVM import readLVM
import numpy as np

import os

from matplotlib.transforms import Bbox
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
    
Ui_MainWindow, QMainWindow = loadUiType("triaxial.ui")
Ui_PopupWindow, QPopupWindow = loadUiType("popupWindow.ui")
Ui_SelectGraphWindow, QSelectGraphWindow = loadUiType("selectgraph.ui")

class TRIAXIAL(QMainWindow, Ui_MainWindow):
    def __init__(self, filePaths):
        super(TRIAXIAL, self).__init__()
        
        # Creates some custom startup graphs
        self.data = []
        for id, file in enumerate(filePaths):
            fileData = readLVM(file)
            self.interpret_Data(fileData)
        
        self.setupUi(self)
        self.create_Canvas() 
        self.setup_Table(filePaths)

       
        # Event Listeners
        for i in range(len(self.listOfBtn)):
            self.listOfBtn[i][0].clicked.connect(lambda: self.header_Info(i))
            self.listOfBtn[i][1].clicked.connect(lambda: self.calib_Info(i))
            self.listOfBtn[i][2].clicked.connect(lambda: self.determine_Su(i))
        
        self.tableWidget.itemChanged.connect(self.changeVisible_State)
        
        # TODO: Implement more functions later
        # # Button panel
        # self.btnChangeGraph.clicked.connect(self.change_Graph)
        # self.btnExtraGraph.clicked.connect(self.extra_Graph)
        # self.btnFailureLine.clicked.connect(self.failure_line)
        # self.btnK0Line.clicked.connect(self.k0_line)
        # self.btnSaveCSV.clicked.connect(self.save_CSV)



    def setup_Table(self, filePaths):
        
        # -*- coding: utf8 -*-
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Label", "Date", "Depth", "Comment", "Header Info", "Calibration Data", "Su [kPa]", "Strain Rate [%]", u"ΔV [cm³]", u"εᵥ [%]", u"Δe/e₀  [-]"]) # Maybe find a way to use tex interpreter instead?
        
        self.tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSortingEnabled(True) 
        self.tableWidget.setColumnHidden(0, True) # To keep track of data when sorted
        self.tableWidget.setColumnHidden(7, True) # TODO: Su analysis not implmented
                
        self.listOfBtn = []
        for i in range(len(filePaths)):
            self.fill_Infotable(self.data[i], i)
       
        
    # Adds drawing area to figure
    def create_Canvas(self): 
        self.fig = Figure()
                
        self.canvas = FigureCanvas(self.fig)
        
        self.toolbar = CustomToolbar(self.canvas, self)
        self.widgetGrid.addWidget(self.toolbar)
        self.widgetGrid.addWidget(self.canvas)
        
        self.default_Plot()
    
    def default_Plot(self):
        # Layout and numbering of subplots
                # 1 - 2 - 3 #
                # 4 - 5 - 6 #
        if not self.fig.axes:
            ax = self.fig.add_subplot(231)
            self.plot_Consolid1(self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(234)
            self.plot_Consolid2(self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(232)
            self.plot_pq       (self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(235)
            self.plot_NTH      (self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(233)
            self.plot_shearStrain(self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(236)
            self.plot_porePress  (self.fig, self.canvas, ax)
                
            ax.plot([0.33, 0.33], [0, 1], color='black', lw=1, transform=self.fig.transFigure, clip_on=False)
            self.fig.tight_layout()
        
        
                # 1 - 2 - 3 - 4 #
                # 5 - 6 - 7 - 8 #
        else:
            ax = self.fig.add_subplot(241)
            self.plot_Consolid1(self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(245)
            self.plot_Consolid2(self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(242)
            self.plot_pq       (self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(246)
            self.plot_NTH      (self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(243)
            self.plot_shearStrain(self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(247)
            self.plot_porePress  (self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(244)
            self.plot_porePress  (self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(248)
            self.plot_porePress  (self.fig, self.canvas, ax)
            
            ax.plot([0.25, 0.25], [0, 1], color='black', lw=1, transform=self.fig.transFigure, clip_on=False)
            ax.plot([0.75, 0.75], [0, 1], color='black', lw=1, transform=self.fig.transFigure, clip_on=False)
            self.fig.tight_layout()
        # # # self.plot_voidCSL(self.fig_4, self.canvas_4) Not found good solution
        # # # #self.plot(self.fig_7, self.canvas_7)
        # # # #self.plot(self.fig_8, self.canvas_8)
    
    
    
    def plot_Consolid1(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['consolidationData']['sqrtTime']
            dataY = self.data[i]['consolidationData']['deltaVolume']
            ax.plot(dataX, dataY)   
        ax.set_title('Consolidation')
        ax.set_xlabel('$\sqrt{t}\quad [s^{0.5}]$')
        ax.set_ylabel('$\Delta{V}\quad [cm^3]$')
        ax.grid(True)
        
        yLimits = ax.get_ylim()
        ax.set_ylim(0, yLimits[1])
        ax.invert_yaxis()
    
        canvas.draw()
        
    def plot_Consolid2(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['consolidationData']['epsAcons']*100 
            dataY = self.data[i]['consolidationData']['excessPoreCons']
            ax.plot(dataX, dataY)    
        ax.set_xlabel('$\epsilon_a$ [%]')
        ax.set_ylabel('$P_{excess}$ [kPa]')
        ax.grid(True)
        canvas.draw()
    
    def plot_pq(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['stress']['pStress']
            dataY = self.data[i]['stress']['qStress']
            ax.plot(dataX, dataY)                           
        ax.set_xlabel("p' [kPa]")
        ax.set_ylabel('q [kPa]')
        ax.grid(True)
        
        xLimits = ax.get_xlim()
        ax.set_xlim([-10,xLimits[1]])
        
        canvas.draw()
        
    def plot_MIT(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['stress']['mStress']
            dataY = self.data[i]['stress']['tStress']
            ax.plot(dataX, dataY)                           
        ax.set_xlabel("p' [kPa]")
        ax.set_ylabel('q [kPa]')
        ax.grid(True)
        
        xLimits = ax.get_xlim()
        ax.set_xlim([0,xLimits[1]])
        
        canvas.draw()
        
    def plot_sig1_sig3(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['stress']['effSigmaR']
            dataY = self.data[i]['stress']['effSigmaA']
            ax.plot(dataX, dataY)                           
        ax.set_xlabel('$\sigma_3$ [kPa]')
        ax.set_ylabel('$\sigma_1$ [kPa]')
        ax.grid(True)
        
        xLimits = ax.get_xlim()
        ax.set_xlim(-10, xLimits[1])
        
        canvas.draw()
    
    def plot_NTH(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['stress']['effSigmaR']
            dataY = self.data[i]['stress']['tStress']
            ax.plot(dataX, dataY)                           
        ax.set_xlabel('$\sigma_3$ [kPa]')
        ax.set_ylabel(r'$\tau$ [kPa]')
        ax.grid(True)
        
        xLimits = ax.get_xlim()
        ax.set_xlim(-10, xLimits[1])
        
        canvas.draw()
        
    def plot_shearStrain(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['epsilonA']*100
            dataY = self.data[i]['stress']['qStress']
            ax.plot(dataX, dataY)                           
        ax.set_xlabel('$\epsilon_a$ [%]')
        ax.set_ylabel('q [kPa]')
        ax.grid(True)
        canvas.draw()
    
    # def plot_voidCSL(self, fig, canvas):
    #     for i in range(len(self.data)):
    #         dataX = (self.data[i]['stress']['pStress']
    #         dataY = self.data[i]['voidRatio']
    #         ax = fig.add_subplot(111)
    #         ax.plot(dataX, dataY)                           
    #     canvas.draw()
    
    
    def plot_porePress(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX =  self.data[i]['epsilonA']*100
            dataY =  self.data[i]['excessPore']
            ax.plot(dataX, dataY)                           
        ax.set_xlabel('$\epsilon_a$ [%]')
        ax.set_ylabel('$P_{excess}$ [kPa]')
        ax.grid(True)
        canvas.draw()
        
    
    
    def interpret_Data(self, fileData):
        # Label & date
        fileInfo = {'label':fileData[0][0], 'date':fileData[0][1]}
        
        #Header
        if len(fileData[1]) > 7:
            header = {'test':fileData[1][2][1], 'depth':float(fileData[1][5][1]), 'height':float(fileData[1][6][1]), 'diameter':float(fileData[1][7][1]),'comment':fileData[1][8][1]} 
            headerAll = fileData[1] # For infoBox
        else:
            header = {'depth':float(fileData[1][3][1]), 'height':float(fileData[1][4][1]), 'diameter':float(fileData[1][5][1]),'comment':fileData[1][6][1]} 
            headerAll = fileData[1] # For infoBox
        
        #Calibration data
        calibData = fileData[2]
        
        # Time & modechange
        time = fileData[4]
        mode = fileData[5]
        
        # Determine location of consolidation and shear phase
        pointer = []
        counter = 0
        for id in mode:
            if id.split(' ')[0] == 'CONS':
                pointer.append(int(id.split(' ')[1]))
            elif id.split(' ')[0] == 'SHEAR' or id.split(' ')[0] == 'CSR':
                pointer.append(int(id.split(' ')[1]))
            elif 'ZERO ' in id:
                row = int(id.split(' ')[1])-counter
                x = fileData[6]
                x = np.delete(x, row, 0)
                fileData[6] = x
                counter += 1

        # Force, stresses and deformation data       
        if len(fileData[6][1]) < 14:
            measuredData = {'deform':fileData[6][:,4], 'force':fileData[6][:,5], 'cellPr':
            fileData[6][:,6],'porePr':fileData[6][:,7], 'water':fileData[6][:,8]}
        else:
            porePr = fileData[6][:,10] - fileData[6][:,9]
            measuredData = {'deform':fileData[6][:,7], 'force':fileData[6][:,8], 'porePr': porePr, 'effCellPr':fileData[6][:,9], 'cellPr':
            fileData[6][:,10], 'water':fileData[6][:,12]}


        # Consolidation data
        sqrtTime        = np.sqrt(time[pointer[0]:pointer[1]-1])        #[s^0.5]
        excessPoreCons  = measuredData['porePr'][pointer[0]:pointer[1]-1]   #[kPa]
        deltaVolume     = measuredData['water'][pointer[0]:pointer[1]-1]    #[cm^3]
        
        initArea   = np.pi/(4*100)*header['diameter']*header['diameter'] #[cm^2]
        initVolume = initArea*header['height']/10                        #[cm^3]
        
        epsVol = deltaVolume[-1]/initVolume
        Acons  = initArea*(1-epsVol)/(1-epsVol/3)
        
        strain      = measuredData['deform']/header['height']
        epsAcons    = strain[pointer[0]:pointer[1]-1]
        
        consolidationData = {'sqrtTime':sqrtTime, 'excessPoreCons':excessPoreCons, 'deltaVolume':deltaVolume, 'epsAcons': epsAcons, 'epsVol':epsVol}
        
        # Shear data
        # Stress - [kPa]
        if len(fileData[6][1]) < 14:
            vertStress  = measuredData['force']*(1-strain)/(Acons)*10 + measuredData['cellPr']
            effSigmaR   = measuredData['cellPr'] - measuredData['porePr']
            effSigmaA   = vertStress - measuredData['porePr']  
            #voidRatio   = measuredData['water'][pointer[1]:]/(initVolume-measuredData['water'][pointer[1]:]) # NOTE: WRONG!
            #Only keep shear data
        else:
            vertStress  = measuredData['force']*(1-strain)/(Acons)*10 + measuredData['cellPr']
            effSigmaR   = measuredData['effCellPr']
            effSigmaA   = vertStress - measuredData['porePr']
            
        epsilonA    = strain[pointer[1]:]
        effSigmaR   = effSigmaR[pointer[1]:]
        effSigmaA   = effSigmaA[pointer[1]:]
        excessPore  = measuredData['porePr'][pointer[1]:]
        
        pStress     = (effSigmaA + effSigmaR*2)/3
        mStress     = (effSigmaA + effSigmaR)/2
        qStress     =  effSigmaA - effSigmaR
        tStress     =  qStress/2
    
        
        stress = {'effSigmaA':effSigmaA, 'effSigmaR':effSigmaR, 'pStress':pStress,'qStress':qStress,'mStress':mStress, 'tStress':tStress}
    
        # Store relevant data
        self.data.append({'fileInfo':fileInfo, 'header':header, 'headerAll':headerAll, 'calibData':calibData, 'time':time, 'mode':mode, 'fileData':fileData, 'consolidationData': consolidationData, 'epsilonA':epsilonA, 'stress':stress, 'excessPore':excessPore}) 



    
    def fill_Infotable(self, data, i):
        # Fill table data content
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        
        item = QtGui.QTableWidgetItem(str(i))
        self.tableWidget.setItem(i,0,item)
        
        item = QtGui.QTableWidgetItem(data['fileInfo']['label'])
        item.setCheckState(QtCore.Qt.Checked)
        self.tableWidget.setItem(i,1,item)
        
        item = QtGui.QTableWidgetItem(data['fileInfo']['date'])
        item.setTextAlignment(QtCore.Qt.AlignCenter);
        self.tableWidget.setItem(i,2,item)
        
        item = QtGui.QTableWidgetItem( str( data['header']['depth']) + ' m')
        item.setTextAlignment(QtCore.Qt.AlignCenter);
        self.tableWidget.setItem(i,3,item)
        
        item = QtGui.QTableWidgetItem(data['header']['comment'])
        self.tableWidget.setItem(i,4,item)
        
        item = QtGui.QTableWidgetItem('NaN')
        item.setTextAlignment(QtCore.Qt.AlignCenter);
        self.tableWidget.setItem(i,8,item)
        
        volume = data['consolidationData']['deltaVolume'][-1]
        item = QtGui.QTableWidgetItem("%.2f" % volume)
        item.setTextAlignment(QtCore.Qt.AlignCenter);
        self.tableWidget.setItem(i,9,item)
        
        epsVol = data['consolidationData']['epsVol']*100
        item = QtGui.QTableWidgetItem("%.2f" % epsVol)
        item.setTextAlignment(QtCore.Qt.AlignCenter);
        self.tableWidget.setItem(i,10,item)
        
        item = QtGui.QTableWidgetItem('NaN')
        item.setTextAlignment(QtCore.Qt.AlignCenter);
        self.tableWidget.setItem(i,11,item)
        
        # create buttons in cells - One for each data -- Need Indexing!
        btnHeaderInfo  = QtGui.QPushButton(self.tableWidget)
        btnCalibInfo   = QtGui.QPushButton(self.tableWidget)
        btnDetermineSu = QtGui.QPushButton(self.tableWidget)
        
        
        self.listOfBtn.append([btnHeaderInfo,btnCalibInfo,btnDetermineSu])
        
        btnHeaderInfo.setText('Info')
        btnCalibInfo.setText('Info')
        btnDetermineSu.setText('Determine Su')
        
        self.tableWidget.setCellWidget(i, 5, btnHeaderInfo)
        self.tableWidget.setCellWidget(i, 6, btnCalibInfo)
        self.tableWidget.setCellWidget(i, 7, btnDetermineSu)
        
        
        
    def changeVisible_State(self, item):
        state = item.checkState()
        row   = item.row()
        actualRow = int(self.tableWidget.item(row,0).text()) # In case of sorting
        if state == 0:
            for ax in self.fig.axes:
                ax.lines[actualRow].set_visible(False)
                ax.relim(visible_only=True)
                ax.autoscale_view()
                self.canvas.draw()
        else:
            for ax in self.fig.axes:
                ax.lines[actualRow].set_visible(True)
                ax.relim(visible_only=True)
                ax.autoscale_view()
                self.canvas.draw()
          
    def header_Info(self, index):
        button = QtGui.qApp.focusWidget() # or button = self.sender()
        index = self.tableWidget.indexAt(button.pos())
        row = index.row()
        actualRow = int(self.tableWidget.item(row,0).text()) # In case of sorting
        
        string = []
        for i in range(len(self.data[actualRow]['headerAll'])):
            string.append(": ".join(self.data[actualRow]['headerAll'][i]))
        string = " \n ".join(string)
        
        self.infoWindow = PopupWindow(string)
        self.infoWindow.show()      

    
    def calib_Info(self, index):
        button = QtGui.qApp.focusWidget() # or button = self.sender()
        index = self.tableWidget.indexAt(button.pos())
        row = index.row()
        actualRow = int(self.tableWidget.item(row,0).text()) # In case of sorting
        
        string = []
        for i in range(len(self.data[actualRow]['calibData'])):
            string.append(": ".join(self.data[actualRow]['calibData'][i]))
        string = " \n ".join(string)
        
        self.infoWindow = PopupWindow(string)
        
        self.infoWindow.show()      
    
    # TODO: Not implmented
    def determine_Su(self, index):
        button = QtGui.qApp.focusWidget() # or button = self.sender()
        index = self.tableWidget.indexAt(button.pos())
        row = index.row()
        actualRow = int(self.tableWidget.item(row,0).text()) # In case of sorting
        
        print('Do something with Su', row)

    # TODO: Currently not implmented
    # def change_Graph(self):
    #     print('Change graph')
    #     
    # def extra_Graph(self):
    #     print('Extra graph')

   ##   def failure_line(self):
    #     self.infoWindow = SelectGraphBox()
    #     self.infoWindow.show()   
    #     
    #     self.infoWindow
    #     print('Failure line')

   ##   def k0_line(self):
    #     print('K0 line')
    #     
    # def save_CSV(self):
    #     print('Save CSV')
        


class CustomToolbar(NavigationToolbar):
# Suggestion for improvement: Make function to determine extent of subplot
    def __init__(self,canvas_,parent_):
        #   | Code name | Hover text | Image | Function |
        self.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to  previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            (None, None, None, None),
            ('SaveSub', 'Save the subplot', 'filesave', 'save_subplot'),
            ('SaveFig', 'Save the figure', 'filesave', 'save_figure'),
            (None, None, None, None),
            )
          
        # How to remove buttons
        #self.toolitems = [t for t in NavigationToolbar.toolitems if t[0] in ('Home', 'Pan', 'Zoom', 'Save')]
        NavigationToolbar.__init__(self,canvas_,parent_)
    
        
    def save_subplot(self):
        if self._active == 'SUBPLOT':
            self._active = None
        else:
            self._active = 'SUBPLOT'
            
        if self._active:
            self.cid1 = self.canvas.mpl_connect('axes_enter_event', self.on_Hover)       
            self.cid2 = self.canvas.mpl_connect('button_press_event', self.on_click)
            self.cid3 = self.canvas.mpl_connect('figure_leave_event', self.outsideSubplot)    
            self.mode = 'Save subplot'
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)
    
    def on_Hover(self, event): # Based on code by Joe Kington
        fig     = event.canvas.figure
        ax      = event.inaxes
        canvas  = event.canvas
        
        pad = 0.0
        
        canvas.draw()
        
        items = ax.get_xticklabels() + ax.get_yticklabels() 
        items += [ax, ax.title, ax.xaxis.label, ax.yaxis.label]
        bbox = Bbox.union([item.get_window_extent() for item in items])
        
        extent = bbox.expanded(1.0 + pad, 1.0 + pad)
        extent = extent.transformed(canvas.figure.transFigure.inverted())
        
        self.extent = extent.transformed(fig.dpi_scale_trans.inverted())
        
        
        rect = Rectangle([extent.xmin, extent.ymin], extent.width, extent.height, facecolor='yellow', edgecolor='none', zorder=-1, transform=fig.transFigure) 
        fig.patches.append(rect)
        
        canvas.draw()
        self.canvas.mpl_connect('axes_leave_event', self.outsideSubplot)
    
    def on_click(self, event):
        if event.inaxes is not None:
            try:
                fileName  = QtGui.QFileDialog.getSaveFileName(self, 'Save file', 'c:\\', "Images (*.png)")
                fileName = os.path.normpath(fileName)
                self.disconnectAll()
                
                fig     = event.canvas.figure
                ax      = event.inaxes
                canvas  = event.canvas
                
                pad = 0.0
                
                canvas.draw()
                
                items = ax.get_xticklabels() + ax.get_yticklabels() 
                items += [ax, ax.title, ax.xaxis.label, ax.yaxis.label]
                bbox = Bbox.union([item.get_window_extent() for item in items])
                
                extent = bbox.expanded(1.0 + pad, 1.0 + pad)
                extent = extent.transformed(fig.dpi_scale_trans.inverted())

                event.canvas.figure.savefig(fileName, bbox_inches=extent)
            
            except:
                self.disconnectAll()
        
    def disconnectAll(self):
        self.canvas.mpl_disconnect(self.cid1)
        self.canvas.mpl_disconnect(self.cid2)
        self.canvas.mpl_disconnect(self.cid3)
        self.mode = ''
        
        
    def outsideSubplot(self, event ):
        try:
            event.canvas.figure.patches.pop()
            event.canvas.draw()
        except:
            pass
        

# TODO: Planned to be used with button panel
# class SelectGraphBox(QSelectGraphWindow, Ui_SelectGraphWindow):
#     def __init__(self):
#         super(QSelectGraphWindow, self).__init__()
#         
#         self.setupUi(self)
# 
#         self.btn_PQ.clicked.connect(self.Plot_PQ)
#         # self.btn_MIT.clicked.connect(self.Plot_)
#         # self.btn_NTH.clicked.connect(self.Plot_NTH)
#         # self.btn_Princip.clicked.connect(self.Plot_Princip)
#          
#     def Plot_PQ(self):
#         self.value=1
#         
#         return self.value
#         self.close()
                    

class PopupWindow(QPopupWindow, Ui_PopupWindow):
    def __init__(self, string):
        super(PopupWindow, self).__init__()
        
        self.setupUi(self)
        self.setWindowTitle("Additional Info")
        
        self.textBox.setAlignment(QtCore.Qt.AlignCenter)
        self.textBox.setText(string)
        self.textBox.setWordWrap(True)
        
        self.btnClose.clicked.connect(self.btn_Close)
        
    def btn_Close(self):
        self.close()
        
    
if __name__ == "__main__":
    import sys
    from PyQt4 import QtGui
    import numpy as np
    
    # # For testing
    filey = [".\\Raw files\\triaxial.lvm", ".\\Raw files\\G1-2_CIUc_D8-30m.lvm" ]

    app = QtGui.QApplication(sys.argv)
    main = TRIAXIAL(filey)
    main.show()
    sys.exit(app.exec_())
    
    