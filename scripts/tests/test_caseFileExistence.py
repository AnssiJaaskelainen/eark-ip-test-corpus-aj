import os
import pytest

# Define a function to check if a file exists
def file_exists(file_path):    
    
    return os.path.exists(file_path)

# Test cases
def test_file_exists(request):    
    test_case_path = request.config.getoption("--testCasePath")
    #print(os.getcwd())
    print("IN PYTEST  using {}".format(test_case_path))
    fullPath = os.path.join(os.getcwd(), test_case_path)
    print(fullPath)    
    # Test an existing file
    result = file_exists(fullPath)    
    assert result==True
    
    

