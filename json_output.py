#!/usr/bin/env python
# encoding: utf-8
"""
json_output.py

Created by Jorge Herskovic on 2011-09-19.
Copyright (c) 2011 UTHealth School of Biomedical Informatics. All rights reserved.
"""

import sys
import os
import json

def serialize_sets_as_lists(thing):
    if isinstance(thing, set):
        return list(thing)
    raise TypeError("I don't know how to serialize %r" % thing)

def output_json(current_l1, current_l2, l1, l2, rec, output_filename=None):
    representation={'original_list_1': [str(x) for x in current_l1],
                    'original_list_2': [str(x) for x in current_l2],
                    'new_list_1': [x.dictionary for x in l1],
                    'new_list_2': [x.dictionary for x in l2],
                    'reconciled': [x.as_dictionary() for x in rec]
                    }
    if output_filename is not None:
        f=open(output_filename, 'w')
        json.dump(representation, f, indent=4, default=serialize_sets_as_lists)
        f.close()
    else:
        return json.dumps(representation, indent=4)