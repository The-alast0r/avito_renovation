from list_parser import parse_renovation_addresses
from avito_parser import *

BEGIN_URL = 'https://www.avito.ru/moskva/kvartiry/prodam/vtorichka/pod-snos-ASgBAgICA0SSA8YQ5geMUvLCDujsmQI?context=&f=ASgBAgICBkSSA8YQ5geMUurBDf7OOfLCDujsmQKO3g4CkN4OAg&i=1&s=104'
# BEGIN_URL = 'https://www.avito.ru/moskva/kvartiry/prodam/vtorichka/pod-snos-ASgBAgICA0SSA8YQ5geMUvLCDujsmQI?context=&f=ASgBAgICBUSSA8YQ5geMUvLCDujsmQKO3g4CkN4OAg&s=104'

if __name__ == '__main__':

    parser = AvitoParser()
    parser.start_parsing(BEGIN_URL)