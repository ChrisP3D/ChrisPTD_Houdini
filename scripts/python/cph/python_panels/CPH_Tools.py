########################################################################
# Replace the sample code below with your own to create a
# PyQt5 or PySide2 interface.  Your code must define an
# onCreateInterface() function that returns the root widget of
# your interface.
#
# The 'hutil.Qt' is for internal-use only.
# It is a wrapper module that enables the sample code below to work with
# either a Qt4 or Qt5 environment for backwards-compatibility.
#
# When developing your own Python Panel, import directly from PySide2
# or PyQt5 instead of from 'hutil.Qt'.
########################################################################

#
# SAMPLE CODE
#
from PySide2 import QtWidgets, QtCore, QtSvg ,QtGui 
import os
from cph import cph_hdaUtils as cphda
import hou



class FileBrowserWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.scrollArea = QtWidgets.QScrollArea()
        self.gridWidget = QtWidgets.QWidget()  # This widget holds the grid layout
        self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.gridWidget)
        self.layout.addWidget(self.scrollArea)
        
        #BUTTONS
        
        self.openHDADialogButton = QtWidgets.QPushButton("Select HDAs")
        self.openHDADialogButton.clicked.connect(self.openHDAFileDialog)
        
        self.openIconDialogButton = QtWidgets.QPushButton("Select Icon SVG ")
        self.openIconDialogButton.clicked.connect(self.openIconFileDialog)
        
        self.setIconButton = QtWidgets.QPushButton("Set Icons")
        self.setIconButton.clicked.connect(self.setIcons)
        
        #ICON
        self.IconSvg = AspectRatioSvgWidget()
        self.svgPath = 'F:/Portfolio/Projects/Glyphs/geo/glyphrnd10.1.svg'
        self.icon_pathfield = QtWidgets.QLineEdit()
        self.IconSvg.setMaximumSize(200, 200) 
        self.IconSvg.load(self.svgPath)
        #ICON PATH
        self.icon_defaultpath = "Path/To/Icon"
        self.icon_pathfield.setText(self.icon_defaultpath)
        
        #LIST SELECTED FILES
        self.selectionListWidget = CustomListWidget()
        self.selectionListWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.selectionListWidget.customContextMenuRequested.connect(self.selectionListWidget.showContextMenu)
        self.selectionListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)   

        #ADD WIDGETS
        self.layout.addWidget(self.openHDADialogButton)
        self.layout.addWidget(self.openIconDialogButton)
        self.layout.addWidget(self.setIconButton)
        self.layout.addWidget(self.selectionListWidget)
        self.layout.addWidget(self.IconSvg)
        self.layout.addWidget(self.icon_pathfield)# Add the list widget to the layout

#####################
#SELECT HDAS
#####################
    def getSelectedHDAs(self):
        hdas_paths = []
        for file in self.selectionListWidget.selectedItems():
            hdas_paths.append(file.text())
        return hdas_paths
        
    def setIcons(self):
        
        target_icon = self.icon_pathfield.text()
        if target_icon == self.icon_defaultpath:
            hou.ui.displayMessage("Please Select An SVG File.")
            return
        elif not target_icon.endswith('.svg'):
            hou.ui.displayMessage("File Type Must Be .svg")
            
        elif not len(self.getSelectedHDAs()):
            hou.ui.displayMessage("Please Select HDAs From the List")
            

            
        else:
            hda_paths = self.getSelectedHDAs()
            paths_string = '\n'.join([hda_path for hda_path in hda_paths])
            hou.ui.displayMessage(f"The Selected Nodes Will have their Icon Set to {target_icon}", details = paths_string)
            for hda_path in hda_paths:
                try:
                    hdadef = hou.hda.definitionsInFile(hda_path)[0]
                    hdadef.setIcon(self.icon_pathfield.text())
                except hou.OperationFailed as e:
                    print(f"Operation failed: {e}")
                except Exception as e:
                    # This is a more generic catch-all for any other exceptions that might occur
                    print(f"An unexpected error occurred: {e}")
                
    def openHDAFileDialog(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        
        filters = ['*hda*','*otl*']
        dialog.setNameFilters(filters)
        
        if dialog.exec_() == QtWidgets.QFileDialog.Accepted:
            paths = dialog.selectedFiles()
            self.processHDASelection(paths)
            

    def processHDASelection(self, paths):
        if not paths:
            return
        
        hdaexts = ['hda','hdalc','hdanc']
        goodpaths = []
        for path in paths:
        #     for file_name in os.listdir(path):
        #         file_path = os.path.join(path, file_name)
            for ext in hdaexts:
                if path.endswith(f'.{ext}') :
                    goodpaths.append(path)
        self.updateHDASelectionList(goodpaths)

        
    def updateHDASelectionList(self, paths):
        self.selectionListWidget.clear() 
        if not paths:
            return
        for path in paths:
            self.selectionListWidget.addItem(path)

            
#####################
#SELECT ICON
#####################


    def openIconFileDialog(self):
        filter = "SVG Files (*.svg)"
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select SVG File","",filter)
        if fileName:
            self.updateIcon(fileName)

    def updateIcon(self, path):
        if not path:
            return
        self.svgPath = path
        self.IconSvg.load(self.svgPath)
        self.icon_pathfield.setText(path)


    def updateGridLayout(self, paths):
        # Clear existing content in the grid
        while self.gridLayout.count():
            child = self.gridLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Populate the grid with new items and checkboxes
        for row, path in enumerate(paths):
            # Create a label for the item name
            label = QtWidgets.QLabel(os.path.basename(path))
            # Create a checkbox for the item
            checkBox = QtWidgets.QCheckBox()
            
            # Add the label and checkbox to the grid
            self.gridLayout.addWidget(label, row, 0)
            self.gridLayout.addWidget(checkBox, row, 1)

class AspectRatioSvgWidget(QtSvg.QSvgWidget):
    def __init__(self, parent=None):
        super(AspectRatioSvgWidget, self).__init__(parent)
        self.setPreserveAspectRatio(True)

    def setPreserveAspectRatio(self, preserve):
        self._preserveAspectRatio = preserve

    def resizeEvent(self, event):
        if self._preserveAspectRatio:
            size = self.sizeHint()
            size.scale(event.size(), QtCore.Qt.KeepAspectRatio)
            self.resize(size)
        super(AspectRatioSvgWidget, self).resizeEvent(event)

    def sizeHint(self):
        if self.renderer().isValid():
            defaultSize = self.renderer().defaultSize()
            return defaultSize
        return super(AspectRatioSvgWidget, self).sizeHint()
    
    
    
    
    
class CustomListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(CustomListWidget, self).__init__(parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, position):
        # Get the list item under the cursor
        listItem = self.itemAt(position)
        if listItem is None:
            return
        
        # Create the context menu
        contextMenu = QtWidgets.QMenu(self)
        
        # Add "Copy to Clipboard" action
        copyAction = contextMenu.addAction("Copy to Clipboard")
        copyAction.triggered.connect(lambda: self.copyToClipboard(listItem.text()))
        
        # Add "Load" action
        loadAction = contextMenu.addAction("Load")
        loadAction.triggered.connect(lambda: self.loadItem(listItem.text()))
        
        # Show the context menu at the cursor's position
        contextMenu.exec_(self.viewport().mapToGlobal(position))

    def copyToClipboard(self, text):
        clipboard = QtGui.QGuiApplication.clipboard()
        clipboard.setText(text)
        print(f"Copied to clipboard: {text}")

    def loadItem(self, text):
        hou.hdaDefinition(text)[0]
        print(f"Loading item: {text}")



