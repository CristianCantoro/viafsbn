#! /usr/bin/env python
# *-* coding: utf-8 *-*

import requests
import logging
from item import SbnItem, ViafItem

# logging
logger = logging.getLogger('viafsbn')

# globals
SBNPERMURL = 'http://id.sbn.it/af/{sbn_code}'
VIAFPERMURL = 'http://viaf.org/viaf/{viaf_code}'


def search_viaf(viaf_code):
    viafurl = VIAFPERMURL.format(viaf_code=viaf_code)
    req_viaf = requests.get(viafurl)
    if req_viaf.ok:
        viaf_item = ViafItem(code=viaf_code,
                             text=req_viaf.text,
                             url=req_viaf.url
                             )
        return viaf_item


def search_sbn(sbn_code, opere=False):
    sbnurl = SBNPERMURL.format(sbn_code=sbn_code.replace('\\', '/'))
    req_sbn = requests.get(sbnurl)
    if req_sbn.ok:
        try:
            sbn_item = SbnItem(code=sbn_code,
                               text=req_sbn.text,
                               url=req_sbn.url,
                               get_works=opere
                               )
        except IndexError:
            sbn_item = None

        return sbn_item
