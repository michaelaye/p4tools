# -*- coding: utf-8 -*-

"""Main module."""
from importlib import resources
import pandas as pd


def get_region_names():
    with resources.path("p4_tools.data", "obsid_region_names.csv") as p:
        return pd.read_csv(p)

