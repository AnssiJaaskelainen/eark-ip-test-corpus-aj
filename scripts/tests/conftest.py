'''
Created on Jun 14, 2024

@author: memorylab-aj
'''
import pytest

def pytest_addoption(parser):
    parser.addoption("--testCasePath", action="store", default="")    
    parser.addoption("--testcase_id", action="store", default="")    
    parser.addoption("--SIPPath", action="store", default="") 
    parser.addoption("--isValid", action="store", default="")