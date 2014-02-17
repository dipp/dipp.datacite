#!/usr/bin/env python

import httplib2
import argparse
import urlparse
import base64
import codecs
import logging
import os.path
import ConfigParser
from resources import DOI, METADATA
from endpoints import ENDPOINTS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

"""https://mds.datacite.org/static/apidoc"""

class Client:
    
    def __init__(self, user, password, endpoint, testMode=False):
        
        self.endpoint = endpoint
        self.testMode = testMode
        self.auth_string = base64.encodestring('%s:%s' % (user, password))

    def _make_rest_uri(self, resource, doi=None):
        if self.testMode:
            query = 'testMode=true'
        else:
            query = ''
            
        if doi:
            path = '/'.join((resource,doi))
        else:
            path = resource
        uri = urlparse.urlunparse(('https',self.endpoint,path,'',query,''))
        logger.info(uri)
        return uri
   
    def get_url(self, doi):
        """URI: https://test.datacite.org/mds/doi/{doi} where {doi} is a
        specific DOI.
        This GET request returns an URL associated with a given DOI.
        """
        h = httplib2.Http()
        uri = self._make_rest_uri(DOI,doi=doi)
        method = 'GET'
        headers = {
            'Accept':'application/xml',
            'Authorization':'Basic ' + self.auth_string
            }   
        response, content = h.request(uri, method, headers=headers)
        logger.info(response['status'])
        return content

    def create_or_modify_doi(self, doi, url):
        """URI: https://test.datacite.org/mds/doi

        POST will mint new DOI if specified DOI doesn't exist. This method will
        attempt to update URL if you specify existing DOI. Standard domains and
        quota restrictions check will be performed. A Datacentre's doiQuotaUsed
        will be increased by 1. A new record in Datasets will be created .
        """
        h = httplib2.Http()
        uri = self._make_rest_uri(DOI,doi=doi)
        method = 'PUT'
        body_unicode = "doi=%s\n url=%s" % (doi, url)
        body = body_unicode.encode('utf-8')
        headers = {
            'Content-Type':'text/plain;charset=UTF-8',
            'Authorization':'Basic ' + self.auth_string
            }
        
        response, content = h.request(uri, method, body=body, headers=headers)
        status = response['status']
        logger.info(status)
        return status, content
    
    def post_metadata(self, metadata):
        """ posts new metadata but does not register the url
        """
        h = httplib2.Http()
        uri = self._make_rest_uri(METADATA)
        method = 'POST'
        body = metadata.encode('utf-8')
        headers = {
            'Content-Type':'application/xml;charset=UTF-8',
            'Authorization':'Basic ' + self.auth_string
            }   
        response, content = h.request(uri, method, body=body, headers=headers)
        status = response['status']
        logger.info(status)
        return status, content

    def get_metadata(self, doi, testMode=0):
        """URI: https://test.datacite.org/mds/metadata/{doi} where {doi} is a
        specific DOI.

        This GET request returns the most recent version of metadata associated
        with a given DOI.
        """

        h = httplib2.Http()
        uri = self._make_rest_uri(METADATA,doi=doi)
        method = 'GET'
        headers = {
            'Accept':'application/xml',
            'Authorization':'Basic ' + self.auth_string
            }
        response, content = h.request(uri, method, headers=headers)
        status = response['status']
        logger.info(status)
        return status, content


    def modify_metadata(self):
        """URI: https://test.datacite.org/mds/metadata/{doi} where {doi} is a
        specific DOI.

        This request returns the most recent version of metadata associated
        with a given DOI.

        URI: https://test.datacite.org/mds/metadata

        This request stores new version of metadata. The request body must
        contain valid XML.
        """

    def deactivate_doi(self,doi):
        """URI: https://test.datacite.org/mds/metadata/{doi} where {doi} is a
        specific DOI.

        This  DELETE request marks a dataset as 'inactive'. To activate it again, POST
        new metadata or set the isActive-flag in the user interface.
        """
        h = httplib2.Http()
        uri = self._make_rest_uri(METADATA,doi=doi)
        method = 'DELETE'
        headers = {
            'Authorization':'Basic ' + self.auth_string
            }
        response, content = h.request(uri, method, headers=headers)
        logger.info(response['status'])
        return content

    def get_media(self):
        """URI: https://test.datacite.org/mds/media/{doi} where {doi} is a
        specific DOI.

        This GET request returns list of pairs of media type and URLs associated
        with a given DOI.
        """

    def add_media(self):
        """URI: https://test.datacite.org/mds/media/{doi} where {doi} is a
        specific DOI.

        POST will add/update media type/urls pairs to a DOI. Standard domain
        restrictions check will be performed.
        """

def main():

    parser = argparse.ArgumentParser(description='Manages DOIs at DataCite')
    parser.add_argument('-d','--doi', help='registered DOI')
    parser.add_argument('-c','--conf', help='Configuration file with access data')
    parser.add_argument('-n','--dry-run', help='The request will not change the database nor will the DOI handle be registered or updated')
    

if __name__ == '__main__':

    #doi = '10.5072/DIPP-TEST1'
    doi = '10.5072/DIPP-TEST2'
    url = 'http://www.dipp.nrw.de/doi1'
    md = codecs.open('../../example.xml', 'r', encoding='utf-8').read()
    test = False

    # read configuration
    
    config_file = "/files/etc/datacite/dev.conf"
    if os.path.isfile(config_file):
        config = ConfigParser.RawConfigParser()
        config.read(config_file)
        user = config.get('DataCite','user')
        password = config.get('DataCite','password')
        endpoint = config.get('DataCite','endpoint')
    
        x = Client(user, password, endpoint, testMode=test)
        # print x.get_metadata(doi)
        # print x.get_url(doi)
        # print x.create_or_modify_doi()
        print x.post_metadata(md)
        #print x.create_or_modify_doi(doi, url)
        #print x.deactivate_doi(doi)
    else:
        print "%s does not exist" % config_file
    
