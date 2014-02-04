#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 12/16/13 at 11:26 AM
# myshelf.py
"""myshelf.py contains a minimally-useful version of shelve based on semidbm instead of anydbm,
to support the MedRec package."""

__author__ = 'Jorge R. Herskovic <jherskovic@gmail.com>'

import cPickle as pickle
from sqlite_dict import SQLiteDict

class shelve(object):
    def __init__(self, filename, flag, protocol):
        self._my_file = SQLiteDict(filename, threadsafe=False)
        self._protocol = protocol

    def __iter__(self):
        for key in self._my_file:
            yield key

    def __getitem__(self, item):
        return pickle.loads(self._my_file[item])

    def __setitem__(self, key, value):
        self._my_file[key] = pickle.dumps(value, self._protocol)

    def close(self):
        self._my_file.close()
        self._my_file = None

    def __del__(self):
        if self._my_file is not None:
            self._my_file.close()

    def keys(self):
        return self._my_file.keys()

    def __len__(self):
        return len(self.keys())

    @classmethod
    def open(cls, filename, flag='c', protocol=pickle.HIGHEST_PROTOCOL):
        """Alternate constructor to mimic the semantics of the python shelve module."""
        return cls(filename, flag, protocol)
