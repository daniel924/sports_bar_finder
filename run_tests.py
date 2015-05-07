#!/usr/bin/python
import optparse
import sys
import unittest
import os

USAGE = """%prog SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to Google Cloud or Google App Engine SDK installation, usually ~/google_cloud_sdk
TEST_PATH   Path to package containing test modules"""


def main(sdk_path, test_path):
    # If the sdk path points to a google cloud sdk installation
    # then we should alter it to point to the GAE platform location.
    if os.path.exists(os.path.join(sdk_path, 'platform/google_appengine')):
      sys.path.insert(0, os.path.join(sdk_path, 'platform/google_appengine'))
    else:
      sys.path.insert(0, sdk_path)

    sys.path.insert(0, 'test')
    sys.path.insert(0, 'model')

    # Ensure that the google.appengine.* packages are available
    # in tests as well as all bundled third-party packages.
    import dev_appserver
    dev_appserver.fix_sys_path()

    # Loading appengine_config from the current project ensures that any
    # changes to configuration there are available to all tests (e.g.
    # sys.path modifications, namespaces, etc.)
    try:
      import appengine_config
    except ImportError:
      print "Note: unable to import appengine_config."

    # Discover and run tests.
    suite = unittest.loader.TestLoader().discover(test_path, pattern = "*_test.py")
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    SDK_PATH = '/usr/local/google_appengine'
    TEST_PATH = '.'
    main(SDK_PATH, TEST_PATH)
