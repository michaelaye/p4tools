import configparser
import logging
import os
import shutil
from pathlib import Path
from urllib.error import URLError

import matplotlib.image as mplimg

try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve


pkg_name = __name__.split(".")[0]

configpath = Path.home() / ".{}.ini".format(pkg_name)

LOGGER = logging.getLogger(__name__)


def get_config():
    """Read the configfile and return config dict.

    Returns
    -------
    dict
        Dictionary with the content of the configpath file.
    """
    if not configpath.exists():
        raise IOError("Config file {} not found.".format(str(configpath)))
    else:
        config = configparser.ConfigParser()
        config.read(str(configpath))
        return config


def get_data_root():
    d = get_config()
    data_root = Path(d["planet4_db"]["path"]).expanduser()
    data_root.mkdir(exist_ok=True, parents=True)
    return data_root

def set_database_path(dbfolder):
    """Use to write the database path into the config.

    Parameters
    ----------
    dbfolder : str or pathlib.Path
        Path to where planet4 will store clustering results by default.
    """
    try:
        d = get_config()
    except IOError:
        d = configparser.ConfigParser()
        d["planet4_db"] = {}
    d["planet4_db"]["path"] = dbfolder
    with configpath.open("w") as f:
        d.write(f)
    print("Saved database path into {}.".format(configpath))


# module global data_root !
if not configpath.exists():
    print("No configuration file {} found.\n".format(configpath))
    savepath = input("Please provide the path where you want to store planet4 results:")
    set_database_path(savepath)
else:
    data_root = get_data_root()


def get_subframe(url):
    """Download image if not there yet and return numpy array.

    Takes a data record (called 'line'), picks out the image_url.
    First checks if the name of that image is already stored in
    the image path. If not, it grabs it from the server.
    Then uses matplotlib.image to read the image into a numpy-array
    and finally returns it.
    """
    targetpath = data_root / "images" / os.path.basename(url)
    targetpath.parent.mkdir(exist_ok=True)
    if not targetpath.exists():
        LOGGER.info("Did not find image in cache. Downloading ...")
        try:
            path = urlretrieve(url)[0]
        except URLError:
            msg = "Image not in cache. Cannot download subframe image. No internet?"
            LOGGER.error(msg)
            return None
        LOGGER.debug("Done.")
        shutil.move(path, str(targetpath))
    else:
        LOGGER.debug("Found image in cache.")
    im = mplimg.imread(targetpath)
    return im