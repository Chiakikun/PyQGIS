﻿# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GetRasterValueSample
                                 A QGIS plugin
 マウスカーソル下のラスタの値をツールチップで表示します
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-01-25
        git sha              : $Format:%H$
        copyright            : (C) 2020 by unemployed
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolTip

# Initialize Qt resources from file resources.py
from .resources import *
import os.path

import qgis.core;

class GetRasterValueSample:
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
            'GetRasterValueSample_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.menu = self.tr(u'&GetRasterValue Sample')

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
        return QCoreApplication.translate('GetRasterValueSample', message)


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
        self.iface.removePluginMenu(
            self.tr(u'&MapTool Sample'),
            self.action)
        self.iface.removeToolBarIcon(self.action)


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

        self.canvas = canvas
        self.iface = iface
        self.timerMapTips = QTimer( canvas )
        self.timerMapTips.timeout.connect( self.showMapTip )

    def canvasMoveEvent(self, event):
        QToolTip.hideText()
        self.timerMapTips.start( 700 )

    def showMapTip( self ):
        self.timerMapTips.stop()

        rLayer = self.iface.activeLayer()
        if type(rLayer) is qgis.core.QgsRasterLayer:
            mousepos = self.canvas.mouseLastXY()
            mappos = self.toMapCoordinates(mousepos)

            ident = rLayer.dataProvider().identify( mappos, qgis.core.QgsRaster.IdentifyFormatValue ) # https://qgis.org/api/qgsraster_8h_source.html#l00057 ピクセル値を取得するみたいです
            if ident.isValid():
                print('マウス位置:' + str(mousepos))
                print('マップ位置:' + str(mappos))

                values = ident.results().values()
                text = ", ".join(['{0:g}'.format(r) for r in values if r is not None] ) # 複数取得することあるかなぁ？
            else:
                text = "Non valid value"
            QToolTip.showText( self.canvas.mapToGlobal( self.canvas.mouseLastXY() ), text, self.canvas )
