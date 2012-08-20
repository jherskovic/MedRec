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
import json
import os, sys

sys.path.append(os.path.dirname(__file__))

import web, urllib, re
from smart_client_python import oauth
from smart_client_python.smart import SmartClient
from reconcile import reconcile_parsed_lists
import bz2
import cPickle as pickle
import base64
from json_output import output_json
from mapping_context import MappingContext
from lxml import  etree
from medication import make_medication
from threading import Thread

web.config.debug = False

# Basic configuration:  the consumer key and secret we'll use
# to OAuth-sign requests.
SMART_SERVER_OAUTH = {'consumer_key': 'pansharpml@apps.smartplatforms.org',
                      'consumer_secret': 'smartapp-secret'}

SERVER_ROOT = '' # e.g. '/http/path/to/app'

UCUM_URL = 'http://aurora.regenstrief.org/~ucum/ucum-essence.xml'

# The following is for multilist
MULTIPLE_LIST_SUPPORT = True
APP_UI = '/static/uthealth/MedRec.html?'
JSON_SRC = 'json_src=' + SERVER_ROOT + '/smartapp/json'
NO_SUMMARY = "no_summary"
LIST_CHOOSER = '/static/uthealth/MedRec.html?json_src=' + SERVER_ROOT + '/smartapp/json&choose_list=' + SERVER_ROOT + '/smartapp/choose_lists'

# The following is for twinlist
#MULTIPLE_LIST_SUPPORT=False
#APP_UI='/static/twinlist/html/twinlist.html?json_src='+SERVER_ROOT+'/smartapp/json'

"""
 A SMArt app serves at least two URLs: 
   * "bootstrap.html" page to load the client library
   * "index.html" page to supply the UI.
"""
urls = ( '/smartapp/index.html', 'RxReconcile',
         '/smartapp/json', 'jsonserver',
         '/smartapp/choose_lists', 'ListChooser',
         '/', 'DummyIndex')

json_data = {}

class DummyIndex:
    def GET(self):
        #web.header('Content-Type', 'text/text')
        return "This is the Pan-SHARP Medication Reconciliation smartapp. Please load it from within a SMART container."


class jsonserver:
    def GET(self):
        #print "jsonserver session contains:", session.keys()
        try:
            my_data = session.json_data
        except:
            raise Exception("Error: No data in the session.")

        session.json_data = None
        #print "Passing the following JSON to the front end:"
        #print my_data
        web.header('Content-Type', 'application/json')
        return my_data


class ListChooser:
    def GET(self):
        list1 = web.input().list1
        list2 = web.input().list2
        session.chosen_lists = (list1, list2)
        #print "Received", session.chosen_lists, "from the frontend."
        return SERVER_ROOT + '/smartapp/index.html'

print >> sys.stderr, "Starting background resource loaders"

rxnorm = None

def load_rxnorm():
    global rxnorm
    print >> sys.stderr, "Reading RXNorm"
    rxnorm = os.path.join(os.path.dirname(__file__), 'rxnorm2012')
    rxnorm = pickle.load(open(rxnorm))

rxnorm_loader = Thread(target=load_rxnorm)
rxnorm_loader.start()

treats = None

def load_treats():
    global treats
    print >> sys.stderr, "Loading treatment relationship dictionary"
    try:
        treats = os.path.join(os.path.dirname(__file__), 'treats.pickle.bz2')
        treats = pickle.load(bz2.BZ2File(treats))
    except:
        treats = {}

treats_loader = Thread(target=load_treats)
treats_loader.start()

mc = None

def build_index():
    print >> sys.stderr, "Building concept index"
    global mc
    global rxnorm_loader
    global treats_loader
    rxnorm_loader.join()
    treats_loader.join()
    # Request use of a shelf for the index for better performance.
    mc = MappingContext(rxnorm, treats,
        concept_name_index=os.path.join(os.path.dirname(__file__), "concept_names.rxnorm2012"))

index_builder = Thread(target=build_index)
index_builder.start()

ucum = None

def load_ucum():
    print >> sys.stderr, "Loading and parsing UCUM data from", UCUM_URL
    global ucum
    try:
        ucum = pickle.load(open('ucum.cache', 'rb'))
    except:
        ucum = etree.parse(UCUM_URL)
        pickle.dump(ucum, open('ucum.cache', 'wb'), pickle.HIGHEST_PROTOCOL)

