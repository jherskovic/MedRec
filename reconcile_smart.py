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

import web, urllib
from smart_client_python import oauth
from smart_client_python.smart import SmartClient
from reconcile import reconcile_parsed_lists
import bz2
import cPickle as pickle
import base64
from json_output import output_json
import random
from mapping_context import MappingContext
from lxml import  etree
from medication import make_medication

web.config.debug = False

# Basic configuration:  the consumer key and secret we'll use
# to OAuth-sign requests.
SMART_SERVER_OAUTH = {'consumer_key': 'my-app@apps.smartplatforms.org', 
                      'consumer_secret': 'smartapp-secret'}

UCUM_URL='http://aurora.regenstrief.org/~ucum/ucum-essence.xml'

"""
 A SMArt app serves at least two URLs: 
   * "bootstrap.html" page to load the client library
   * "index.html" page to supply the UI.
"""
urls = ('/smartapp/bootstrap.html', 'bootstrap',
        '/smartapp/index.html', 'RxReconcile',
        '/smartapp/json/(.+)', 'jsonserver')

json_data={}

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

class jsonserver:
    def GET(self, json_id):
        global json_data
        my_data=json_data[json_id][:]
        del json_data[json_id]
        return my_data

print "Bootstrapping reconciliation: Reading data files"
rxnorm=pickle.load(bz2.BZ2File('rxnorm.pickle.bz2'))
try:
    treats=pickle.load(bz2.BZ2File('treats.pickle.bz2'))
except:
    treats={}
print "Building concept index"
mc=MappingContext(rxnorm, treats)

print "Loading and parsing UCUM data from", UCUM_URL
ucum=etree.parse(UCUM_URL)

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
        background-col+or: #c19ee3; color: black;
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

de_parenthesize=lambda x: x.replace('[', '').replace(']', '').replace('{', '').replace('}', '')
def get_unit_name(abbr, ucum_xml=ucum):
    if abbr[0]=='{':
        return de_parenthesize(abbr)
    root=ucum.getroot()
    nodes=[x for x in root.findall(".//unit[@Code]") if x.attrib.get('Code', '') == abbr]
    if len(nodes) != 1:
        print "Error: number of UCUM entries for %s != 1" % abbr
        return '?'
    unitname=nodes[0].find('name')
    return unitname.text

def make_random_json_id(length=32):
    source='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    return ''.join( random.choice(source) for i in xrange(length) )
    
# Exposes pages through web.py
class RxReconcile(object):
    """An SMArt REST App start page"""
    def GET(self):
        global json_data
        # Fetch and use
        smart_oauth_header = web.input().oauth_header
        smart_oauth_header = urllib.unquote(smart_oauth_header)
        client = get_smart_client(smart_oauth_header)
        oauth_data=base64.b64encode(bz2.compress(smart_oauth_header, 9))
        #client = get_smart_client(oauth_data)

        # Represent the list as an RDF graph
        med_lists = client.records_X_medication_lists_GET()
 
        lists_q = """
            PREFIX dcterms:<http://purl.org/dc/terms/>
            PREFIX sp:<http://smartplatforms.org/terms#>
            PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            select ?l ?s ?sname ?d 
            where {
                ?l a sp:MedicationList.
                ?l sp:medListSource ?s.
                ?s dcterms:title ?sname.
              
                optional { ?l dcterms:date ?d }
 
            }"""
 
        lists = med_lists.graph.query(lists_q)
 
        def one_list(list_uri):
            one_list_q = """
            PREFIX dcterms:<http://purl.org/dc/terms/>
            PREFIX sp:<http://smartplatforms.org/terms#>
            PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
               SELECT  ?med  ?name ?quant ?quantunit ?freq ?frequnit ?inst ?startdate ?prov
               WHERE {
                    """ + list_uri.n3() + """ sp:medication ?med.
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
                      OPTIONAL {
                      ?med sp:provenance ?prov. }
                }
            """
            return med_lists.graph.query(one_list_q)
        
        if len(lists) < 2:
            print "I am lame, and therefore expect exactly two lists. Besides, with less than two, what do you expect me to reconcile?"
            return "<html><head></head><body>Nothing to reconcile. There were less than two lists.</body></html>"
            
        if len(lists)>2:
            print "*** WARNING *** There were %d lists, but I only used the first two." % len(lists)
        
        lists=[x for x in lists]
        
        rdf_list_1=one_list(lists[0][0])
        rdf_list_2=one_list(lists[1][0])
        print "List 1:", len(rdf_list_1), "items"
        for x in rdf_list_1:
            print "Med=", x[0].toPython()
            print "Name=", x[1].toPython()
            print "quant=", x[2].toPython()
            print "quantunit=", x[3].toPython()
            print "freq=",x[4].toPython()
            print "frequnit=",x[5].toPython()
            print "inst=",x[6].toPython()
            print "startdate=",x[7].toPython()
            print "provenance=", x[8].toPython() if x[8] is not None else ""
            print
            
        # Find the last fulfillment date for each medication
        #self.last_pill_dates = {}
        #for pill in pills:
        #    self.update_pill_dates(pill)
        
        def make_med_from_rdf(rdf_results):
            drugName=rdf_results[1].toPython()
            quantity=rdf_results[2].toPython() if rdf_results[2] is not None else ""
            quantity_unit=rdf_results[3].toPython() if rdf_results[3] is not None else ""
            quantity_unit=get_unit_name(quantity_unit)
            frequency=rdf_results[4].toPython() if rdf_results[4] is not None else ""
            # TODO: Finish the rest of the conversion.
            frequency_unit={'/d': 'daily', '/wk': 'weekly', '/mo': 'monthly', None: ''}[rdf_results[5].toPython()]
            inst=rdf_results[6].toPython()
            startdate=rdf_results[7].toPython()
            provenance=rdf_results[8].toPython if rdf_results[8] is not None else ""
            med_dict={'name': drugName,
                      'units': quantity_unit,
                      'dose': quantity,
                      'instructions': inst,
                      'formulation': quantity_unit,
                      }
            med=make_medication(med_dict, mc, provenance)
            return med
        
        list1=[make_med_from_rdf(x) for x in rdf_list_1]
        list2=[make_med_from_rdf(x) for x in rdf_list_2]
        
        r1, r2, rec=reconcile_parsed_lists(list1, list2, mc)

        #store a formatted list
        json_id=make_random_json_id()
        while json_id in json_data:
            json_id=make_random_json_id()
        json_data[json_id]=output_json(list1, list2, r1, r2, rec)
        #return output_html(list1, list2, r1, r2, rec)
        raise web.seeother('/static/MedRec.html?json_src=/smartapp/json/%s' % json_id)

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
