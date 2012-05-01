"""
Example SMArt REST Application: Parses OAuth tokens from
browser-supplied cookie, then provides a list of which prescriptions
will need to be refilled soon (based on dispense day's supply + date).

Josh Mandel
Children's Hospital Boston, 2010

Modified by J Herskovic to create the MedRec SMART App. This is badly cobbled 
together from Josh's smart_rx_reminder demo. Be gentle.

UTHealth SBMI, 2011
"""

import web,  urllib
import datetime
import smart_client_python
from smart_client_python import oauth
from smart_client_python.smart import SmartClient
from smart_client_python.common.util import serialize_rdf
from reconcile import reconcile_lists
import bz2
import cPickle as pickle
import base64
from html_output import output_html
import random
from mapping_context import MappingContext

web.config.debug = False

# Basic configuration:  the consumer key and secret we'll use
# to OAuth-sign requests.
SMART_SERVER_OAUTH = {'consumer_key': 'my-app@apps.smartplatforms.org', 
                      'consumer_secret': 'smartapp-secret'}


"""
 A SMArt app serves at least two URLs: 
   * "bootstrap.html" page to load the client library
   * "index.html" page to supply the UI.
"""
urls = ('/smartapp/bootstrap.html', 'bootstrap',
        '/smartapp/index.html',     'GetDate',
        '/smartapp/reconcile.html', 'RxReconcile')

# Required "bootstrap.html" page just includes SMArt client library
class bootstrap:
    def GET(self):
        return """<!DOCTYPE html>
                   <html>
                    <head>
                     <script src="http://sample-apps.smartplatforms.org/framework/smart/scripts/smart-api-client.js"></script>
                    </head>
                    <body></body>
                   </html>"""

print "Bootstrapping reconciliation: Reading data files"
rxnorm=pickle.load(bz2.BZ2File('rxnorm.pickle.bz2'))
try:
    treats=pickle.load(bz2.BZ2File('treats.pickle.bz2'))
except:
    treats={}
print "Building concept index"
mc=MappingContext(rxnorm, treats)

OUTPUT_TEMPLATE="""<html>
    <head>
        <title>MedRec %(filename)s</title>
        <script src="http://sample-apps.smartplatforms.org/framework/smart/scripts/smart-api-page.js"></script>
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
<!-- Hooper's Indexing Consistency (for complete reconciliation): %(hoopers)1.7f -->
</body>
</html>
"""

DATE_TEMPLATE="""<html>
    <head>
        <title>MedRec dates</title>
        <script src="http://sample-apps.smartplatforms.org/framework/smart/scripts/smart-api-page.js"></script>
    </head>
    <body>
    <form action="/smartapp/reconcile.html" method="GET">
    <p>Reconcile the medications before this date to the medications after this date: <input type="text" name="recdate" />
      <input type="hidden" name="cookie_name" value="%s">
    </p><p><input type="submit" value="Submit" /></p></form>
    </body>
</html>"""



class GetDate(object):
    def GET(self):
        smart_oauth_header = web.input().oauth_header
        smart_oauth_header = urllib.unquote(smart_oauth_header)
        #client = get_smart_client(smart_oauth_header)
        oauth_data=base64.b64encode(bz2.compress(smart_oauth_header, 9))
        return DATE_TEMPLATE % oauth_data
 

# Exposes pages through web.py
class RxReconcile(object):
    """An SMArt REST App start page"""
    def GET(self):
        # Fetch and use
        oauth_data=bz2.decompress(base64.b64decode(web.input().cookie_name))
        print oauth_data
        client = get_smart_client(oauth_data)

        # Represent the list as an RDF graph
        meds = client.records_X_medications_GET().graph

        # Find a list of all fulfillments for each med.
        q = """
            PREFIX dc:<http://purl.org/dc/elements/1.1/>
            PREFIX dcterms:<http://purl.org/dc/terms/>
            PREFIX sp:<http://smartplatforms.org/terms#>
            PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
               SELECT  ?med ?name ?quantx ?quant ?quantunit ?freqx ?freq ?frequnit ?inst ?startdate
               WHERE {
                      ?med rdf:type sp:Medication .
                     ?med sp:drugName ?medc.
                      ?medc dcterms:title ?name.
                      ?med sp:instructions ?inst.
                      ?med sp:quantity ?quantx.
                      OPTIONAL {
                      ?quantx sp:value ?quant. 
                      ?quantx sp:unit ?quantunit. }
                      ?med sp:frequency ?freqx.
                      OPTIONAL {
                      ?freqx sp:value ?freq.
                      ?freqx sp:unit ?frequnit. }
                      ?med sp:startDate ?startdate.
               }
            """
        pills = meds.query(q)

        # Find the last fulfillment date for each medication
        #self.last_pill_dates = {}
        #for pill in pills:
        #    self.update_pill_dates(pill)
        list1=[]
        list2=[]
        # THIS WORKS WITH CAROL DIAZ OR BRIAN ROBINSON
        SPLIT_DATE=web.input().recdate
        for x in pills:
            #print x
            #this_pill=str(x['name'])+" "+str(x['inst'])
            this_pill=str(x[1])+" "+str(x[8]) # Now we have to access these via indices
            #if str(x['startdate'])<SPLIT_DATE:
            #if str(x[10])<SPLIT_DATE:
            #    # This drug was discontinued before the date in question. Skip.
            #    continue
            if str(x[9])<SPLIT_DATE:
                list1.append(this_pill)
            else:
                list2.append(this_pill)
        r1, r2, rec=reconcile_lists(list1, list2, mc)

        #Print a formatted list
        return output_html(list1, list2, r1, r2, rec)


header = """<!DOCTYPE html>
<html>
  <head>                     <script src="http://sample-apps.smartplatforms.org/framework/smart/scripts/smart-api-page.js"></script></head>
  <body>
"""

footer = """
</body>
</html>"""


"""Convenience function to initialize a new SmartClient"""
def get_smart_client(authorization_header, resource_tokens=None):
    oa_params = oauth.parse_header(authorization_header)
    
    resource_tokens={'oauth_token':       oa_params['smart_oauth_token'],
                     'oauth_token_secret':oa_params['smart_oauth_token_secret']}

    server_params={'api_base':            oa_params['smart_container_api_base']}

    ret = SmartClient(SMART_SERVER_OAUTH['consumer_key'], 
                       server_params, 
                       SMART_SERVER_OAUTH, 
                       resource_tokens)
    print ret
    print ret.baseURL
    ret.record_id=oa_params['smart_record_id']
    return ret

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'))

if __name__ == "__main__":
    app.run()
