"""
Test suite for the Environdata Weather Mate 3000 driver.

Copyright (C) 2021 Gary Roderick                    gjroderick<at>gmail.com

A python unittest based test suite for aspects of the Environdata Weather Mate
3000 driver. The test suite tests correct operation of:

-

Version: 0.1.0a1                                    Date: ? November 2021

Revision History
    ? November 2021     v0.1.0
        -   initial release

To run the test suite:

-   copy this file to the target machine, nominally to the $BIN/user/tests
    directory

-   run the test suite using:

    $ PYTHONPATH=$BIN python3 -m user.tests.test_environdata [-v]
"""
# python imports
import struct
import time
import unittest

# Python 2/3 compatibility shims
import six

# WeeWX imports
import weewx
import user.environdata

TEST_SUITE_NAME = "Environdata driver"
TEST_SUITE_VERSION = "0.1.0a1"


class ParseTestCase(unittest.TestCase):
    """Test the various driver parser methods."""

    stn_dict = {'ip_address': '192.168.254.254',
                'port': 10001,
                'poll_interval': 20
                }

    raw_r1_data = """r1
WS=   ,WD=   ,RH=   ,AT=   ,BP=   ,BV=   ,LC=   ,SV=   ,CC=   ,PW=   ,IW=   ,IW=   ,RS=   ,Co=
+000002.20,+000111.21,+000068.49,+000014.30,+001004.02,+000012.55,+000041.88,+000008.23,+000000.00,+000003.00,+000002.00,+000045.32,+000012.20,+000001.00
km/h  ,Degs  ,%     ,DegC  ,hPa   ,V     ,mA    ,V     ,mA    ,km/h  ,km/h  ,Degs  ,mm    ,Mins
>"""
    parsed_r1_data = {'wind_direction': 111.21,
                      'wind_speed': 2.2,
                      'barometric_pressure': 1004.02,
                      'battery_voltage': 12.55,
                      'charge_current': 0.0,
                      'communications': 1.0,
                      'load_current': 0.04188,
                      'relative_humidity': 68.49,
                      'air_temperature': 14.3,
                      'rain_since_9am': 12.2,
                      'solar_voltage': 8.23,
                      'peak_wind_gust': 3.0,
                      'instantaneous_wind_speed': 2.0,
                      'instantaneous_wind_direction': 45.32
                      }
    converted_r1_data = {'wind_direction': 111.21,
                         'wind_speed': 2.2,
                         'barometric_pressure': 1004.02,
                         'battery_voltage': 12.55,
                         'charge_current': 0.0,
                         'communications': 60.0,
                         'load_current': 0.04188,
                         'relative_humidity': 68.49,
                         'air_temperature': 14.3,
                         'rain_since_9am': 1.22,
                         'solar_voltage': 8.23,
                         'peak_wind_gust': 3.0,
                         'instantaneous_wind_speed': 2.0,
                         'instantaneous_wind_direction': 45.32
                         }
    mapped_r1_data = {'avg_wind_direction': 111.21,
                      'avg_wind_speed': 2.2,
                      'barometer': 1004.02,
                      'batteryStatus1': 12.55,
                      'charge_current': 0.0,
                      'communications': 60.0,
                      'load_current': 0.04188,
                      'outHumidity': 68.49,
                      'outTemp': 14.3,
                      'rain_9am': 1.22,
                      'solar_voltage': 8.23,
                      'windGust': 3.0,
                      'windSpeed': 2.0,
                      'windDir': 45.32
                      }

    def setUp(self):

        # get an Environdata driver object
        self.driver = user.environdata.EnvirondataDriver(**self.stn_dict)

    def tearDown(self):

        pass

    def test_parse_r1_data(self):
        """Test the parsing of r1 data."""

        # test an expected r1 raw data response
        self.assertDictEqual(self.driver.parse_r1_data(self.raw_r1_data),
                             self.parsed_r1_data)

        # test a corrupted response
        pass

        # test a None response
        self.assertEqual(self.driver.parse_r1_data(None), None)

    def test_convert_data(self):
        """Test the conversion of parsed r1 data."""

        # test an expected r1 parsed data response
        self.assertDictEqual(self.driver.convert_data(self.parsed_r1_data),
                             self.converted_r1_data)

        # test a corrupted response
        pass

        # test a None response
        self.assertEqual(self.driver.convert_data(None), None)

    def test_map_data(self):
        """Test the mapping of converted r1 data."""

        # test an expected r1 converted data response
        self.assertDictEqual(self.driver.map_data(self.converted_r1_data),
                             self.mapped_r1_data)

        # test a corrupted response
        pass

        # test a None response
        self.assertEqual(self.driver.map_data(None), None)


