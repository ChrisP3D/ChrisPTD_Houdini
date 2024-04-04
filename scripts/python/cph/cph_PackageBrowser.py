from __future__ import print_function
from __future__ import absolute_import
#from toolutils import safe_reload

from builtins import range
import os
import hou

import json

from package import model
from package import pkgen
import hdefereval
import resourceui as rui

#safe_reload(model)

from PySide2 import QtWidgets, QtCore, QtGui  

class PackageBrowser(QtWidgets.QFrame):
    def __init__(self,parent=None):
        super(PackageBrowser, self).__init__(parent)

        self.marker_count = 1        

        #scene setup
        self._currentPackage = None

        # widget config
        self._error_brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        self._error_brush.setStyle(QtCore.Qt.SolidPattern)

        self._warn_brush = QtGui.QBrush(QtGui.QColor(255, 255, 0))
        self._warn_brush.setStyle(QtCore.Qt.SolidPattern)

        self._info_brush = QtGui.QBrush(QtGui.QColor(0, 255, 0))
        self._info_brush.setStyle(QtCore.Qt.SolidPattern)

        self._msg_brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        self._msg_brush.setStyle(QtCore.Qt.SolidPattern)

        # all actions
        self._createActions()

        # child widgets

        # Menu bar
        self._file_menu = QtWidgets.QMenu(self)
        self._file_menu.aboutToShow.connect(self._populateFileMenu)

        self._edit_menu = QtWidgets.QMenu(self)
        self._edit_menu.aboutToShow.connect(self._populateEditMenu)

        menu_bar = hou.qt.MenuBar(self)
        file_menu_action = menu_bar.addAction("File")
        file_menu_action.setMenu(self._file_menu)
        edit_menu_action = menu_bar.addAction("Edit")
        edit_menu_action.setMenu(self._edit_menu)

        # create and set the tree view of packages
        self._treeview = BrowserTree(self) 

        # custom menu
        self._file_context_menu = QtWidgets.QMenu()
        self._file_context_menu.setStyleSheet(hou.qt.styleSheet())
        self._file_context_menu.aboutToShow.connect(self._populateContextMenu)
        
        # message view
        self._msg_view = rui.messageView()

        #message view buttons
        msg_clear_button = rui.PushButton(self._clear_messages_action)
      
        msg_toolbar_layout = QtWidgets.QHBoxLayout()
        msg_toolbar_layout.setSpacing(rui.UI().SIZE4)
        msg_toolbar_layout.setContentsMargins(rui.UI().MARGIN4)
        msg_toolbar_layout.addWidget(msg_clear_button)
        msg_toolbar_layout.addStretch()

        vmsg_layout = QtWidgets.QVBoxLayout()
        vmsg_layout.setSpacing(rui.UI().SIZE4)
        vmsg_layout.setContentsMargins(rui.UI().MARGIN4)
        vmsg_layout.addLayout(msg_toolbar_layout)
        vmsg_layout.addWidget(self._msg_view)

        msg_widget = QtWidgets.QWidget()
        msg_widget.setLayout(vmsg_layout)

        # toolbar buttons
        help_button = rui.PushButton(self._show_help_action)
        help_button.setProperty("transparent", True)

        # layout setup
        #view_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        view_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        view_splitter.addWidget(self._treeview)
        view_splitter.addWidget(msg_widget)
        view_splitter.setStretchFactor(0, .3)
        view_splitter.setStretchFactor(1, .7)

        toolbar_layout = QtWidgets.QHBoxLayout()
        toolbar_layout.setSpacing(rui.UI().SIZE4)
        toolbar_layout.setContentsMargins(rui.UI().MARGIN4)
        toolbar_layout.addWidget(menu_bar)

        toolbar_layout.addStretch(1)
        toolbar_layout.addWidget(help_button)                

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setSpacing(rui.UI().SIZE4)
        vlayout.setContentsMargins(rui.UI().MARGIN4)
        vlayout.addLayout(toolbar_layout)
        vlayout.addWidget(view_splitter)

        self.setLayout(vlayout)

    def _createActions(self):        
        self._load_package_action = QtWidgets.QAction(self)
        self._load_package_action.setText('Load Package...')
        self._load_package_action.triggered.connect(self.onLoadPackage)

        self._load_package_archive_action = QtWidgets.QAction(self)
        self._load_package_archive_action.setText('Load Package Archive...')
        self._load_package_archive_action.triggered.connect(self.onLoadPackageArchive)

        self._reload_package_action = QtWidgets.QAction(self)
        self._reload_package_action.setText('Reload')
        self._reload_package_action.triggered.connect(self.onReloadPackage)

        self._remove_package_action = QtWidgets.QAction(self)
        self._remove_package_action.setText('Remove')
        self._remove_package_action.triggered.connect(self.onRemovePackage)

        self._reload_selected_package_action = QtWidgets.QAction(self)
        self._reload_selected_package_action.setText('Reload Selected Package')
        self._reload_selected_package_action.triggered.connect(self.onReloadPackage)

        self._remove_selected_package_action = QtWidgets.QAction(self)
        self._remove_selected_package_action.setText('Remove Selected Package')
        self._remove_selected_package_action.triggered.connect(self.onRemovePackage)
        
        self._edit_package_action = QtWidgets.QAction(self)
        self._edit_package_action.setText('Edit')
        self._edit_package_action.triggered.connect(self.onEditPackage)

        self._expand_node_action = QtWidgets.QAction(self)
        self._expand_node_action.setText('Expand All')
        self._expand_node_action.triggered.connect(self.onExpandNode)

        self._show_help_action = QtWidgets.QAction(self)
        self._show_help_action.setIcon(hou.qt.createIcon('BUTTONS_help', rui.UI().SIZE26, rui.UI().SIZE26))
        self._show_help_action.setToolTip('Open package help')
        self._show_help_action.triggered.connect(self.onShowHelp)

        self._clear_messages_action = QtWidgets.QAction(self)        
        self._clear_messages_action.setIcon(hou.qt.createIcon('BUTTONS_clear', rui.UI().BTN_SIZE, rui.UI().BTN_SIZE))        
        self._clear_messages_action.setText('Clear')
        self._clear_messages_action.setToolTip('Clear messages')
        self._clear_messages_action.triggered.connect(self.onClearMessages)

        self._edit_selected_package_action = QtWidgets.QAction(self)
        self._edit_selected_package_action.setText('Edit Selected Package...')
        self._edit_selected_package_action.triggered.connect(self.onEditSelectedPackage)       

        self._new_package_action = QtWidgets.QAction(self)
        self._new_package_action.setText('New Package...')
        self._new_package_action.triggered.connect(self.onNewPackage)
        # NOTE: disabled until we have a code generator
        self._new_package_action.setEnabled(False)

        self._edit_package_file_action = QtWidgets.QAction(self)
        self._edit_package_file_action.setText('Edit Package...')
        self._edit_package_file_action.triggered.connect(self.onEditPackageFile)

    def _populateContextMenu(self):
        self._file_context_menu.addAction(self._edit_package_action)
        self._file_context_menu.addAction(self._expand_node_action)
        self._file_context_menu.addAction(self._reload_package_action)
        self._file_context_menu.addAction(self._remove_package_action)

        index = self._treeview.currentIndex()
        node = self._treeview.model().topNode(index)
        if node:
            self._edit_package_action.setEnabled(not node.packageLocked())
            self._reload_package_action.setEnabled(not node.packageLocked())
            self._remove_package_action.setEnabled(not node.packageLocked())

    def _populateFileMenu(self):
        self._file_menu.addAction(self._new_package_action)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._load_package_action)
        self._file_menu.addAction(self._load_package_archive_action)
        self._file_menu.addAction(self._reload_selected_package_action)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._remove_selected_package_action)

        index = self._treeview.currentIndex()
        node = self._treeview.model().topNode(index)
        if node:
            self._reload_selected_package_action.setEnabled(not node.packageLocked())
            self._remove_selected_package_action.setEnabled(not node.packageLocked())

    def _populateEditMenu(self):
        self._edit_menu.addAction(self._edit_package_file_action)
        self._edit_menu.addAction(self._edit_selected_package_action)

        index = self._treeview.currentIndex()
        node = self._treeview.model().topNode(index)
        if node:
            self._edit_package_file_action.setEnabled(not node.packageLocked())
            self._edit_selected_package_action.setEnabled(not node.packageLocked())

    def _clearMessages(self):
        try:
            self._msg_view.clear()
        except:
            pass

    def _refresh(self, reload=False):
        """
        reload: reload all packages if True
        """
        self._treeview.model().updateItems(reload)
        
    def _expandNode( self, index ):
        if not index.isValid():
            return

        childCount = index.model().rowCount(index)
        for i in range(childCount):
            child_index = index.child(i, 0)
            self._expandNode( child_index )

        if index.isValid():
            self._treeview.expand(index)

    def _addAutoloadPackage(self, target_package_filepath):
        """ Create an autoload package in the user folder for loading 
        target_package_filepath on start-up. An autoload package is a 
        simpler package used to redirect the loading of 
        target_package_filepath.
        """

        # Setup the autoload template parms
        kwargs = {}
        kwargs["template"] = "autoload.pkt"
        kwargs["tokens"] = [
            ("##enable##", "true"),
            ("##show##", "false"),
            ("##package_file##", "{}".format(target_package_filepath))]

        # create the package content
        package_content = pkgen.newPackage(kwargs)

        # save the autoload package to user folder
        autoload_package = self._makeAutoloadPackageFile(target_package_filepath)
        with open(autoload_package, 'w', encoding="utf-8") as f:
            f.write(package_content)

    def _removeAutoloadPackage(self, target_package_filepath):
        """ Find and remove the target_package_filepath's autoload 
            package file.
            Returns True if successful.
        """
        autoload_package = self._makeAutoloadPackageFile(target_package_filepath)
        
        if not os.path.isfile(autoload_package):
            return False

        try:
            os.remove(autoload_package)
            return True
        except Exception as e:
            pass
        return False

    def _makeAutoloadPackageFile(self, target_package_filepath, create_folder=True):
        """ Create the file path of the autoload package for a given 
            target package.
        e.g 
        target_package_filepath: /var/tmp/packages/mypackage.json
        autoload: $HOUDINI_USER_PREF_DIR/packages/mypackage_autoload.json
        """
        user_package_folder = "%s/packages" % os.environ['HOUDINI_USER_PREF_DIR']
        if not os.path.isdir(user_package_folder):
            if not create_folder:
                return ""
            os.mkdir( user_package_folder )
        
        base_name = os.path.basename(target_package_filepath)        
        base_name = os.path.splitext(base_name)[0]
        return "{}/{}_autoload.json".format(user_package_folder, base_name)

    def _addDisabledPackage(self, target_package_filepath):
        """ Create a disable package in the user folder to prevent 
            target_package_filepath to load on start-up. 
        """

        # Setup the disabled template parms
        kwargs = {}
        kwargs["template"] = "disable.pkt"
        kwargs["tokens"] = [
            ("##__disable__##", "{}".format(target_package_filepath)),
            ("##load_package_once##", "true"),
            ("##show##", "false")]

        # create the package content
        package_content = pkgen.newPackage(kwargs)

        # save the autoload package to user folder
        new_package = self._makePackageFile(target_package_filepath)
        with open(new_package, 'w', encoding="utf-8") as f:
            f.write(package_content)

    def _removeDisabledPackage(self, package_filepath):
        """ Find and remove a package in the user folder that matches
            package_filepath.
            Returns True if successful.
        """
        package = self._makePackageFile(package_filepath, create_folder=False)
        
        if not os.path.isfile(package):
            return False

        try:
            with open(package, encoding="utf-8") as f:
                data = json.load(f)
                if data["__disable__"] != package_filepath:
                    return False
        except:
            return False

        try:
            os.remove(package)
            return True

        except Exception as e:
            pass
        return False
    
    def _makePackageFile(self, target_package_filepath, create_folder=True):
        """ Create a new package file path in the user fodler.
            e.g 
            target_package_filepath: /var/tmp/packages/mypackage.json
            new package: $HOUDINI_USER_PREF_DIR/packages/mypackage.json
        """
        user_package_folder = "%s/packages" % os.environ['HOUDINI_USER_PREF_DIR']
        if not os.path.isdir(user_package_folder):
            if not create_folder:
                return ""
            os.mkdir( user_package_folder )
        
        base_name = os.path.basename(target_package_filepath)        
        base_name = os.path.splitext(base_name)[0]
        return "{}/{}.json".format(user_package_folder, base_name)

    def _makeNewPackageFile(self, package_folder=None):
        if not package_folder:
            package_folder = "{}/packages".format(os.environ['HOUDINI_USER_PREF_DIR'])

        # Get a unique filename
        filename = None
        filename_default = "package"
        while not filename:
            filename, status = QtWidgets.QInputDialog.getText(self, "New Package", "File Name", 
                QtWidgets.QLineEdit.Normal, filename_default)
            if not status:
                return None

            if not filename:
                filename = filename_default

            package_file_path = "{}/{}.json".format(package_folder, filename)
            self.printMessage(package_file_path)
            if not os.path.isfile(package_file_path):
                return package_file_path
            
            if hou.ui.displayConfirmation("File exists, overwrite?"):
                return package_file_path
            filename = None

    def printMessage(self, msg, msg_type=hou.severityType.Message):
        self._msg_view.appendText(msg, severity=msg_type)
                        
    # handlers
    def onActivate(self):

        ''' called by the pypanel framework '''
        hou.hipFile.addEventCallback(self.onSceneLoaded)
        hou.ui.addResourceEventCallback(self.onResourceEvent)

        self._refresh(reload=False)

    def onDeactivate(self):
        """ Called by the pypanel framework 
        """ 
        # Don't remove callbacks here so the browser can still work when 
        # hidden.
        pass

    def onDestroy(self):
        """ called by the pypanel framework 
        """ 
        hou.hipFile.removeEventCallback(self.onSceneLoaded)
        hou.ui.removeResourceEventCallback(self.onResourceEvent)

    def onPackageApplyAction(self, **kwargs):
        """
        Package editor callback
        """
        package_filepath = kwargs.get("package_filepath", None)
        if package_filepath:
            try:
                hou.ui.reloadPackage(package_filepath)
            except:
                pass

    def onContextMenu(self, pos):
        global_pos = QtGui.QCursor.pos()
        self._file_context_menu.popup(global_pos)

    def onExpandNode(self):
        index = self._treeview.currentIndex()
        self._expandNode( index )
                
    def onLoadPackage(self):
        # Open a dialog to select a package 
        package_folder = os.environ['HOUDINI_USER_PREF_DIR']
        package_file_path = hou.ui.selectFile(
            title='Select and load a package file',
            start_directory=package_folder,
            multiple_select=False,
            pattern='*.json')

        if not package_file_path:
            return

        try:
            hou.ui.loadPackage(package_file_path)
        except:
            self.printMessage(
                "Could not load package: %s" % package_file_path, hou.severityType.Error)

    def onLoadPackageArchive(self):
        # Open a dialog to select a package 
        package_folder = os.environ['HOUDINI_USER_PREF_DIR']
        package_file_path = hou.ui.selectFile(
            title='Select and load a package archive file',
            start_directory=package_folder,
            multiple_select=False,
            pattern='*.zip')

        if not package_file_path:
            return

        try:
            hou.ui.loadPackageArchive(package_file_path)
        except:
            self.printMessage(
                "Could not load package archive: %s" % package_file_path, hou.severityType.Error)

    def onRemovePackage(self):
        index = self._treeview.currentIndex()
        node = self._treeview.model().topNode(index)
        package_filepath = node.packageFilepath()
        try:
            hou.ui.unloadPackage(package_filepath)
            self._removeAutoloadPackage(package_filepath)
            self._removeDisabledPackage(package_filepath)
        except:
            hdefereval.executeDeferred(_printMessage, self, node.errors(), hou.severityType.Error)

    def onReloadPackage(self):
        index = self._treeview.currentIndex()
        node = self._treeview.model().topNode(index)
        package_filepath = node.packageFilepath()
        try:
            hou.ui.reloadPackage(package_filepath)
        except:
            hdefereval.executeDeferred(_printMessage, self, node.errors(), hou.severityType.Error)

    def onEditPackage(self):
        index = self._treeview.currentIndex()
        node = self._treeview.model().topNode(index)
        hou.ui.openFileEditor('Package Editor', node.packageFilepath(), self.onPackageApplyAction, 
            {'package_filepath':node.packageFilepath()} )

    def onEditSelectedPackage(self):
        index = self._treeview.currentIndex()
        node = self._treeview.model().topNode(index)

        if node is None:
            return

        self.onEditPackage()

    def onNewPackage(self):
        """ Create a new package.
        """

        # create a new file in the user folder with a code template
        package_file_path = self._makeNewPackageFile()
        if not package_file_path:
            return

        # create the package content
        kwargs = {}
        kwargs["template"] = "basic.pkt"
        package_content = pkgen.newPackage(kwargs)

        with open(package_file_path, 'w', encoding="utf-8") as file:
            file.write(package_content)

        # Load the new package
        hou.ui.loadPackage(package_file_path)
        hou.ui.openFileEditor('Package Editor', package_file_path, self.onPackageApplyAction, 
            {'package_filepath':package_file_path} )
        
    def onEditPackageFile(self):
        package_folder = os.environ['HOUDINI_USER_PREF_DIR']
        package_file_path = hou.ui.selectFile(
            title='Edit Package',
            start_directory=package_folder,
            multiple_select=False,
            pattern='*.json')

        if not package_file_path:
            return

        hou.ui.openFileEditor('Package Editor', package_file_path )

    def onCheckAutoLoad(self, index):
        """ Set a package to load on startup when checked. When unchecked,
            mark the package to not load on startup. 
            
            checked: We add an "autoload" package in the user folder to
                     load a target package on startup. The autoload
                     package is a simple package with an instruction to
                     load the real package (target).

                     If the folder has already a package with the same 
                     name as the target package, we just remove it instead. 
                     
                     NOTE: probably not the best solution.

            unchecked:  Remove the "autoload" package if one exists for 
                        the target package. If there isn't one, add a 
                        package to disable the target package.
        """

        node = index.internalPointer()

        if node.isChecked():
            # Mark the package to load on startup
            if not self._removeDisabledPackage(node.packageFilepath()):
                # Package not disabled, add an autoload package 
                self._addAutoloadPackage(node.packageFilepath())
        elif not self._removeAutoloadPackage(node.packageFilepath()):
            # No autoload package to remove, we assume the package 
            # was loaded automatically on startup from a known
            # folder. Add a new package instead to the user 
            # folder to disable the target package on startup.
            self._addDisabledPackage(node.packageFilepath())

    def onSceneLoaded(self, event_type):
        if event_type in (hou.hipFileEventType.AfterLoad, hou.hipFileEventType.AfterClear):
            self._refresh(reload=False)

    def onSelectionChanged(self, signal):
        index = self._treeview.currentIndex()
        node = self._treeview.model().topNode(index)

        if node:
            self.printMessage(node.errors(), hou.severityType.Error)
            self.printMessage(node.warnings(), hou.severityType.Warning)

        self._edit_package_action.setEnabled(True)
        self._reload_selected_package_action.setEnabled(True)
        self._remove_selected_package_action.setEnabled(True)

    def onShowHelp(self):
        desktop = hou.ui.curDesktop()
        browser = desktop.paneTabOfType(hou.paneTabType.HelpBrowser)
        if browser is None:
            browser = desktop.createFloatingPane(hou.paneTabType.HelpBrowser)

        import houdinihelp
        help_path = houdinihelp.getHelpForId('h.plugins')
        browser.displayHelpPath(help_path)

    def onClearMessages(self):
        self._clearMessages()
    
    def onResourceEvent(self, **kwargs):
        
        if hou.resourceType.Package is not kwargs["resource_type"]:
            return

        action_msg = {hou.resourceEventMessage.OnLoad:"loaded",
                      hou.resourceEventMessage.OnReload:"reloaded",
                      hou.resourceEventMessage.OnUnload:"unloaded"} 
        
        package_name = ""
        try:
            package_name = kwargs['package_name']
        except:
            try:
                package_name = kwargs['package_filepath']
            except:
                pass                

        try:
            if kwargs["event_message_type"] == hou.severityType.Error:
                self.printMessage(kwargs["event_message"], hou.severityType.Error)
                self._refresh(True)
                return
        except:
            pass

        try:
            msg = "{} {}".format(package_name, action_msg[kwargs["event_type"]])
            self.printMessage(msg, hou.severityType.Message)
        except:
            msg = "Package {} error".format(package_name)
            self.printMessage(msg, hou.severityType.Error)

        self._refresh(True)

