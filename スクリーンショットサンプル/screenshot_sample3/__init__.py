# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ScreenShotSample3
                                 A QGIS plugin
 ラスタレイヤ毎にスクリーンショット
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-02-04
        copyright            : (C) 2020 by Chiakikun
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
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ScreenShotSample3 class from file ScreenShotSample3.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .screenshot_sample3 import ScreenShotSample3
    return ScreenShotSample3(iface)
