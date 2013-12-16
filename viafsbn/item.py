#! /usr/bin/env python
# *-* coding: utf-8 *-*

import re
import logging
import requests
from collections import namedtuple
from lxml import html

# logging
logger = logging.getLogger('viafsbn.item')

# globals
UPDATE_DATE = re.compile(r'Data di aggiornamento')
RISULTATI = re.compile(r'Risultati: (\d*)-(\d*) di (\d*)')
BRTAG = re.compile(r'<br.*?>')
TAG = re.compile(r'<.*?>')


def remove_br_tags(data, rmwith=''):
    return BRTAG.sub(rmwith, data)


def remove_tags(data, rmwith=''):
    return TAG.sub(rmwith, data)


class Item(object):

    def __init__(self, code, text, url):
        self.code = code
        self.text = text
        self.url = url
        self.name = None
        self.opere = list()

    def __repr__(self):
        return u'Item(name={name})'.format(name=self.name.encode('utf-8'),
                                           code=self.code)

    class Work(object):

        def __init__(self):
            self.titolo = None
            self.url = None
            self.autori = None
            self.edizione = None

        def __repr__(self):
            return 'Work(titolo={titolo}, autori={autori})'.format(
                titolo=self.titolo and self.titolo.encode('utf-8'),
                autori=self.autori and self.autori.encode('utf-8'))


class SbnItem(Item):
    BASE_SBN_URL = 'http://opac.sbn.it/'

    def __init__(self, code, text, url, get_works=False):
        super(SbnItem, self).__init__(code, text, url)
        self._parse()
        if get_works:
            self._get_works()

    def _parse(self):
        doc = html.document_fromstring(self.text)
        corpo = doc.xpath("//div[@id='corpo_opac']")[0]

        tbody = doc.xpath("//div[@id='corpo_opac']/table")[0].getchildren()[0]
        trows = [tr.getchildren() for tr in tbody]
        scheda = dict()
        for row in trows:
            key = row[1].text.strip().lower().replace(' ', '_')
            value = row[2].text.strip()

            if key == 'nome_autore':
                value = row[2].getchildren()[0].text
                scheda['link_opere'] = self.BASE_SBN_URL + \
                    row[2].getchildren()[0].get('href')

            if key == 'fonti':
                value = [div.text.replace(u'\xb7', u'').strip()
                         for div in row[2].getchildren()]

            scheda[key] = value

        try:
            update_date = [row.replace('Data di aggiornamento:', '').strip()
                           for row in corpo.text_content().split('\n')
                           if UPDATE_DATE.search(row)][0]

        except:
            update_date = ''

        scheda['update'] = update_date

        Scheda = namedtuple('Scheda', ' '.join(scheda.keys()))
        self.scheda = Scheda(**{k: v
                                for k, v in scheda.iteritems()
                                })

        self.name = scheda['nome_autore'].strip()

    def _get_works(self):
        RISULTATI_XPATH = "//*[@id='corpo_opac']/div[1]/div[2]/div[2]/div[1]"

        BASE_SEARCH_URL = 'http://opac.sbn.it/opacsbn/opaclib' \
            '?db=solr_iccu&resultForward=opac/iccu/brief.jsp' \
            '&from=1&nentries={res_tot}&searchForm=opac/iccu/error.jsp' \
            '&do_cmd=search_show_cmd&item:5032:BID={code}'

        OPERE_XPATH = "//div[@id='colonna_risultati']/table[@id='records']" \
                      "/tbody"

        req_opere = requests.get(self.scheda.link_opere)
        if req_opere.ok:
            doc = html.document_fromstring(req_opere.text)
            risultati = doc.xpath(RISULTATI_XPATH)[0].text_content().strip()
            resmatch = RISULTATI.match(risultati)
            if resmatch:
                res_start = int(resmatch.group(1))
                res_stop = int(resmatch.group(2))
                res_tot = int(resmatch.group(3))

                url = BASE_SEARCH_URL.format(
                    res_tot=res_tot,
                    code='IT\\ICCU\\'+self.code)

            req_opere_tot = requests.get(url)
            if req_opere_tot.ok:
                doc = html.document_fromstring(req_opere_tot.text)
                topere = doc.xpath(OPERE_XPATH)[0].getchildren()
                topere = [row.getchildren()[3].getchildren() for row in topere]
                for op in topere:
                    opera = self.Work()
                    for div in op:
                        if div.get('class') == 'rectitolo':
                            opera.url = self.BASE_SBN_URL + \
                                div.getchildren()[0].get('href')

                            opera.titolo = div.getchildren()[0].text.strip()

                        elif div.get('class') == 'rec_3a_linea':
                            sourceline = div.sourceline
                            raw_source = req_opere_tot.\
                                text.split('\n')[sourceline-1:sourceline][0]
                            opera.edizione = remove_tags(
                                remove_br_tags(raw_source, '\n'))

                        else:
                            opera.autori = div.text

                    self.opere.append(opera)

    def __repr__(self):
        return u'SbnItem(name={name}, code={code})'.format(
            name=self.name.encode('utf-8'),
            code=repr(self.code))


class ViafItem(Item):
    JUSTLINKS = 'justlinks.json'

    def __init__(self, code, text, url):
        super(ViafItem, self).__init__(code, text, url)
        self._parse()
        self._justlinks()

    def _parse(self):
        doc = html.document_fromstring(self.text.encode('utf-8'))
        self.name = doc.xpath("//*[@id='nameEntry1']")[0].text

    def _justlinks(self):
        justlinks_url = self.url + self.JUSTLINKS
        req_links = requests.get(justlinks_url)
        if req_links.ok:
            justlinks = req_links.json()
            cleanlinks = dict([link for link in
                               map(lambda (k, v):
                                   (k, v[0])
                                   if isinstance(v, list)
                                   else None, justlinks.items()
                                   )
                               if link is not None
                               ])
            Links = namedtuple('Links', cleanlinks.keys())
            self.links = Links(**cleanlinks)

    def __repr__(self):
        return u'ViafItem(name={name}, code={code})'.format(
            name=self.name.encode('utf-8'),
            code=self.code)