# for deferred logging
def _printMessage(view, msg, msg_type=hou.severityType.Message):
    view.printMessage(msg, msg_type)

class BrowserTree(QtWidgets.QTreeView):
 
    def __init__(self, browser):
        super(BrowserTree, self).__init__(browser)
        
        self._browser = browser
        self.setAlternatingRowColors(True)
        self.setWordWrap(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._browser.onContextMenu)
        self.setItemDelegate(CustomStyleItemDelegate(self))
        self.setUniformRowHeights(True)

        # init model                
        self.setModel( model.PackageModel() ) 
        self.model().autoLoadUpdateSignal.connect(self._browser.onCheckAutoLoad)

        # Selection
        selection_model = self.selectionModel()
        selection_model.selectionChanged.connect(self._browser.onSelectionChanged)

        # Header
        h = self.header()
        h.setStretchLastSection(False)
        h.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        h.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)        

    def hasNodes(self):
        return len(self._node_dictionary) > 0

    def resizeEvent(self, event):
        def computeAutoWidthFactor(treeview, width):
            extra = 1.5
            try:
                factor = (float(treeview.fontMetrics().horizontalAdvance("Auto"))/float(width))*extra
            except:
                width = treeview.columnWidth(0) + treeview.columnWidth(1)
                factor = (float(treeview.fontMetrics().horizontalAdvance("Auto"))/float(width))*extra

            return (factor, width)
            
        (factor_auto, width) = computeAutoWidthFactor(self, event.size().width())        
        factor_pkg = 1.0 - factor_auto
        
        self.setColumnWidth(0, width * factor_pkg)
        self.setColumnWidth(1, width * factor_auto)


