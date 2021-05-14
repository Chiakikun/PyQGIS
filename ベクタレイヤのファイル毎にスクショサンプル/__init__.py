# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .screenshot_sample import ScreenShotSample
    return ScreenShotSample(iface)
