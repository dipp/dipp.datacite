#!/usr/bin/env python

import httplib2
import urlparse
import base64
import ConfigParser


# resources
DOI = 'doi'
METADATA = 'metadata'
MEDIA = 'media'

class Client:
    
    def __init__(self, user, password, endpoint, doi):
        
        self.doi = doi
        self.endpoint = endpoint
        self.auth_string = base64.encodestring('%s:%s' % (user, password))

    def _make_rest_uri(self, resource, doi=None, testMode=0):
        if testMode:
            query = 'testMode=true'
        else:
            query = ''
        path = '/'.join((resource,doi))
        uri = urlparse.urlunparse(('https',endpoint,path,'',query,''))
        return uri
   
    def get_url(self):
        """URI: https://test.datacite.org/mds/doi/{doi} where {doi} is a
        specific DOI.
        This GET request returns an URL associated with a given DOI.
        """
        h = httplib2.Http()
        uri = self._make_rest_uri(DOI,doi=self.doi)
        method = 'GET'
        headers = {
            'Accept':'application/xml',
            'Authorization':'Basic ' + self.auth_string
            }
        response, content = h.request(uri, method, headers=headers)
        return content

    def create_or_modify_doi(self):
        """URI: https://test.datacite.org/mds/doi

        POST will mint new DOI if specified DOI doesn't exist. This method will
        attempt to update URL if you specify existing DOI. Standard domains and
        quota restrictions check will be performed. A Datacentre's doiQuotaUsed
        will be increased by 1. A new record in Datasets will be created .
        """

    def get_metadata(self, testMode=0):
        """URI: https://test.datacite.org/mds/metadata/{doi} where {doi} is a
        specific DOI.

        This GET request returns the most recent version of metadata associated
        with a given DOI.
        """

        h = httplib2.Http()
        uri = self._make_rest_uri(METADATA,doi=self.doi,testMode=testMode)
        method = 'GET'
        headers = {
            'Accept':'application/xml',
            'Authorization':'Basic ' + self.auth_string
            }
        response, content = h.request(uri, method, headers=headers)
        return content

    def modify_metadata(self):
        """URI: https://test.datacite.org/mds/metadata/{doi} where {doi} is a
        specific DOI.

        This request returns the most recent version of metadata associated
        with a given DOI.

        URI: https://test.datacite.org/mds/metadata

        This request stores new version of metadata. The request body must
        contain valid XML.
        """

    def deactivate_doi(self):
        """URI: https://test.datacite.org/mds/metadata/{doi} where {doi} is a
        specific DOI.

        This  DELETE request marks a dataset as 'inactive'. To activate it again, POST
        new metadata or set the isActive-flag in the user interface.
        """

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
    print "a cli application. one day..."

if __name__ == '__main__':

    doi = '10.5072/DIPP-TEST1'

    # read configuration
    config_file = "/files/etc/datacite/dev.conf"
    config = ConfigParser.RawConfigParser()
    config.read(config_file)
    user = config.get('DataCite','user')
    password = config.get('DataCite','password')
    endpoint = config.get('DataCite','endpoint')

    x = Client(user, password, endpoint, doi)
    #print x.get_metadata(testMode=0)
    print x.get_url()

