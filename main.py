from list_parser import parse_renovation_addresses
from avito_parser import *

BEGIN_URL = 'https://www.avito.ru/moskva_i_mo/kvartiry/prodam?context=&s=104'

if __name__ == '__main__':

    parser = AvitoParser()
    parser.parse_avito(BEGIN_URL)
    