#    def test_get_weewx_field(self):
#        """Test getting the WeeWX field name given the Environdata field name."""
#
#        # test
#        self.assertEqual(self.driver.get_w_field(['AT', '+000014.30', 'DegC']),
#                         'outTemp')


class ConversionTestCase(unittest.TestCase):
    """Test the various driver unit conversion methods."""

    stn_dict = {'ip_address': '192.168.254.254',
                'port': 10001,
                'poll_interval': 20
                }

    def setUp(self):

        # get an Environdata driver object
        self.driver = user.environdata.EnvirondataDriver(**self.stn_dict)

    def tearDown(self):

        pass

    def test_conversion_methods(self):
        """Test unit conversion methods."""

        pass


def suite(test_cases):
    """Create a TestSuite object containing the tests we are to perform."""

    # get a test loader
    loader = unittest.TestLoader()
    # create an empty test suite
    suite = unittest.TestSuite()
    # iterate over the test cases we are to add
    for test_class in test_cases:
        # get the tests from the test case
        tests = loader.loadTestsFromTestCase(test_class)
        # add the tests to the test suite
        suite.addTests(tests)
    # finally return the populated test suite
    return suite


def main():
    import argparse

    # test cases that are production ready
    test_cases = (ParseTestCase, ConversionTestCase)

    usage = """python -m user.tests.test_environdata --help
           python -m user.tests.test_environdata --version
           python -m user.tests.test_environdata [-v|--verbose=VERBOSITY] [--ip-address=IP_ADDRESS] [--port=PORT]

        Arguments:

           VERBOSITY: Path and file name of the WeeWX configuration file to be used.
                        Default is weewx.conf.
           IP_ADDRESS: IP address to use to contact the Environdata Weather Mate 3000.
           PORT: Port to use to contact the Environdata Weather Mate 3000."""
    description = 'Test the the Environdata Weather Mate 3000 driver code.'
    epilog = """You must ensure the WeeWX modules are in your PYTHONPATH. For example:

    PYTHONPATH=/home/weewx/bin python -m user.tests.test_environdata --help
    """

    parser = argparse.ArgumentParser(usage=usage,
                                     description=description,
                                     epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--version', dest='version', action='store_true',
                        help='display Environdata Weather Mate 3000 driver test suite version number')
    parser.add_argument('--verbose', dest='verbosity', type=int, metavar="VERBOSITY",
                        default=2,
                        help='How much status to display, 0-2')
    parser.add_argument('--ip-address', dest='ip_address', metavar="IP_ADDRESS",
                        help='Environdata Weather Mate 3000 IP address to use')
    parser.add_argument('--port', dest='port', type=int, metavar="PORT",
                        help='Environdata Weather Mate 3000 port to use')
    # parse the arguments
    args = parser.parse_args()

    # display version number
    if args.version:
        print("%s test suite version: %s" % (TEST_SUITE_NAME, TEST_SUITE_VERSION))
        print("args=%s" % (args,))
        exit(0)
    # run the tests
    # get a test runner with appropriate verbosity
    runner = unittest.TextTestRunner(verbosity=args.verbosity)
    # create a test suite and run the included tests
    runner.run(suite(test_cases))


if __name__ == '__main__':
    main()
