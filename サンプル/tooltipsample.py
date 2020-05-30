# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ToolTipSample
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Chiakikun
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
使い方例（『https://github.com/Chiakikun/PyQGIS/blob/master/ダイアログ無し雛形/nodialog_skelton.py』に組み込む場合）

プラグインのフォルダにこのファイルを置く

インポート
from .tooltipsample import ToolTipSample

nodialog_skelton.pyのメソッドを次に書き換える
    def setConnect(self):
        self.tooltipSample = ToolTipSample(self.iface, self.canvas, 700)
        self.canvas.setMapTool(self.tooltipSample)  # このサンプルを登録

        self.canvas.mapToolSet.connect(self.unsetTool) # このサンプル実行中に他のアイコンを押した場合


    def disConnect(self):
        if self.tooltipSample.isActive():
            self.canvas.unsetMapTool(self.tooltipSample)
        try:
            self.canvas.mapToolSet.disconnect(self.unsetTool)
        except:
            pass
"""
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtWidgets import QToolTip
import qgis.core


class ToolTipSample(qgis.gui.QgsMapTool):
    def __init__(self, iface, canvas, ms): # msはミリ秒
        qgis.gui.QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.iface = iface

        self.ms = ms
        # canvasMoveEventで設定した秒数（msで設定）経過したら呼ばれるメソッドを設定
        self.timerMapTips = QTimer( canvas )
        self.timerMapTips.timeout.connect( self.showMapTip )


    def canvasMoveEvent(self, event):
        QToolTip.hideText()
        self.timerMapTips.start(self.ms)


    def showMapTip( self ):
        self.timerMapTips.stop()

        # 表示する値を設定する。この辺は適当に変えて。
        mappos = self.toMapCoordinates(self.canvas.mouseLastXY())
        value = mappos

        if value == None:
            return
        text = str(value)
        QToolTip.showText( self.canvas.mapToGlobal( self.canvas.mouseLastXY() ), text, self.canvas )


    def deactivate(self):
        self.timerMapTips.timeout.disconnect( self.showMapTip )
