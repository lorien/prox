import os

__version__ = '0.0.16'

country_database_file = os.path.join(os.path.dirname(__file__),
                                     'database', 'GeoLite2-Country.mmdb')
