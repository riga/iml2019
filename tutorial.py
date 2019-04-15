# coding: utf-8

"""
Helpful utilities for the "Physics-inspired feature engineering" turorial,
held at the IML workshop 2019.
"""

import os
import sys
import functools
import urllib

import numpy as np
import six


# print function with auto-flush
print_ = functools.partial(six.print_, flush=True)

# define directories and urls
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")
eos_dir = "/eos/user/m/mrieger/public/iml2019"
eos_url_pattern = "https://cernbox.cern.ch/index.php/s/xDYiSmbleT3rip4/download?path={}&files={}"

# check if we have access to /eos or not
has_eos = os.access(eos_dir, os.R_OK)
print_("eos access: {}".format("✔︎" if has_eos else "✗"), flush=True)

# if eos is accessible, amend sys.path to find shared software
# otherwise, software must be installed manually (or via requirements.txt on binder)
if has_eos:
    sys.path.insert(0, os.path.join(eos_dir, "software/lib/python2.7/site-packages"))


# eos url with arguments
def eos_url(*args):
    path = os.path.normpath("/" + "/".join(str(s) for s in args[:-1]))
    files = str(args[-1])
    return eos_url_pattern.format(urllib.quote_plus(path), urllib.quote_plus(files))


# file download helper
def download(src, dst, bar=None):
    import wget
    return wget.download(src, out=dst, bar=bar)


# gets a file from eos, passed relative to eos_dir (see abpve)
# returns the full eos path when eos is available, otherwise downloads it via cernbox and returns
# the location of the downloaded file
def get_file(eos_file):
    eos_file = eos_file.lstrip("/")
    if has_eos:
        return os.path.join(eos_dir, eos_file)
    else:
        local_path = os.path.join(data_dir, eos_file)
        if not os.path.exists(local_path):
            local_dir = os.path.dirname(local_path)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            print_("downloading {} from CERNBox".format(eos_file), flush=True)
            download(eos_url(eos_file), local_path)
        return local_path


# data loading helper
def load_lbn_data(level="low", sorting="gen", kind="train"):
    """
    Loads an LBN dataset defined by *level* ("low", "high" or "mixed"), *sorting* ("gen" or "pt"),
    and *kind* ("train" or "test"). The return value is dictionary-like object with two keys,
    "labels" and "features", which point to plain numpy arrays.
    """
    levels = ("low", "high", "mixed")
    if level not in levels:
        raise ValueError("unknown dataset level '{}', must be one of {}".format(
            level, ",".join(levels)))

    sortings = ("gen", "pt")
    if sorting not in sortings:
        raise ValueError("unknown dataset sorting '{}', must be one of {}".format(
            sorting, ",".join(sortings)))

    kinds = ("train", "test")
    if kind not in kinds:
        raise ValueError("unknown dataset kind '{}', must be one of {}".format(
            kind, ",".join(kinds)))

    # download the file from CERNBox when not eos is not accessible
    local_path = get_file("lbn/data/{}_{}_{}.npz".format(level, sorting, kind))

    # open and return the numpy file object
    return np.load(local_path)
