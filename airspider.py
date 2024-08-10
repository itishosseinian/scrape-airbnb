import scrapy
import json
import re

class AirspiderSpider(scrapy.Spider):
    name = "airspider"

    location = 'Calgary'
    location = location.replace(' ','--')
    num_adult = 2
    num_child = 1
    num_pet = 1
    checkin = '2024-08-08'
    checkout = '2024-08-14'
    

    base_url = f'https://www.airbnb.co.uk/s/{location}/homes?checkin={checkin}&checkout={checkout}&adults={num_adult}&children={num_child}&pets={num_pet}'

    def start_requests(self):


        yield scrapy.Request(url= self.base_url,callback= self.parse)

    def parse(self, response):


        data = response.xpath("//script[@id='data-deferred-state-0']/text()").get()
        jsdata = json.loads(data)

        target_result = jsdata['niobeMinimalClientData'][0][1]['data']['presentation']['staysSearch']['results']['searchResults']

        for result in target_result:
            yield{
                'full_url': f'https://www.airbnb.co.uk/rooms/{result['listing']['id']}?adults={self.num_adult}&children={self.num_child}&pets={self.num_pet}&search_mode=regular_search&check_in={self.checkin}&check_out={self.checkout}',
                'avg rating': result['listing']['avgRatingA11yLabel'],
                'images': [res['picture'] for res in result['listing']['contextualPictures']],
                'options': re.findall(r'"messages":\s*\[(.*?)\]',json.dumps(result['listing']['contextualPictures'])),
                'room id ': result['listing']['id'],
                'title': result['listing']['name'] + ' ' + result['listing']['title'],
                'price per night': result['pricingQuote']['structuredStayDisplayPrice']['primaryLine']['accessibilityLabel'],
                'total price': result['pricingQuote']['structuredStayDisplayPrice']['secondaryLine']['accessibilityLabel'],
                'coordinates': f"latitude: { result['listing']['coordinate']['latitude']} longitude: {result['listing']['coordinate']['longitude']}",
                 
            }
    

        next_page = jsdata['niobeMinimalClientData'][0][1]['data']['presentation']['staysSearch']['results']['paginationInfo']['nextPageCursor']
        print(next_page)
        
        if next_page:
            next_url = self.base_url + f'&pagination_search=true&cursor={next_page}'
            yield scrapy.Request(url= next_url, callback= self.parse)
