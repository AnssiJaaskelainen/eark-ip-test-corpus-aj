import json
import os
import subprocess

#from swagger_server.models import ValidationReport

MAIN_OPTS = [
    'java',
    '-jar',
    '/home/memorylab-aj/eclipse-workspace/EARKCSP/commonsIP/commons-ip2-cli-2.6.2.jar',
    'validate',
    '-v',
    '-i'    
]
REP_OPTS = [
    '-r',
    'commons-ip'
]

def validate_ip(info_pack):
    #print("1. InfoPack =  {}".format(info_pack))
    """Returns a tuple comprising the process exit code, the validation report
    and the captured stderr."""
    ret_code, file_name, stderr = java_runner(info_pack)
    validation_report = None
    if ret_code == 0:
        with open(file_name, 'r', encoding='utf-8') as _f:
            #print("4. Opening {}".format(file_name))
            contents = _f.read()
            #print("5. Content read succesfully")
        os.remove(file_name)
        validationContent = json.loads(contents)
        #validation_report = ValidationReport.from_dict(json.loads(contents))
        #print("Report: {}".format(validationContent))
    return ret_code, validationContent, stderr

def java_runner(ip_root):
    #print("1.5 {}".format(ip_root)) #Still ok    
    command=[]
    command+=MAIN_OPTS
    command.append(ip_root)
    command+=REP_OPTS
    #print("2. {}".format(command))    
    proc_results = subprocess.run(command, capture_output=True, text=True)
    #print (proc_results)
    command.clear()
   
    return proc_results.returncode, proc_results.stdout.split("'")[1], proc_results.stderr

