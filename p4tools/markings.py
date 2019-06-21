import math
from math import cos, degrees, pi, radians, sin, tau
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse
from shapely import affinity
from shapely import geometry as geom

from . import io

IMG_X_SIZE = 840
IMG_Y_SIZE = 648


def set_subframe_size(ax):
    """Set plot view limit on Planet 4 subframe size."""
    ax.set_xlim(0, IMG_X_SIZE)
    ax.set_ylim(IMG_Y_SIZE, 0)


def calc_fig_size(width):
    """Calc figure height in ratio of subframes."""
    ratio = IMG_X_SIZE / IMG_Y_SIZE
    return (width, width / ratio)


class Marking:
    def __init__(self, data, scope='planet4'):
        self.data = data
        self.scope = scope


class Blotch(Ellipse):

    """Blotch management class for P4.

    Parameters
    ----------
    data : object with blotch data attributes
        object should provide attributes [`x`, `y`, `radius_1`, `radius_2`, `angle`]
    scope : {'planet4', 'hirise'}
        string that decides between using x/y or image_x/image_y as center corods
    color : str, optional
        to control the color of the mpl.Ellipse object

    Attributes
    ----------
    to_average : list
        List of cols to be averaged after clustering
    data : object with blotch data attributes, as provided by `data`
    center : tuple (inherited from matplotlib.Ellipse)
        Coordinates of center, i.e. self.x, self.y
    """
    to_average = 'x y image_x image_y angle radius_1 radius_2'.split()

    def __init__(self, data, scope='planet4', with_center=False, url_db='', **kwargs):
        self.data = data
        self.scope = scope if scope is not None else 'planet4'
        self.with_center = with_center
        self.url_db = Path(url_db)
        self.ax = None
        if scope not in ['hirise', 'planet4']:
            raise TypeError('Unknown scope: {}'.format(scope))
        try:
            self.x = data.x if scope == 'planet4' else data.image_x
            self.y = data.y if scope == 'planet4' else data.image_y
        except AttributeError:
            print("No x and y attributes in data:\n{}"
                  .format(data))
            raise AttributeError
        # default member number is 1. This is set to the cluster member inside
        # clustering execution.
        self._n_members = 1
        super(Blotch, self).__init__((self.x, self.y),
                                     data.radius_1 * 2, data.radius_2 * 2,
                                     data.angle, alpha=0.65, linewidth=2,
                                     fill=False, **kwargs)
        self.data = data

    @property
    def subframe(self):
        urls = pd.read_csv(self.url_db).set_index('tile_id').squeeze()
        url = urls.at[self.data.tile_id]
        return io.get_subframe(url)

    def show_subframe(self, ax=None, aspect='auto'):
        if ax is None:
            _, ax = plt.subplots(figsize=calc_fig_size(8))
        ax.imshow(self.subframe, origin='upper', aspect=aspect)
        ax.set_axis_off()
        self.ax = ax

    def is_equal(self, other):
        if self.data.x == other.data.x and\
           self.data.y == other.data.y and\
           self.data.image_x == other.data.image_y and\
           self.data.image_y == other.data.image_y and\
           self.data.radius_1 == other.data.radius_1 and\
           self.data.radius_2 == other.data.radius_2 and\
           self.data.angle == other.data.angle:
            return True
        else:
            return False

    def to_shapely(self):
        """Convert a markings.Blotch to shapely Ellipse.

        Code from https://gis.stackexchange.com/questions/243459/drawing-ellipse-with-shapely/243462
        """
        circ = geom.Point(self.center).buffer(1)
        ell = affinity.scale(circ, self.data.radius_1, self.data.radius_2)
        ellr = affinity.rotate(ell, self.data.angle)
        return ellr

    @property
    def area(self):
        return pi * self.data.radius_1 * self.data.radius_2

    @property
    def x1(self):
        return math.cos(math.radians(self.angle)) * self.data.radius_1

    @property
    def y1(self):
        return math.sin(self.angle) * self.data.radius_1

    @property
    def p1(self):
        return np.array(self.center) + np.array([self.x1, self.y1])

    @property
    def p2(self):
        return np.array(self.center) - np.array([self.x1, self.y1])

    @property
    def x2(self):
        return math.cos(math.radians(self.angle + 90)) * self.data.radius_2

    @property
    def y2(self):
        return math.sin(math.radians(self.angle + 90)) * self.data.radius_2

    @property
    def p3(self):
        return np.array(self.center) + np.array([self.x2, self.y2])

    @property
    def p4(self):
        return np.array(self.center) - np.array([self.x2, self.y2])

    @property
    def limit_points(self):
        return [self.p1, self.p2, self.p3, self.p4]

    def plot_center(self, ax, color='b'):
        ax.scatter(self.x, self.y, color=color,
                   s=20, marker='.')

    def plot_limit_points(self, ax, color='b'):
        for x, y in self.limit_points:
            ax.scatter(x, y, color=color, s=20, marker='o')

    @property
    def n_members(self):
        return self._n_members

    @n_members.setter
    def n_members(self, value):
        self._n_members = value

    def plot(self, color='green', ax=None):
        self.show_subframe(ax)
        ax = self.ax
        if ax is None:
            _, ax = plt.subplots()
        if color is not None:
            self.set_color(color)
        ax.add_patch(self)
        if self.with_center:
            self.plot_center(ax, color=color)

    def store(self, fpath=None):
        out = self.data
        for p in range(1, 5):
            attr = 'p' + str(p)
            point = getattr(self, attr)
            out[attr + '_x'] = point[0]
            out[attr + '_y'] = point[1]
        if 'image_id' not in out.index:
            pass
            # out['image_id'] = self.image_id
        if fpath is not None:
            out.to_hdf(str(fpath.with_suffix('.hdf')), 'df')
        out['n_members'] = self.n_members
        return out

    def __str__(self):
        s = "markings.Blotch object. Input data:\n"
        s += self.data.__str__()
        s += '\n'
        s += "N_members: {}".format(self.n_members)
        return s

    def __repr__(self):
        return self.__str__()
