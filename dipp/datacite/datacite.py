#!/usr/bin/env python

import httplib2
import argparse
import urlparse
import base64
import codecs
import logging
import sys
import string
import os.path
import ConfigParser
from resources import DOI, METADATA

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)
log_string = "%s API %s method: status %s"

# https://mds.datacite.org/static/apidoc

class Client:
    
    def __init__(self, user, password, prefix, endpoint, testMode=False):
        
        self.endpoint = endpoint
        self.prefix = prefix
        self.testMode = testMode
        self.auth_string = base64.encodestring('%s:%s' % (user, password))

    def _make_rest_uri(self, resource, doi=None):
        """create the uri for the restfull webservice of datacite"""
        if self.testMode:
            query = 'testMode=true'
        else:
            query = ''
            
        if doi:
            path = '/'.join((resource, doi))
        else:
            path = resource
        
        if not self.endpoint:
            logger.info('No valid endpoint specified.')
            return None
        else:
            return urlparse.urlunparse(('https', self.endpoint, path, '', query, ''))
    
    def validate_doi(self, doi):
        """check if the doi contains only the recommended characters
        i'm pretty sure this could be done more elegant with reg exp...
        """  
        separator = '/'
        allowed = list(string.ascii_lowercase) + \
                  ['-', '.', '_', '+', ':', '/'] + \
                  [str(i) for i in range(0, 10)]
                   
        parts = doi.strip().lower().split(separator)
        
        validity = True
        reason = ""
        if len(parts) < 2:
            validity = False
            reason = "separator '%s' missing" % separator
        elif parts[0] != self.prefix:
            validity = False
            reason = "wrong prefix, should be '%s'" % self.prefix
        else:
            for x in parts[1]:
                if x not in allowed:
                    validity = False
                    reason = "character '%s' not allowed" % x
                    break
        logger.info('%s valid: %s, %s' % (doi, validity, reason))
        return validity

    def get_url(self, doi):
        """URI: https://test.datacite.org/mds/doi/{doi} where {doi} is a
        specific DOI.
        This GET request returns an URL associated with a given DOI.
        """
        h = httplib2.Http()
        resource = DOI
        method = 'GET'
        uri = self._make_rest_uri(resource, doi=doi)
        if not uri:
            return None, None
        else:
            headers = {
                'Accept':'application/xml',
                'Authorization':'Basic ' + self.auth_string
                }   
            response, content = h.request(uri, method, headers=headers)
            status = response['status']
            logger.info(log_string % (resource, method, status))
            return status, content

    def create_or_modify_doi(self, doi, url):
        """URI: https://test.datacite.org/mds/doi

        POST will mint new DOI if specified DOI doesn't exist. This method will
        attempt to update URL if you specify existing DOI. Standard domains and
        quota restrictions check will be performed. A Datacentre's doiQuotaUsed
        will be increased by 1. A new record in Datasets will be created .
        """
        h = httplib2.Http()
        resource = DOI
        method = 'PUT'
        uri = self._make_rest_uri(resource, doi=doi)
        body_unicode = "doi=%s\n url=%s" % (doi, url)
        body = body_unicode.encode('utf-8')
        headers = {
            'Content-Type':'text/plain;charset=UTF-8',
            'Authorization':'Basic ' + self.auth_string
            }
        
        response, content = h.request(uri, method, body=body, headers=headers)
        status = response['status']
        logger.info(log_string % (resource, method, status))
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
        logger.info('metadata API - post, %s ' % status)
        return status, content

    def get_metadata(self, doi):
        """URI: https://test.datacite.org/mds/metadata/{doi} where {doi} is a
        specific DOI.

        This GET request returns the most recent version of metadata associated
        with a given DOI.
        """

        h = httplib2.Http()
        uri = self._make_rest_uri(METADATA, doi=doi)
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

    def deactivate_doi(self, doi):
        """URI: https://test.datacite.org/mds/metadata/{doi} where {doi} is a
        specific DOI.

        This  DELETE request marks a dataset as 'inactive'. To activate it again, POST
        new metadata or set the isActive-flag in the user interface.
        """
        h = httplib2.Http()
        uri = self._make_rest_uri(METADATA, doi=doi)
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
    parser.add_argument('doi', help='DOI')
    parser.add_argument('-u', '--url', help='Url of article')
    parser.add_argument('-c', '--conf', required=True, help='Configuration file with access data')
    parser.add_argument('-n', '--dry-run', action='store_true', dest='testMode', help='The request will not change the database nor will the DOI handle be registered or updated')
    
    args = parser.parse_args()
    config_file = args.conf

    if os.path.isfile(config_file):
        config = ConfigParser.RawConfigParser()
        config.read(config_file)
        user = config.get('DataCite','user')
        prefix = config.get('DataCite','prefix')
        password = config.get('DataCite','password')
        endpoint = config.get('DataCite','endpoint')
    else:
        print "%s does not exist" % config_file
        sys.exit()

    logger.info('user:   %s' % user)
    logger.info('prefix: %s' % prefix)

    client = Client(user, password, prefix, endpoint, testMode=args.testMode)
    print client.get_url(args.doi)
    print client.validate_doi(args.doi)

if __name__ == '__main__':

    #doi = '10.5072/DIPP-TEST1'
    doi = '10.5072/DIPP-TEST6'
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
        prefix = config.get('DataCite','prefix')
        endpoint = config.get('DataCite','endpoint')
    
        x = Client(user, password, prefix, endpoint, testMode=test)
        # print x.get_metadata(doi)
        
        # print x.create_or_modify_doi()
        #print x.post_metadata(md)
        #print x.create_or_modify_doi(doi, url)
        #print x.deactivate_doi(doi)
        print prefix
        print doi, x.validate_doi(doi)
        doi = ""
        print doi, x.validate_doi(doi)
        
        doi = "10.5072/SDFas-sdf123"
        print doi, x.validate_doi(doi)
        
        doi = "10.5072sdfas-sdf"
        print doi, x.validate_doi(doi)
        
        doi = "10.5072/sdfas#sdf"
        print doi, x.validate_doi(doi)
        
        doi = "10.5073/sdfas#sdf"
        print doi, x.validate_doi(doi)
        
        doi = "10.5072/sdfas/sdf"
        print doi, x.validate_doi(doi)
        
    else:
        print "%s does not exist" % config_file
    
