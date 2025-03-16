import unittest
from unittesting import TestDB
from unittesting import TestGetUser
from unittesting import TestRegistration
from unittesting import TestLogin

from backendunittesting import TestNavigator

from similarItemTest import similarItemTest

# Create a test suite
def suite():
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(unittest.makeSuite(TestDB))
    test_suite.addTest(unittest.makeSuite(TestGetUser))
    test_suite.addTest(unittest.makeSuite(TestRegistration))
    test_suite.addTest(unittest.makeSuite(TestLogin))

    test_suite.addTest(unittest.makeSuite(TestNavigator))
    test_suite.addTest(unittest.makeSuite(similarItemTest))
    
    return test_suite

# Run the test suite
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())