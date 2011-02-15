#!/usr/bin/env python

from constants import *
import os.path

HTML_TEMPLATE="""<html><head><title>MedRec %(filename)s</title></head>
<body>
<p>Original lists</p>
<table border=1>
<tr><td style="background-color:#B892CA">%(original_list_1)s</td>
<td style="background-color:#95A7CA">%(original_list_2)s</td></tr>
</table>
<p>Reconciliation</p>
<table border=1>
%(reconciled)s
%(unreconciled)s
</table>
<p>Hooper's Indexing Consistency (for complete reconciliation): %(hoopers)1.7f</p>
</body>
</html>
"""

RECONCILED_TEMPLATE="""<tr><td style="background-color:green;color:white">%(reconciled)s</td></tr>"""
UNRECONCILED_TEMPLATE="""<tr><td><table border=1><tr><td style="background-color:#B892CA">%(unreconciled_list_1)s</td>
<td style="background-color:#95A7CA">%(unreconciled_list_2)s</td></tr></table></td></tr>"""

def reconciliation_to_string(rec):
    if rec.med1.normalized_string==rec.med2.normalized_string or rec.strength==1.0:
        return str(rec.med1)
    else:
        return "%1.2f match (%s) between %s and %s" % (rec.strength, rec.mechanism, rec.med1, rec.med2)

def output_html(current_l1, current_l2, l1, l2, rec, output_filename):
    f=open(output_filename, "w")
    reconciled_list="<br>\n".join([reconciliation_to_string(x) for x in rec])
    original_1="<br>\n".join([str(x) for x in current_l1])
    original_2="<br>\n".join([str(x) for x in current_l2])
    if len(l1)>0:
        unrec_1="<br>\n".join([str(x) for x in l1])
    else:
        unrec_1="<br>"+"&nbsp;"*10+"\n<br>\n"
    if len(l2)>0:
        unrec_2="<br>\n".join([str(x) for x in l2])
    else:
        unrec_2="<br>"+"&nbsp;"*10+"\n<br>\n"
    unreconciled=UNRECONCILED_TEMPLATE % {"unreconciled_list_1": unrec_1,
                                          "unreconciled_list_2": unrec_2}
    hoopers=float(len(rec))/float(len(rec)+len(l1)+len(l2))
    reconciled=RECONCILED_TEMPLATE % {"reconciled": reconciled_list}
    f.write(HTML_TEMPLATE % {"original_list_1": original_1,
                             "original_list_2": original_2,
                             "reconciled": reconciled,
                             "unreconciled": unreconciled,
                             "filename": os.path.split(output_filename)[1],
                             "hoopers": hoopers,
                             })
    f.close()
