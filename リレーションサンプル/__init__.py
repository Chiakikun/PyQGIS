# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .relation_sample import RelationSample
    return RelationSample(iface)
