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
    corrupt_raw_r1_data = """r1
WS=   ,WD=   ,RH=   ,AT=   ,BP=   ,BV=   ,LC=   ,SV=   ,CC=   ,PW=   ,IW=   ,IW=   ,RS=   ,Co=
+000002.20,+0001zz.21,+000068.49,+000.014.30,+001004.02,+000012.55,+000041.88,+000008.23,+000000.00,+000003.00,+000002.00,+000045.32,+000012.20,+000001.00
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
    parsed_corrupt_r1_data = {'wind_speed': 2.2,
                              'barometric_pressure': 1004.02,
                              'battery_voltage': 12.55,
                              'charge_current': 0.0,
                              'communications': 1.0,
                              'load_current': 0.04188,
                              'relative_humidity': 68.49,
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
        self.assertDictEqual(self.driver.parse_r1_data(self.corrupt_raw_r1_data),
                             self.parsed_corrupt_r1_data)

        # test a None response
        self.assertIsNone(self.driver.parse_r1_data(None))

    def test_convert_data(self):
        """Test the conversion of parsed r1 data."""

        # test an expected r1 parsed data response
        self.assertDictEqual(self.driver.convert_data(self.parsed_r1_data),
                             self.converted_r1_data)

        # test a None response
        self.assertIsNone(self.driver.convert_data(None))

    def test_map_data(self):
        """Test the mapping of converted r1 data."""

        # test an expected r1 converted data response
        self.assertDictEqual(self.driver.map_data(self.converted_r1_data),
                             self.mapped_r1_data)

        # test a None response
        self.assertIsNone(self.driver.map_data(None))


    def test_get_r1_environdata_field(self):
        """Test getting an Environdata field name given an r1 field name."""

        for e_field, value in six.iteritems(self.driver.r1_map):
            r1_field = value.get('field')
            # test that we have a non-None r1 field
            self.assertIsNotNone(r1_field)
            # get an appropriate element parameter to pass to get_r1_e_field()
            if e_field == 'instantaneous_wind_speed':
                element = (r1_field, '123', 'km/h')
            elif e_field == 'instantaneous_wind_direction':
                element = (r1_field, '123', 'Degs')
            else:
                element = (r1_field, '123', 'units')
            # test get_r1_e_field()
            self.assertEqual(self.driver.get_r1_e_field(element), e_field)


class UtilityTestCase(unittest.TestCase):
    """Test the various driver unit conversion methods."""

    stn_dict = {'ip_address': '192.168.254.254',
                'port': 10001,
                'poll_interval': 20
                }

    class FakeOpts(object):
        """Fake Opts class for use where OptionParser opts are required."""

        def __init__(self):
            self.faker = None
            self.ip_address = None
            self.port = None

    def setUp(self):

        # get an Environdata driver object
        self.driver = user.environdata.EnvirondataDriver(**self.stn_dict)
        self.opts = UtilityTestCase.FakeOpts()

    def tearDown(self):

        pass

    def test_ip_from_config_opts(self):
        """Test obtaining an IP address from OptionsParser opts or Station dict."""

        # test obtaining IP address from opts
        self.opts.ip_address = '1.2.3.4'
        self.assertEqual(user.environdata.ip_from_config_opts(self.opts, self.stn_dict),
                         '1.2.3.4')
        # test obtaining IP address from stn_dict
        self.opts.ip_address = None
        self.assertEqual(user.environdata.ip_from_config_opts(self.opts, self.stn_dict),
                         '192.168.254.254')
        # test being unable to obtain IP address from opts or stn_dict
        self.assertIsNone(user.environdata.ip_from_config_opts(self.opts, {'a': 1}))

    def test_port_from_config_opts(self):
        """Test obtaining an IP address from OptionsParser opts or Station dict."""

        # test obtaining IP address from opts
        self.opts.port = 1234
        self.assertEqual(user.environdata.port_from_config_opts(self.opts, self.stn_dict),
                         1234)
        # test obtaining IP address from stn_dict
        self.opts.port = None
        self.assertEqual(user.environdata.port_from_config_opts(self.opts, self.stn_dict),
                         10001)
        # test being unable to obtain port from opts or stn_dict
        self.assertEqual(user.environdata.port_from_config_opts(self.opts, {'a': 1}),
                         user.environdata.DEFAULT_PORT)
        # test no port in opts and an invalid port in stn_dict
        stn_dict = dict(self.stn_dict)
        stn_dict['port'] = 'a'
        self.assertEqual(user.environdata.port_from_config_opts(self.opts, stn_dict),
                         user.environdata.DEFAULT_PORT)


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
    test_cases = (ParseTestCase, UtilityTestCase)

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
