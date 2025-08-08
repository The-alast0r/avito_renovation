class AddressPrettifier:
    """Класс преобразования адресов в требуемый вид."""

    def __init__(self, mode):
        self.mode           = mode
        self.origin_address = ''
        self.pretty_address = ''

    def make_address_pretty(self, address):
        self.origin_address = address

        if (self.mode == 'avito'):
            
            # Замены для адресов с авито
            if ('\n' in address):
                address = address.split('\n')[0]
            if ('ул.' in address):
                address = address.replace('ул.', 'улица')
            if ('пр.' in address):
                address = address.replace('пр.', 'проезд')
                address = address.replace('пp.', 'проезд') # Какой-то умник в базе реновации поставил английскую p
            if ('пр-т' in address):
                address = address.replace('пр-т', 'проспект')
            if ('наб.' in address):
                address = address.replace('наб.', 'набережная')
            if ('ш.,' in address):
                address = address.replace('ш.', 'шоссе')
            if ('б-р' in address):
                address = address.replace('б-р', 'бульвар')

        elif (self.mode == 'mos.ru'):

            # Замены для адресов с mos.ru
            parts = [part.strip() for part in address.split(',')]
            prefix_parts = []
            house_info = []
            
            for part in parts:
                if part.startswith('дом '):
                    value = part[4:].strip()
                    house_info.append(value)
                elif part.startswith('корпус '):
                    value = part[7:].strip()
                    house_info.append('к' + value)
                elif part.startswith('строение '):
                    value = part[9:].strip()
                    house_info.append('с' + value)
                else:
                    prefix_parts.append(part)
            
            address = ", ".join(prefix_parts)
            if house_info:
                house_str = ''.join(house_info)
                if address:
                    address += ", " + house_str
                else:
                    address = house_str

        self.pretty_address = address