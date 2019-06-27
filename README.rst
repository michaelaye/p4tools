=================
Planet Four Tools
=================


.. image:: https://img.shields.io/pypi/v/p4tools.svg
        :target: https://pypi.python.org/pypi/p4tools

.. image:: https://img.shields.io/travis/michaelaye/p4tools.svg
        :target: https://travis-ci.org/michaelaye/p4tools

.. image:: https://readthedocs.org/projects/p4tools/badge/?version=latest
        :target: https://p4tools.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

Tools for Planet Four data reduction and analysis.


* Free software: MIT license
* Documentation: https://p4tools.readthedocs.io.

Installation
------------

.. code-block:: bash

     conda install -c michaelaye planetfour-catalog
     pip install p4tools

Features
--------

* Provides access to the Planet Four catalog data (see Install instructions):

.. code-block:: python

    from p4tools import io
    fans = io.get_fan_catalog()
    blotches = io.get_blotch_catalog()
    tile_coords = io.get_tile_coordinates()
    tile_urls = io.get_tile_urls()
    metadata = io.get_metadata()  # data for the HiRISE images used
    region_names = io.get_region_names()  # informal region identifiers for observation IDs
    
These functions will use the `intake` library to download the data via the links provided inside the planetfour-catalog data.
For read performance, the data is then being stored in your local storage folder that is being asked for at the first use of the `io` module of `p4tools`.
These paths are being stored in `$HOME/.p4tools.ini`.

* Enables plotting of catalog data on top of the HiRISE image tile that was used during marking
     
Updating
--------

To update `p4tools` do

.. code-block:: bash

    pip install -U p4tools
    
To update the catalog, first you need to get new download links by doing 

.. code-block:: bash

    conda update -c michaelaye planetfour-catalog
    
and after that, because `p4tools` caches the catalog items, you need to provide the parameter `update=True` when using the access functions, like so:

.. code-block:: python
    
    from p4tools import io
    fans = io.get_fan_catalog(update=True)
    
which will trigger a new download.

Credits
---------

This package was created with Cookiecutter_ and the forked `michaelaye/cookiecutter-pypackage-conda`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`michaelaye/cookiecutter-pypackage-conda`: https://github.com/michaelaye/cookiecutter-pypackage-conda