class CustomStyleItemDelegate(QtWidgets.QStyledItemDelegate):
    
    def paint(self, painter, option, model_index): 
        column = model_index.column()
        is_top = model_index.internalPointer().isTop()
        new_rect = QtCore.QRect(option.rect)

        if column == model.AUTO_COL_INDEX and is_top: 
            # draw rectangle around the checkbox
            painter.save()
            painter.setPen(QtGui.QColor(QtCore.Qt.black))
            painter.drawRect(option.rect)
            painter.restore()

            # draw checked mark
            element = QtWidgets.QCommonStyle().PE_IndicatorCheckBox
            styleoption = QtWidgets.QStyleOptionButton()
            styleoption.rect = new_rect

            icon = model_index.model().data(model_index, QtCore.Qt.DecorationRole)
            if icon:
                pixmap = icon.pixmap(QtCore.QSize(model.ICON_SIZE, model.ICON_SIZE))
                QtWidgets.QCommonStyle().drawItemPixmap(painter, new_rect, QtCore.Qt.AlignCenter, pixmap)            
        else:
            super(CustomStyleItemDelegate, self).paint(painter, option, model_index)

#for debugging
def iterate_model(index, model_to_iterate, depth, func):
    if index.isValid():
        func(index, depth)

    if model_to_iterate.hasChildren(index) is None:
        return

    for i in range(0,model_to_iterate.rowCount(index)):
        for j in range(0,model_to_iterate.columnCount(index)):
            iterate_model(model_to_iterate.index(i, j, index), model_to_iterate, depth+1, func )

def dump_model( view ):
    iterate_model( view.rootIndex(), view.model(), 0, 
        lambda index, depth: print( index.parent().isValid(), ':', index.row(), ',', index.column(), '=', index.data()) )
