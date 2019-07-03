from matplotlib import pyplot as plt

from . import io, markings


def plot_blotches_for_tile(tile_id, ax=None):
    blotches = io.get_blotch_catalog()
    tile_blotches = blotches.query("tile_id == @tile_id")
    if ax is None:
        _, ax = plt.subplots()
    for _, blotch in tile_blotches.iterrows():
        m = markings.Blotch(blotch, with_center=False)
        m.plot(ax=ax)
