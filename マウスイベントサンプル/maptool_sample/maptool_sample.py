# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MapToolSample
                                 A QGIS plugin
 MapToolを使ったサンプルです。
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-11-19
        git sha              : $Format:%H$
        copyright            : (C) 2019 by unemployed
        email                : chiakikungm@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *

import os.path

import qgis.core;

class MapToolSample:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MapToolSample_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.menu = self.tr(u'&MapTool Sample')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MapToolSample', message)


    def initGui(self):
        icon = QIcon(':/plugins/maptool_sample/icon.png')
        self.action = QAction(icon, self.tr(u'MapTool版サンプル'), self.iface.mainWindow())
        self.action.triggered.connect(self.execSample)
        self.action.setEnabled(True)
        self.action.setCheckable(True)
        self.action.setEnabled(True)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.menu, self.action)
        
        # このサンプル実行中かな?
        self.isrun = False

        # 追加 キャンバス上のマウスイベント設定
        self.mouseEventSample = MouseEventSample(self.iface, self.iface.mapCanvas())
        self.iface.mapCanvas().mapToolSet.connect(self.unsetTool)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&MapTool Sample'),
                action)
            self.iface.removeToolBarIcon(action)


    def unsetTool(self, tool):
        try:
        # 実行中にこのサンプル以外のアイコンを押した場合
            if not isinstance(tool, MouseEventSample) and self.isrun:
                self.isrun = False
                self.action.setChecked(False)
        except Exception:
            pass


    def execSample(self):
        if self.isrun:
            self.iface.mapCanvas().unsetMapTool(self.mouseEventSample)
            self.iface.mapCanvas().setMapTool(self.previousMapTool)
            self.isrun = False
        else:
            self.previousMapTool = qgis.utils.iface.mapCanvas().mapTool()
            self.iface.mapCanvas().setMapTool(self.mouseEventSample)
            self.isrun = True

        
class MouseEventSample(qgis.gui.QgsMapTool):
    def __init__(self, iface, canvas):
        qgis.gui.QgsMapTool.__init__(self, canvas)

    def canvasMoveEvent(self, event):
        print('マウス移動:' + str(self.toMapCoordinates(event.pos())))

    def canvasPressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            print('左クリック!' + str(self.toMapCoordinates(event.pos())))

        if event.button() == QtCore.Qt.RightButton:
            print('右クリック!' + str(self.toMapCoordinates(event.pos())))
