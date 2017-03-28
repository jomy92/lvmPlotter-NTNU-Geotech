from PyQt4.uic import loadUiType
from PyQt4 import QtGui, QtCore

from readLVM import readLVM
import numpy as np

from matplotlib.transforms import Bbox
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

from statsmodels.nonparametric.smoothers_lowess import lowess

Ui_MainWindow, QMainWindow = loadUiType("crs.ui")
Ui_PopupWindow, QPopupWindow = loadUiType("popupWindow.ui")

class CRS(QMainWindow, Ui_MainWindow):
    def __init__(self, filePaths):
        super(CRS, self).__init__()
        
        # Creates some custom startup graphs
        self.data = []
        for id, file in enumerate(filePaths):
            fileData = readLVM(file)
            self.interpret_Data(fileData)
        
        self.setupUi(self)
        self.create_Canvas() 
        self.setup_Table(filePaths)


        ## Implement more functions later
        # TODO: Implement pc determination (auto, or self)
        # TODO: Calculate Moc, mNC and Cvref = 100 ?
        # TODO: Calculate quality of test
        # TODO: Fitting of data (clip of some parts of data)
        # TODO: Give option to put in table values (unit weight, water content, in situ stress etc.)
        # TODO: Save data to CSV
        # TODO: Option to change graphs and order of graphs.
        
        # Event Listeners
        for i in range(len(self.listOfBtn)):
            self.listOfBtn[i][0].clicked.connect(lambda: self.header_Info(i))
            self.listOfBtn[i][1].clicked.connect(lambda: self.calib_Info(i))
            #self.listOfBtn[i][2].clicked.connect(lambda: self.determine_pc(i))
        
        self.tableWidget.itemChanged.connect(self.update_Plot)
        
        # # Button panel
        # self.btnChangeGraph.clicked.connect(self.change_Graph)
        # self.btnFailureLine.clicked.connect(self.module_line)
        # self.btnSaveCSV.clicked.connect(self.save_CSV)
        
    
    def setup_Table(self, filePaths):
        
        # -*- coding: utf8 -*-
        # TODO: Add column with strain rate
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Label", "Date", "Depth", "Enable Smooth", "Comment", "Header Data", "Calibration Info" ]) 
        # Maybe find a way to use tex interpreter instead?
        
        self.tableWidget.setSortingEnabled(True) 
        self.tableWidget.setColumnHidden(0, True) # To keep track of data when sorted
        
        self.listOfBtn = []
        for i in range(len(filePaths)):
            self.fill_Infotable(self.data[i], i)
    
    
    def create_Canvas(self): 
        self.fig = Figure()
                
        self.canvas = FigureCanvas(self.fig)
        
        self.toolbar = CustomToolbar(self.canvas, self)
        self.widgetGrid.addWidget(self.toolbar)
        self.widgetGrid.addWidget(self.canvas)
        
        self.default_Plot()


    def default_Plot(self):
        # Layout and numbering of subplots
                # 1 - 2 #
                # 3 - 4 #
                # 5 - 6 #
        if not self.fig.axes:
            ax = self.fig.add_subplot(321)
            self.plot_Sig_Eps (self.fig, self.canvas, ax)
            
            ax = self.fig.add_subplot(323)
            self.plot_M_Sig   (self.fig, self.canvas, ax)
             
            ax = self.fig.add_subplot(325)
            self.plot_Cv_Sig  (self.fig, self.canvas, ax)
             
            ax = self.fig.add_subplot(322)
            self.plot_U_Sig   (self.fig, self.canvas, ax)
             
            ax = self.fig.add_subplot(324)
            self.plot_t_Sig   (self.fig, self.canvas, ax)
             
            ax = self.fig.add_subplot(326)
            self.plot_k_Sig   (self.fig, self.canvas, ax)
                
            self.fig.tight_layout()

    def plot_Sig_Eps(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['oedoData']['sigmaV']
            dataY = self.data[i]['oedoData']['epsilon']*100
            ax.plot(dataX, dataY)   
        ax.set_xlabel('$\sigma$ [kPa]')
        ax.set_ylabel('$\epsilon_a$ [%]')
        ax.grid(True)
        
        yLimits = ax.get_ylim()
        ax.set_ylim(0, yLimits[1])
        ax.invert_yaxis()
    
        canvas.draw()

    def plot_M_Sig(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['oedoData']['sigmaM']
            dataY = self.data[i]['filteredData']['M']/1000
            ax.plot(dataX, dataY)   
        ax.set_xlabel('$\sigma_m$ [kPa]')
        ax.set_ylabel('$M$ [MPa]')
        ax.grid(True)
        
        xLimits = ax.get_xlim()
        ax.set_xlim([0,xLimits[1]])
        
        canvas.draw()
    
    def plot_Cv_Sig(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['oedoData']['sigmaM']
            dataY = self.data[i]['filteredData']['Cv']
            ax.plot(dataX, dataY)   
        ax.set_xlabel('$\sigma_m$ [kPa]')
        ax.set_ylabel('$C_v [m^2/s]$')
        ax.grid(True)
        
        xLimits = ax.get_xlim()
        ax.set_xlim([0,xLimits[1]])
        
        canvas.draw()
    
    def plot_U_Sig(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['oedoData']['sigmaV']
            dataY = self.data[i]['oedoData']['porePr']
            ax.plot(dataX, dataY)   
        ax.set_xlabel('$\sigma$ [kPa]')
        ax.set_ylabel('$U_0$ [kPa]')
        ax.grid(True)
        
        xLimits = ax.get_xlim()
        ax.set_xlim([0,xLimits[1]])
        
        canvas.draw()

    def plot_t_Sig(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['oedoData']['sigmaV']
            dataY = self.data[i]['time']
            ax.plot(dataX, dataY)   
        ax.set_xlabel('$\sigma$ [kPa]')
        ax.set_ylabel('t [s]')
        ax.grid(True)
        
        xLimits = ax.get_xlim()
        ax.set_xlim([0,xLimits[1]])
        
        canvas.draw()
    
    def plot_k_Sig(self, fig, canvas, ax):
        for i in range(len(self.data)):
            dataX = self.data[i]['oedoData']['sigmaM']
            dataY = self.data[i]['filteredData']['k']
            ax.plot(dataX, dataY)   
        ax.set_xlabel('$\sigma_m$ [kPa]')
        ax.set_ylabel('$k$ [?]')
        ax.grid(True)
        
        xLimits = ax.get_xlim()
        ax.set_xlim([0,xLimits[1]])
        
        canvas.draw()

    def interpret_Data(self, fileData):
        # Label & date
        fileInfo = {'label':fileData[0][0], 'date':fileData[0][1]}
        # TODO: Change label to filename since label is name of machine
        
        #Header
        header = {'depth':float(fileData[1][3][1].replace(",",".")), 'height':float(fileData[1][6][1].replace(",",".")), 'area':float(fileData[1][5][1].replace(",",".")),'comment':fileData[1][4][1]}
        headerAll = fileData[1] # For infoBox
        
        #Calibration data
        calibData = fileData[2]
        
        # Time & modechange
        time = fileData[4]
        mode = fileData[5] # Obsolete at the moment
        
        # Remove first row
        fileData[6] = np.delete(fileData[6], 0, 0)
        time        = np.delete(time, 0, 0)
        
        
        # Force, stresses and deformation data       
        measuredData = {'deform':fileData[6][:,4]/1000, 'vertPr':fileData[6][:,5], 'porePr':fileData[6][:,6]}
        
        ## Calculated values
        epsilon = measuredData['deform']/header['height']
        sigmaV  = measuredData['vertPr']    # Total stress
        porePr  = measuredData['porePr']
        
        arraySize = len(sigmaV)-1  # Used for looping and allocating variable size
        
        # TODO: Handle division by zero!
        M = np.zeros(arraySize)
        for i in range(arraySize):
            M[i] = (sigmaV[i+1]-sigmaV[i])/(epsilon[i+1] - epsilon[i])
            if M[i] < 0:
                M[i] = 0.0001
        
        sigmaM  = sigmaV - 2/3 * porePr     # Effective stress
        sigmaM = np.delete (sigmaM, 0, 0)   # Need same dim as M & Cv
        
        Cv = np.zeros(arraySize)
        for i in range(arraySize):
            Cv[i] = (sigmaV[i+1]-sigmaV[i])/(time[i+1]-time[i]) * (header['height']*(1-epsilon[i]))**2/(2*porePr[i]) # m^2/s  31 556 926?
            if Cv[i] < 0:
                Cv[i] = 0
        
        avg = np.median(Cv)
        std = np.std(Cv, ddof=1)
            
        for i in range(arraySize):
            if Cv[i] > 0.25*std:
                Cv[i] = Cv[i] = avg
            
        # TODO: Must determine factor to get m^2/yr    
        #k   =   Cv/M*10  # 10 is spesific weight of water UNIT???
        k = np.zeros(arraySize) # Remove this line when done
        
        filtered_M  = M
        filtered_Cv = Cv
        filtered_k  = k
           
        oedoData = {'sigmaV':sigmaV, 'sigmaM':sigmaM, 'epsilon':epsilon, 'porePr':porePr, 'M':M, 'Cv':Cv, 'k':k}
        filteredData = {'M':filtered_M, 'Cv':filtered_Cv, 'k':filtered_k}
        
        # Store relevant data
        self.data.append({'fileInfo':fileInfo, 'header':header, 'headerAll':headerAll, 'calibData':calibData, 'time':time, 'mode':mode, 'fileData':fileData, 'oedoData':oedoData, 'filteredData':filteredData}) 
    
    
    def fill_Infotable(self, data, i):
        # Fill table data content
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        
        item = QtGui.QTableWidgetItem(str(i))
        self.tableWidget.setItem(i,0,item)
        
        item = QtGui.QTableWidgetItem(data['fileInfo']['label'])
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(QtCore.Qt.Checked)
        self.tableWidget.setItem(i,1,item)
        
        item = QtGui.QTableWidgetItem(data['fileInfo']['date'])
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
        item.setTextAlignment(QtCore.Qt.AlignCenter);
        self.tableWidget.setItem(i,2,item)
        
        item = QtGui.QTableWidgetItem( str( data['header']['depth']) + ' m')
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
        item.setTextAlignment(QtCore.Qt.AlignCenter);
        self.tableWidget.setItem(i,3,item)
        
        item = QtGui.QTableWidgetItem('0%')  # SMOOTH
        item.setTextAlignment(QtCore.Qt.AlignCenter);
        #item.setCheckState(QtCore.Qt.Checked)
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable)
        self.tableWidget.setItem(i,4,item)
        
        item = QtGui.QTableWidgetItem(data['header']['comment'])
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)
        item.setTextAlignment(QtCore.Qt.AlignCenter);
        self.tableWidget.setItem(i,5,item)
        
        # create buttons in cells - One for each data -- Need Indexing!
        btnHeaderInfo  = QtGui.QPushButton(self.tableWidget)
        btnCalibInfo   = QtGui.QPushButton(self.tableWidget)
        
        self.listOfBtn.append([btnHeaderInfo,btnCalibInfo])
        
        btnHeaderInfo.setText('Info')
        btnCalibInfo.setText('Info')
        
        self.tableWidget.setCellWidget(i, 6, btnHeaderInfo)
        self.tableWidget.setCellWidget(i, 7, btnCalibInfo)
        
    def update_Plot(self, item):
        col = item.column()
        if col == 1:
            self.changeVisible_State(item)
        else:
            self.smoothData(item)
    
    def smoothData(self, item): 
        state = item.checkState()
        row   = item.row()
        actualRow = int(self.tableWidget.item(row,0).text()) # In case of sorting
    
        text = item.text()
        text = text.replace(',','.')
        text = text.replace('%','')
        
        try:
            value = float(text)
        except:
            value = -1 # Flag for error
            
            
        if value >= 0 and value <=75:
            string = str(value) + ' %'
            value = value/100
            self.defineItemText(actualRow, string)
        elif value == 0:
            string = str(value) + ' %'
            self.defineItemText(actualRow, string)
        else:
            outputString = 'Error \n Value must be either between: \n 0.1-75 %'
            self.infoWindow = PopupWindow(outputString)
            self.infoWindow.show()    
            
            string = '0.0 %'
            self.defineItemText(actualRow, string)
            value = 0.0
            
        if value == 0.0 or value == 0:
                self.data[actualRow]['filteredData']['M']  = self.data[actualRow]['oedoData']['M']
                self.data[actualRow]['filteredData']['Cv'] = self.data[actualRow]['oedoData']['Cv']
                self.data[actualRow]['filteredData']['k']  = self.data[actualRow]['oedoData']['k']
        else:
            self.data[actualRow]['filteredData']['M']  = lowess(self.data[actualRow]['oedoData']['M'], self.data[actualRow]['oedoData']['sigmaM'],  return_sorted=False, frac=value, it=0)
            self.data[actualRow]['filteredData']['Cv'] = lowess(self.data[actualRow]['oedoData']['Cv'], self.data[actualRow]['oedoData']['sigmaM'], return_sorted=False, frac=value, it=0)
            self.data[actualRow]['filteredData']['k']  = lowess(self.data[actualRow]['oedoData']['k'], self.data[actualRow]['oedoData']['sigmaM'],  return_sorted=False, frac=value, it=0)
        
        
        self.fig.axes[1].lines[actualRow].set_data(self.data[actualRow]['oedoData']['sigmaM'], self.data[actualRow]['filteredData']['M']/1000)
        self.fig.axes[1].relim(visible_only=True)
        self.fig.axes[1].autoscale_view()
        self.canvas.draw()
        self.fig.axes[2].lines[actualRow].set_data(self.data[actualRow]['oedoData']['sigmaM'], self.data[actualRow]['filteredData']['Cv'])
        self.fig.axes[2].relim(visible_only=True)
        self.fig.axes[2].autoscale_view()
        self.canvas.draw()
        self.fig.axes[5].lines[actualRow].set_data(self.data[actualRow]['oedoData']['sigmaM'], self.data[actualRow]['filteredData']['k'])
        self.fig.axes[5].relim(visible_only=True)
        self.fig.axes[5].autoscale_view()
        self.canvas.draw()
            
             
    def defineItemText(self, row, string):
        item = QtGui.QTableWidgetItem(string)
        item.setTextAlignment(QtCore.Qt.AlignCenter);
        self.tableWidget.itemChanged.disconnect(self.update_Plot)
        self.tableWidget.setItem(row, 4, item)
        self.tableWidget.itemChanged.connect(self.update_Plot)
        
    
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
    filey = [".\\Raw files\\oedometer.lvm" ]

    app = QtGui.QApplication(sys.argv)
    main = CRS(filey)
    main.show()
    sys.exit(app.exec_())
    
    