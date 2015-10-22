import unittest
import sys
import os.path
import ConfigParser

from dipp.datacite.datacite import Client

config_file = "/files/etc/datacite/dev.conf"

if os.path.isfile(config_file):
    config = ConfigParser.RawConfigParser()
    config.read(config_file)
    user = config.get('DataCite','user')
    password = config.get('DataCite','password')
    prefix = config.get('DataCite','prefix')
    endpoint = config.get('DataCite','endpoint')
else:
    print "%s not found, exiting." % config_file
    sys.exit()


client = Client(user, password, prefix, endpoint, testMode=False)

class TestDataCite(unittest.TestCase):
    
    def test_valid_doi(self):
        # correct DOI
        self.assertTrue(client.validate_doi('10.5072/DIPP-TEST1')[0])
        # wrong prefix
        self.assertFalse(client.validate_doi('10.5000/DIPP-TEST1')[0])
        # wrong character
        self.assertFalse(client.validate_doi('10.5072/DIPP~TEST1')[0])
        # missing separator
        self.assertFalse(client.validate_doi('10.5072DIPP~TEST1')[0])

if __name__ == '__main__':
    unittest.main()

