import pytest
import subprocess
import json
import re

# Test cases

def test_isvalid_false(request):
    test_path = request.config.getoption("--testCasePath")
    #print(test_path)
    testcase_id = request.config.getoption("--testcase_id")
    #print("\nTEST: {}".format(testcase_id))
    SIPPath = request.config.getoption("--SIPPath")    
    #print("\nSIP: {}".format(SIPPath)
    isValid = request.config.getoption("--isValid")
    #print("is valid = {}".format(isValid))   
    print("\nPytest testing {}".format(SIPPath))
    
    rawText = subprocess.check_output(['eark-validator', SIPPath], text=True).splitlines() 
    i=0
    for oneItem in rawText:
        if str(oneItem).startswith('{'):
            #print("Json part {}-{}".format(i, oneItem))
            break        
        i+=1
    print("Json part of eark validator results is {}, collecting..".format(i))
    
    try:
        earkjsonText = rawText[i] #The above find the correct part to gather
    except Exception as e:                    
        print("ERROR in getting json data from eark validator: {}".format(e))
    
    #print("Seeking {}".format(testcase_id))
    earkdata = json.loads(earkjsonText)                
    earkschematron_results = earkdata['metadata']['schematron_results']
    ruleItems = []
    for oneitem in earkschematron_results: #Only within results if failed       
       if oneitem['rule_id'] not in ruleItems:
           ruleItems.append(oneitem['rule_id'])
    #print("All eark validator identifed rules = {}".format(ruleItems))
    if isValid=="FALSE":
        assert testcase_id in ruleItems #IIf return True 0, all good, 
    else:
        assert testcase_id not in ruleItems #if return True 0, all good
    