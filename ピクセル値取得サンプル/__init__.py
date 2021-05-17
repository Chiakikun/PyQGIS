# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .getrasterpixelvalue_sample import GetRasterPixelValueSample
    return GetRasterPixelValueSample(iface)
