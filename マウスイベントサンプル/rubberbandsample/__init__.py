# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RubberBandSample
                                 A QGIS plugin
 RubberBandのSampleです
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-11-23
        copyright            : (C) 2019 by unemployed
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
    """Load RubberBandSample class from file RubberBandSample.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .rubberbandSample import RubberBandSample
    return RubberBandSample(iface)