ucum_loader = Thread(target=load_ucum)
ucum_loader.start()

OUTPUT_TEMPLATE = """<html>
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

de_parenthesize = lambda x: x.replace('[', '').replace(']', '').replace('{', '').replace('}', '')

def get_unit_name(abbr, ucum_xml=ucum):
    if len(abbr) == 0: return "UNITS_MISSING"

    if abbr[0] == '{':
        return de_parenthesize(abbr)
    global ucum
    global ucum_loader
    ucum_loader.join()
    root = ucum.getroot()
    nodes = [x for x in root.findall(".//unit[@Code]") if x.attrib.get('Code', '') == abbr]
    if len(nodes) != 1:
        print "Error: number of UCUM entries for %s != 1" % abbr
        return '?'
    unitname = nodes[0].find('name')
    return unitname.text

# Exposes pages through web.py
class RxReconcile(object):
    """An SMArt REST App start page"""

    def GET(self):
        # Fetch and use
        try:
            smart_oauth_header = web.input().oauth_header
        except:
            smart_oauth_header = session.oauth_header
            del session.oauth_header

        smart_oauth_header = urllib.unquote(smart_oauth_header)
        client = get_smart_client(smart_oauth_header)
        oauth_data = base64.b64encode(bz2.compress(smart_oauth_header, 9))
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
               SELECT  ?med  ?name ?rxcui ?quant ?quantunit ?freq ?frequnit ?inst ?startdate ?prov
               WHERE {
                    <""" + list_uri + """> sp:medication ?med.
                      ?med rdf:type sp:Medication .
                      ?med sp:drugName ?medc.
                      ?medc dcterms:title ?name.
                      ?medc sp:code ?code.
                      ?code dcterms:identifier ?rxcui.
                      OPTIONAL {?med sp:instructions ?inst.}
                      OPTIONAL {
                      ?med sp:quantity ?quantx.
                      ?quantx sp:value ?quant. 
                      ?quantx sp:unit ?quantunit. }
                      OPTIONAL {
                      ?med sp:frequency ?freqx.
                      ?freqx sp:value ?freq.
                      ?freqx sp:unit ?frequnit. }
                      OPTIONAL {?med sp:startDate ?startdate.}
		      OPTIONAL { ?med sp:provenance ?prov. }
                }
            """
            #print one_list_q
            return med_lists.graph.query(one_list_q)

        if len(lists) < 2:
            #print "I am lame, and therefore expect exactly two lists. Besides, with less than two, what do you expect me to reconcile?"
            web.header('Content-Type', 'text/html')
            return "<html><head></head><body>Nothing to reconcile. There were less than two lists.</body></html>"

        lists = [x for x in lists]
        my_app_ui = APP_UI
        my_app_params = []
        if len(lists) > 2:
            #print "*** WARNING *** There were %d lists. Looking for user-chosen lists." % len(lists)
            try:
                # Chosen_lists should contain URIs
                chosen_lists = session.chosen_lists
                if chosen_lists is None:
                    raise AttributeError
                session.chosen_lists = None

                # If we are here, it's because the user chose lists already
                my_app_params.append(NO_SUMMARY)
            except AttributeError:
                # No chosen lists; make the user choose.
                list_metadata = [dict(
                    URL=str(x[0].toPython()),
                    source=str(x[1].toPython()),
                    name=str(x[2].toPython()),
                    date=str(x[3].toPython()) if x[3] is not None else "") for x in lists]
                lists = [one_list(x['URL']) for x in list_metadata]
                list_info = []
                for i in range(len(lists)):
                    list_info.append({'meta': list_metadata[i], 'meds': [str(x[1]) for x in lists[i]]})
                session.json_data = json.dumps(list_info)
                session.oauth_header = web.input().oauth_header
                #print session.json_data
                #print >> sys.stderr, "Session contents:", session.keys()
                raise web.seeother(LIST_CHOOSER)
        else:
            chosen_lists = (lists[0][0], lists[1][0])

        rdf_list_1 = one_list(chosen_lists[0])
        rdf_list_2 = one_list(chosen_lists[1])
        # print "LISTS", lists
        #         print "List 1:", len(rdf_list_1), "items"
        #         for x in rdf_list_1:
        #             print "Med=", x[0]
        #             print "Name=", x[1]
        #             print "RxCUI=", x[2]
        #             print "quant=", x[3]
        #             print "quantunit=", x[4]
        #             print "freq=", x[5]
        #             print "frequnit=", x[6]
        #             print "inst=", x[7]
        #             print "startdate=", x[8]
        #             print "provenance=", x[9]
        #             print

        # Find the last fulfillment date for each medication
        #self.last_pill_dates = {}
        #for pill in pills:
        #    self.update_pill_dates(pill)

        FREQ_UNITS = {
            'd': ['days', 'daily'],
            'wk': ['weeks', 'weekly'],
            'mo': ['months', 'monthly'],
            'hr': ['hours', 'hourly'],
            'min': ['minutes', 'every minute']
        }

        def make_med_from_rdf(rdf_results):
            drugName = str(rdf_results[1].toPython())
            rxCUI = str(rdf_results[2].toPython()) if rdf_results[2] is not None else None
            quantity = rdf_results[3].toPython() if rdf_results[3] is not None else "No quantity"
            quantity_unit = str(rdf_results[4].toPython()) if rdf_results[4] is not None else "No quantity units"
            quantity_unit = get_unit_name(quantity_unit)
            frequency = rdf_results[5].toPython() if rdf_results[5] is not None else "No frequency"
            # TODO: Finish the rest of the conversion.
            freq_unit_uri = rdf_results[6]
            frequency_unit = "No frequency unit"

            if freq_unit_uri:
                (freqc, frequ) = re.match("\/\(?(?:(\d*)\.)?(d|mo|min|hr|wk)?\)?", freq_unit_uri.toPython()).groups()
                try:
                    u = FREQ_UNITS[frequ]
                    frequency_unit = u[1]
                    if freqc:
                        freqc = int(freqc)
                        if freqc > 1:
                            frequency_unit = "per %s %s" % (freqc, frequ)

                except KeyError, ValueError:
                    print >> sys.stderr, "Could not parse", freq_unit_uri
                    pass
                    #print frequency_unit

            inst = str(rdf_results[7].toPython()) if rdf_results[7] else "No instructions"
            startdate = rdf_results[8].toPython() if rdf_results[8] else "No startdate"
            provenance = rdf_results[9].toPython() if rdf_results[9] is not None else ""
            med_dict = {'name': drugName,
                        'rxCUI': rxCUI,
                        'units': quantity_unit,
                        'dose': quantity,
                        'instructions': inst,
                        'formulation': quantity_unit
            }
            #print med_dict

            if med_dict['rxCUI'] in mc._rxnorm.code_cui:
                med_dict['cuis'] = set([mc._rxnorm.code_cui[med_dict['rxCUI']]])
                #print "The CUI for", med_dict['rxCUI'], "is", med_dict['cuis']
            med = make_medication(med_dict, mc, provenance)
            return med

        global mc
        global index_builder
        # Make_med_from_rdf requires the mapping context to be ready.
        index_builder.join()
        list1 = [make_med_from_rdf(x) for x in rdf_list_1]
        list2 = [make_med_from_rdf(x) for x in rdf_list_2]

        r1, r2, rec = reconcile_parsed_lists(list1, list2, mc)

        #store a formatted list
        session.json_data = output_json(list1, list2, r1, r2, rec)
        #return output_html(list1, list2, r1, r2, rec)
        my_app_params.append(JSON_SRC)
        my_app_ui += '&'.join(my_app_params)
        #print "Redirecting to", my_app_ui
        raise web.seeother(my_app_ui)

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

    resource_tokens = {'oauth_token': oa_params['smart_oauth_token'],
                       'oauth_token_secret': oa_params['smart_oauth_token_secret']}

    server_params = {'api_base': oa_params['smart_container_api_base']}
    try:
        ret = SmartClient(SMART_SERVER_OAUTH['consumer_key'],
            server_params,
            SMART_SERVER_OAUTH,
            resource_tokens)
    except:
        import traceback

        print >> sys.stderr, traceback.format_exc()
        raise
    ret.record_id = oa_params['smart_record_id']
    return ret

app = web.application(urls, globals())
curdir = os.path.dirname(__file__)
session = web.session.Session(app, web.session.DiskStore(os.path.join(curdir, 'sessions')), )
#print >>sys.stderr, session, session.keys()

if __name__ == "__main__":
    app.run()
else:
    application = app.wsgifunc() 
