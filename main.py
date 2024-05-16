import platform, aiohttp, asyncio, json
from datetime import datetime, timedelta
from abc import abstractmethod, ABC

URL_TO_NBP_API = 'https://api.nbp.pl/api/exchangerates/tables/a/'
FORMAT_API = '?format=json'
THE_OLDEST_RATE = 10
CURRENCIES = ['USD', 'EUR']


class Parser(ABC):
    @abstractmethod
    def value(self):
        pass

class ParseURL(Parser):
    def __init__(self, url, format_api, date_of_rate):
        self.url = url
        self.format_api = format_api
        self.date_of_rate = date_of_rate

    def value(self):
        url_date_rate = f'{self.url}{self.date_of_rate}{self.format_api}'
        return url_date_rate

class ParseDate(Parser):
    def __init__(self, days_to_current_date:str):
        self.days_to_current_date = days_to_current_date

    def value(self):
        days_to_current_date = int(self.days_to_current_date)
        date_of_rate = datetime.today() - timedelta(days=days_to_current_date)
        date_of_rate = date_of_rate.strftime('%Y-%m-%d')
        return date_of_rate
    
class InputDate(Parser):
    def value(self):
        msg = f'Podaj, sprzed ilu dni chcesz uzyskać wartość kursu waluty (kurs nie starszy niż sprzed 10 dni): '
        date = input(msg)
        if  not date.isdigit():
            msg = f'podano błędną wartość'
            print_msg(msg)
        elif int(date) > 10:
            msg = f'Kurs waluty nie może być starszy niż sprzed 10 dni'
            print_msg(msg)
        else:
            return date
        
class ParseJsonData(Parser):
    def __init__(self, json_data:dict, currencies:list):
        self.json_data = json_data
        self.currencies = currencies

    def value(self):
        searched_currencies = []
        try:
            list_of_all_currencies = self.json_data[0]['rates']
            for currency in list_of_all_currencies:
                if currency['code'] in self.currencies:
                    searched_currencies.append(currency)
            return searched_currencies
        except:
            msg = f'Błędny format danych'
            print_msg(msg)
        
        
def print_msg(msg):
    print(msg)

async def import_data_json(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    msg = f'Status: {response.status}\n'
                    print_msg(msg)
                    result = await response.json()
                    return result
                else:
                    msg = f'Error status: {response.status} for {url}'
                    print_msg(msg)
        except aiohttp.ClientConnectorError as err:
                msg = f'Connection error: {url}, {str(err)}'
                print_msg(msg)


def main():
    date = InputDate().value()
    date = ParseDate(date).value()
    url = ParseURL(URL_TO_NBP_API, FORMAT_API, date).value()

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    nbp_data = asyncio.run(import_data_json(url))
    rates = ParseJsonData(nbp_data, CURRENCIES).value()
    print_msg(rates)


if __name__ == "__main__":
    main()
