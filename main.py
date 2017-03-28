from PyQt4 import QtGui, QtCore
import selector
import crs

if __name__ == "__main__":
    import sys
    import numpy as np
    
    app = QtGui.QApplication(sys.argv)
    importGui = selector.Selector()
    importGui.show()
     
    sys.exit(app.exec_())