README.txt

MedRec v0.01

This is Dr. Herskovic's medication reconciliation algorithm. It takes two lists
of medications and returns three lists: a reconciled list, the part of list 1 
that could not be reconciled, and the part of list 2 that could not be reconciled.

This implementation requires RXNorm, which is part of the UMLS. You can extract
RXNorm from the UMLS to use with this program by using the included 
generate_rxnorm_file.py script. You must have an RRF version of the UMLS to use 
this script. Invoke it as:
python generate_rxnorm_file.py /path/to/umls/metathesaurus rxnorm.pickle.bz2

It also requires a treatment database in a pickled bz2 file. You may ignore this 
file, and treatment intent reconciliation will be skipped. If you want to 
provide one, it should be a pickle dictionary of the form 
{'CUI_of_drug': set(['CUI_of_condition', 'CUI_of_another_condition', etc.])}

I apologize in advance, but I can not share the dataset we used to create our 
own copy of the treatment file, nor the treatment file itself. The algorithm 
will still work without it.
 
After you have your rxnorm pickled file, please try out:
python reconcile.py 

to perform a demo reconciliation.

I also included the SMARTApp version of the reconciliation algorithm. You will 
need Josh Mandel's smart client modules, available from
https://github.com/chb/smart_client_python and placed in the smart_client 
subdirectory (and, of course, all its dependencies). Try:

python reconcile_smart.py 8000 

and run it inside the SMART sandbox to play with it.