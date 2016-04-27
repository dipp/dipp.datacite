Managing DOIs at DataCite (dipp.datacite)
=========================================

.. image:: https://travis-ci.org/dipp/dipp.datacite.svg?branch=master
    :target: https://travis-ci.org/dipp/dipp.datacite


Posting, registering and updating DOI at the `DataCite Metadata Store 
<http://mds.datacite.org/>`_.

Installation
------------

DataCite does not support bare HTTP, thus we need to install the Python SSL library.
To avoid problems when using datcite from within plone we need the egg unzipped:

.. code-block:: bash

    $ easy_install --always-unzip ssl 

The Python modules are installed by running:

.. code-block:: bash

    $ easy_install -f http://alkyoneus.hbz-nrw.de/dist -n -U dipp.datacite

Note that test.datacite.org uses SNI, which is not supported by httplib2/Python 2.4 



