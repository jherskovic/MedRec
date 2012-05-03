'''
Created on May 3, 2012

@author: cbearden
'''

class Problem(object):
    __slots__ = ['_name', '_patient_count', '_ratio']
    def __init__(self, name, patient_count, ratio):
        self._name = name
        self._patient_count = patient_count
        self._ratio = ratio
    @property
    def name(self):
        return self._name
    @property
    def patient_count(self):
        return self._patient_count
    @property
    def ratio(self):
        return self._ratio
    def _is_lt(self, other):
        if self.ratio > other.ratio:
            return True
        elif self.ratio < other.ratio:
            return False
        elif self.patient_count > other.patient_count:
            return True
        elif self.patient_count < other.patient_count:
            return False
        elif self.name < other.name:
            return True
        else:
            return False
    def __lt__(self, other):
        return self._is_lt(other)
    def __gt__(self, other):
        return not self._is_lt(other)


class DrugProblemKB(object):
    pass