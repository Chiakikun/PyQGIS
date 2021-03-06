# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Dialog Skelton
        copyright            : (C) 2019 by Chiakikun
        email                : chiakikungm@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QPoint
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .dialog_skelton_dialog import DialogSkeltonDialog
import os.path

class DialogSkelton:

    def __init__(self, iface):
        self.menu_pos = '雛形' # プラグインの登録場所
        self.plugin_name = 'ダイアログ有り雛形'
        self.toolbar = True

        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None


    def initGui(self):
        icon = QIcon(self.plugin_dir+'/icon.png')
        self.action = QAction(icon, self.plugin_name, self.iface.mainWindow())
        self.action.triggered.connect(self.run) # アイコンを押下した時に実行されるメソッドを登録
        if self.toolbar:
            self.iface.addToolBarIcon(self.action) # ツールバーにアイコンを表示させたいなら#外して
        self.iface.addPluginToMenu(self.menu_pos, self.action)

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu(self.menu_pos, self.action)
        self.iface.removeToolBarIcon(self.action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = DialogSkeltonDialog(self.iface, self.action, self.iface.mainWindow()) # self.iface.mainWindow()を渡すと、ダイアログがQGISの後ろに隠れないようになります

        # 邪魔にならない場所にダイアログを表示させたいので
        pos = self.canvas.mapToGlobal(QPoint( 0, 0 ))
        self.dlg.move(pos.x(), pos.y())

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
