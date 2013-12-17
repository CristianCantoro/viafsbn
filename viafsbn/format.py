#! /usr/bin/env python
# *-* coding: utf-8 *-*

import json

def json_format(item, tipo, opere=False):
    basedict = {'name': item.name,
                'type': tipo,
                'code': item.code,
                'url': item.url
                }

    if tipo == 'SBN' and opere:
        basedict['opere'] = [{'titolo': o.titolo,
                              'autori': o.autori
                              }
                             for o in item.opere
                             ]

    if tipo == 'VIAF':
        basedict['links'] = vars(item.links)

    return json.dumps(basedict)
