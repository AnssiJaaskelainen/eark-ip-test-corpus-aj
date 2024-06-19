import xml.etree.ElementTree as ET 
import subprocess
import os 
import json
import sys
import CommonsipValidator as comval
from importlib.metadata import PackagePath

import pytest
#from bokeh.util.sampledata import package_path


def useCommonsIP(testPath):
    ret_code, validation_report, stderr = comval.validate_ip(testPath)
    #print("6")
    #print ("Path: {} \n Report: {}\n error: {}\n return code: {}\n".format(testPath, validation_report, stderr, ret_code))
    return validation_report


if len(sys.argv) == 1:
    print("Path(s) to testCase.xml file(s) must be specified!")
    exit(1)

total_test_cases = 0
total_rules = 0
total_validations = 0
failed_validations = 0
failed_parsings = 0
missing_packages = 0
skipped_validations = 0

#[Collection lists]
missing_packages_list = []
incorrectPaths = []


eark_inconsistent_outputs = 0
eark_correct_valid_validatons = 0
eark_correct_invalid_validatons = 0

cs_inconsistent_outputs = 0
cs_correct_valid_validatons = 0
cs_correct_invalid_validatons = 0
cscsiperrors = [] 

pytest_testCaseExists = 0
pytest_testCaseNotExists = 0

pytest_correctTrue = 0
pytest_wrongTrue = 0
pytest_correctFalse = 0
pytest_wrongFalse = 0

notImplemented = 0
                
