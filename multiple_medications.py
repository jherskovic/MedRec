#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 1/8/14 at 3:33 PM

__author__ = 'Jorge R. Herskovic <jherskovic@gmail.com>'

# Since __getattribute__ captures ALL attribute access (it's very obnoxious that way)
# we can't call self._contained in MultipleMedications, because that will send us into endless recursion.
# Instead, we must use object.__getattribute__(instance, <something>)
# As that is annoying, we'll shortcut it with a lambda
_gattr = lambda instance, attr_name: object.__getattribute__(instance, attr_name)


class MultipleMedications(object):
    """Represents a combination of more than one medication. Useful, for example, for matching
    Zestoretic against Lisinopril and Hydrochlorothiazide.

    All operations on the class are translated to lists of operations on the constituent medications."""

    def __init__(self, medications):
        """Takes a list of medications as an argument. All of them MUST be of the same type."""
        med_types = set([type(x) for x in medications])
        if len(med_types) > 1:
            raise TypeError("The MultipleMedications class only supports a single type of object in each instance.")
        self._contained = med_types.pop()
        self._meds = medications

    def __getattribute__(self, name):
        """Figure out if this is an attribute of the underlying medications. If it is, and it is a callable,
        return a callable that calls the attribute for each member.

        If it isn't, return the attribute for each member.

        We also special-case access to two attributes, _contained_type and _meds, that returns the actual
        objects inside.
        """
        # And we'll shortcut a self-attribute with "selfie"
        selfie = lambda attr_name: _gattr(self, attr_name)

        # We'll also need to know the type contained by this class regardless
        my_type = selfie("_contained")
        if name == "_contained_type":
            return my_type

        # And, if we've made it this far, the items contained too
        my_meds = selfie("_meds")
        if name == "_contained_meds":
            return my_meds

        # Inspect the contained type to see if the requested name is an attribute.
        attr = _gattr(my_type, name)
        # And then check to see if the attribute is actually callable
        if hasattr(attr, '__call__'):
            def newfunc(*args, **kwargs):
                return [_gattr(x, name)(*args, **kwargs) for x in my_meds]

            return newfunc
        else:
            return [_gattr(x, name) for x in my_meds]

