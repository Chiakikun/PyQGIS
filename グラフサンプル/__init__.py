# -*- coding: utf-8 -*-
def classFactory(iface):  # pylint: disable=invalid-name
    from .graph_sample import GraphSample
    return GraphSample(iface)