for test_case_path in sys.argv[1:]:
    total_test_cases += 1
    
    #This part handles the pytest of each file
    ipPart = os.path.basename(os.path.dirname(os.path.normpath(test_case_path)))   
    testScriptPath = "scripts/tests/test_caseFileExistence.py"
    print("pytest for {} in {}".format(ipPart, testScriptPath))
    testPath = os.path.join(os.getcwd(), testScriptPath)
    #runs a pytest to check if the path exists
    #pytest.main([test_case_path])
    pyTestFileExistsResult = pytest.main(["--testCasePath",os.path.normpath(test_case_path), testPath])
    
    if (pyTestFileExistsResult==0): #Means file is found
        pytest_testCaseExists+=1
        #Continue to deepter tests
    else:
        pytest_testCaseNotExists+=1
        
        
    
    dir_path = os.path.dirname(test_case_path)

    try:
        tree = ET.parse(test_case_path)
    except Exception as e:
        failed_parsings += 1
        print("PARSING FAILED: {}".format(test_case_path))
        print(e)
        continue
    #break

    root = tree.getroot()    
    
    """ <id specification="E-ARK CSIP" version="2.1.0" requirementId="CSIP60"/>"""
    testcase_id = root.find('id').get('requirementId')

    """<testCase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="testCase.xsd"  testable="TRUE">"""
    if root.get('testable') != 'TRUE':        
        skipped_validations += 1
        continue

    for rule in root.iter('rule'):
        total_rules += 1
        rule_id = rule.get('id')
        errorLevel = rule.find('error').get('level')
      
        for package in rule.find('corpusPackages'):            
            total_validations += 1

            relative_path = package.find('path').text            
            if relative_path == '' or relative_path is None:
                #print(f'Path in {test_case_path}, rule id: {rule_id} is misssing.')
                missing_packages += 1                
                tempList=[test_case_path, "rule {}".format(rule_id)]
                missing_packages_list.append(tempList)
                
                continue

            package_path = os.path.join(dir_path, relative_path)
            #print("Start: {}".format(package_path))
            earkerrorids = []        
            earkwarningids = [] 
            earkinfoids = []
            allEarkIDs = []   
            
            cserrorids = []                   
            cswarningids = [] 
            csinfoids = []
            allCsIDs = []   
            
            isValid = package.get('isValid')            
            try:
                isImplemented = package.get('isImplemented')
                #print("Is implemented = {}".format(isImplemented))
            except Exception as e:                
                continue          
            
            #print("\nTESTING: {} rule {}-{}, valid = {}, error level = {}".format(testcase_id, rule_id, package_path, isValid, errorLevel ))               
            #TESTING: CSIP14 rule 1-./corpus/CSIP/CSIP14/invalid/mets-xml_metsHdr_agent_name_empty, valid = FALSE, error level = ERROR

            #Required for next pytest
            """testcase_id,
            package_path, 
            isValid"""
            testScriptPath = "scripts/tests/test_isValidFalse.py"
            print("pytest for {} in {}".format(ipPart, testScriptPath))
            testPath = os.path.join(os.getcwd(), testScriptPath)
            
            Sip_path = os.path.join(os.getcwd(), os.path.normpath(package_path))

            print("{} SIP path to test:  {}".format(testcase_id, Sip_path))
            if isImplemented=="TRUE":
                pySIPResult = pytest.main([
                    "-s",
                    "--testCasePath", testScriptPath,
                    "--testcase_id" , testcase_id,
                    "--SIPPath", Sip_path,  
                    "--isValid", isValid,
                     testPath])
                # 0 = True --> testcase_id found in test results
                # 1 = False --> testcase_id NOT found in test results as it should have
                print("Assert result {} -- {} is Valid".format(pySIPResult, isValid))
                if pySIPResult==0:
                    if isValid=="TRUE":
                        pytest_correctTrue+=1
                    else:
                        pytest_wrongTrue+=1
                else:
                    if isValid=="FALSE":
                        pytest_correctFalse+=1
                    else:
                        pytest_wrongFalse+=1
            else:
                notImplemented+=1
                
                                   
                

           
               
                     
                
            """CSIP handling section"""
            """"
            try:
                csdata = useCommonsIP(package_path)
                csschema_results = csdata['validation']
                #print("CSIP validator contains {} items".format(len(csschema_results)))
                #print(csdata)                    
                for oneitem in csschema_results:                    
                    outcome = oneitem['testing']['outcome']
                    
                    if outcome =="FAILED":
                        allCsIDs.append(oneitem['id'])                            
                        if oneitem['level']=="MUST":
                            cserrorids.append(oneitem['id'])
                            if oneitem['id'] == 'CSIP0':
                                if package_path not in cscsiperrors:                                    
                                    cscsiperrors.append(package_path)
                                
                        if oneitem['level']=="SHOULD":
                            cswarningids.append(oneitem['id'])
                        if oneitem['level']=="MAY":
                            csinfoids.append(oneitem['id'])
                
                print("CS validator")                
                print("Error IDs{}".format(cserrorids))
                print("Warning IDs{}".format(cswarningids))
                print("Info IDs{}".format(csinfoids))     
                print("All CS ID:s {}".format(allCsIDs))
                
                              
                   
                  
            except Exception as e:            
                continue
            #print("{} , rule {} - csip schema results = {}".format(testcase_id, rule_id, csschema_results))
            #Gets all rule_id:s from results into a list:
             
                

            except Exception as e: 
                failed_validations += 1
                print("{} - FAILED: {} -->{}".format(id, package_path, e))
                incorrectPaths.append(package_path)
            """   
   
    if total_test_cases>1:
       break

print("RESULTS")
"""
print("Paths defined in testCase.xml missing: {}\n".format(len(incorrectPaths)))
i=1
for oneitem in incorrectPaths:
    print("{}-{}".format(i, oneitem))
    i+=1
print("Missing test packages: {} {}".format(len(missing_packages_list), missing_packages_list))
"""
print("PYTEST")
print("Found {} testCase.xml files, missing {}".format(pytest_testCaseExists, pytest_testCaseNotExists))
print("Tested {} cases and {} validation rules".format(total_test_cases, total_validations))
print("Correct Valid {}".format(pytest_correctTrue))
print("--Wrong Valid {}".format(pytest_wrongTrue))
print("Correct InValid {}".format(pytest_correctFalse))
print("--Wrong InValid {}".format(pytest_wrongFalse))
print("NOT implemented tests {}".format(notImplemented))
       

    