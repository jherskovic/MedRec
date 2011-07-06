#!/usr/bin/python
"""
html_output.py

Contains templates and functions to generate HTML-formatted tables for easy review.

Created by Jorge Herskovic 
Copyright (c) 2011 UTHealth School of Biomedical Informatics. All rights reserved.
"""


from constants import *
import os.path

HTML_TEMPLATE="""<html>
    <head>
        <title>MedRec %(filename)s</title>
    </head>
<body>
<style type="text/css">
    tr.list11 td {
        background-color: #B892CA; color: black;
    }
    tr.list12 td {
        background-color: #c19ee3; color: black;
    }
    tr.list21 td {
        background-color: #95A7CA; color: black;
    }
    tr.list22 td {
        background-color: #97acd7; color: black;
    }
    tr.rec1 td {
        background-color: #378109; color: white;
    }
    tr.rec2 td {
        background-color: #529012; color: white
    }
</style>
<p>Original lists</p>
<table border=1>
    <tr>
        <td><table border=0>%(original_list_1)s</table></td>
        <td><table border=0>%(original_list_2)s</table></td>
    </tr>
</table>
<p>Reconciliation</p>
<table border=1>
    <tr>
        <td><table border=0>%(reconciled)s</table></td>
    </tr>
    <tr>
        <td><table border=0>%(unreconciled_list_1)s</table></td>
        <td><table border=0>%(unreconciled_list_2)s</table></td>
    </tr>
</table>
<p>Hooper's Indexing Consistency (for complete reconciliation): %(hoopers)1.7f</p>
</body>
</html>
"""


TEMPLATE_1=['<tr class="list11"><td>%s</td></tr>', '<tr class="list12"><td>%s</td></tr>']
TEMPLATE_2=['<tr class="list21"><td>%s</td></tr>', '<tr class="list22"><td>%s</td></tr>']
REC_TEMPLATE=['<tr class="rec1"><td>%s</td></tr>', '<tr class="rec2"><td>%s</td></tr>']

def reconciliation_to_string(rec):
    if rec.med1.normalized_string==rec.med2.normalized_string or rec.strength==1.0:
        return str(rec.med1)
    else:
        return "%1.2f match (%s) between %s and %s" % (rec.strength, rec.mechanism, rec.med1, rec.med2)

def extend_list_by_repeating(orig_list, desired_length):
    orig_len=len(orig_list)
    new_list=[orig_list[x % orig_len] for x in xrange(desired_length)]
    return new_list
    
def output_html(current_l1, current_l2, l1, l2, rec, output_filename):
    f=open(output_filename, "w")
    
    reconciled_list=[reconciliation_to_string(x) for x in rec]
    rec_template_to_size=extend_list_by_repeating(REC_TEMPLATE, len(reconciled_list))
    reconciled_list="\n".join([x[0] % x[1] for x in zip(rec_template_to_size, reconciled_list)])
    
    original_1=[str(x) for x in current_l1]
    o1_template_to_size=extend_list_by_repeating(TEMPLATE_1, len(original_1))
    
    original_2=[str(x) for x in current_l2]
    o2_template_to_size=extend_list_by_repeating(TEMPLATE_2, len(original_2))
    
    original_1="\n".join([x[0] % x[1] for x in zip(o1_template_to_size, original_1)])
    original_2="\n".join([x[0] % x[1] for x in zip(o2_template_to_size, original_2)])
    
    if len(l1)>0:
        unrec_1=[str(x) for x in l1]
        unrec_1_template=extend_list_by_repeating(TEMPLATE_1, len(unrec_1))
        unrec_1="\n".join([x[0] % x[1] for x in zip(unrec_1_template, unrec_1)])
    else:
        unrec_1="\n".join([x[0] % x[1] for x in zip(TEMPLATE_1, ["",""])])
    if len(l2)>0:
        unrec_2=[str(x) for x in l2]
        unrec_2_template=extend_list_by_repeating(TEMPLATE_2, len(unrec_2))
        unrec_2="\n".join([x[0] % x[1] for x in zip(unrec_2_template, unrec_2)])
    else:
        unrec_2="\n".join([x[0] % x[1] for x in zip(TEMPLATE_2, ["",""])])
    #unreconciled=UNRECONCILED_TEMPLATE % {"unreconciled_list_1": unrec_1,
    #                                      "unreconciled_list_2": unrec_2}
    hoopers=float(len(rec))/float(len(rec)+len(l1)+len(l2))
    #reconciled=RECONCILED_TEMPLATE % {"reconciled": reconciled_list}
    f.write(HTML_TEMPLATE % {"original_list_1": original_1,
                             "original_list_2": original_2,
                             "reconciled": reconciled_list,
                             "unreconciled_list_1": unrec_1,
                             "unreconciled_list_2": unrec_2,
                             "filename": os.path.split(output_filename)[1],
                             "hoopers": hoopers,
                             })
    f.close()
