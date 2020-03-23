#################################
##### Name: BENJAMIN ROTH
##### Uniqname: ROTHBEN
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

base_url = 'https://www.nps.gov'
state_dict = {}
i=0


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, name="None", category="None", address="None", zip="None", number="None"):
        self.name=name
        self.category=category
        self.address=address
        self.zip=zip
        self.number=number


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    state_page_url = base_url
    response = requests.get(state_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    state_listing_parent = soup.find(role="menu")
    state_listings = state_listing_parent.find_all('li')

    for state in state_listings:
        state_link_tag = state.find('a')
        state_details_path = state_link_tag['href']
        state_details_url = base_url + state_details_path
        state_dict[state.text.strip().lower()] = state_details_url

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    if site_url not in site_instance_dict:
        print('Fetching from NPS site')
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        site_title_parent = soup.find(class_="Hero-titleContainer clearfix")
        site_title = site_title_parent.find('a')
        name = site_title.text.strip()
        NationalSite.name=name

        category_parent = soup.find(class_="Hero-designationContainer")
        category_html = category_parent.find(class_="Hero-designation")
        category = category_html.text.strip()
        NationalSite.category=category

        address_parent = soup.find(class_="adr")
        address_locality_html = address_parent.find(itemprop="addressLocality")
        address_locality = address_locality_html.text.strip()

        address_region_html = address_parent.find(itemprop='addressRegion')
        address_region = address_region_html.text.strip()

        address = f"{address_locality}, {address_region}"
        NationalSite.address=address

        zip_html = address_parent.find(itemprop="postalCode")
        zip = zip_html.text.strip()
        NationalSite.zip=zip

        number_parent = soup.find(class_="vcard")
        number_html = number_parent.find(itemprop="telephone")
        number = number_html.text.strip()
        NationalSite.number=number
        site_instance_dict.setdefault(site_url, [])
        site_instance_dict[site_url].append(f"{name} ({category}): {address} {zip}")
        return f"{name} ({category}): {address} {zip}"
    else:
        print('Getting from cache')
        a = site_instance_dict.get(site_url, "")
        for b in a:
            print(b)

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    if state_url not in sites_dict:
        based_url = 'https://www.nps.gov'
        url_end = 'index.htm'
        i=0
        response = requests.get(state_url)
        soup = BeautifulSoup(response.text, 'html.parser')


        sites_parent = soup.find(id="parkListResults")
        state_listings = sites_parent.find_all('h3')

        for site in state_listings:
            state_link_tag = site.find('a')
            state_details_path = state_link_tag['href']
            site_details_url = based_url + state_details_path + url_end
            
            full_return = get_site_instance(site_details_url)
            i += 1
            park_results_list.append(full_return)
            sites_dict.setdefault(state_url, [])
            sites_dict[state_url].append(f"[{i}] {full_return}")
            print(f"[{i}] {full_return}")
    else:
        print('Getting from cache')
        a = sites_dict.get(state_url, "")
        for b in a:
            print(b)



def get_nearby_places(site_object):
    api_key = secrets.API_KEY
    base_url = 'http://www.mapquestapi.com/search/v2/radius'
    params = {"key": api_key, "origin": site_object, "radius": 10, "maxMatches": 10, "ambiguities": "ignore", "outFormat": "json"}
    if site_object not in site_object_dict:
        print("Fetching from MapQuest")
        response = requests.get(base_url, params)
        result = response.json()
        o = result.get('searchResults', "")
        for a in o:
            b = a.get("fields", "")
            name = b['name']
            if b['group_sic_code_name_ext'] == "":
                category = "Category Unavailable"
            else:
                category = b['group_sic_code_name_ext']
            if b['address'] == "":
                address = "No Address"
            else: 
                address = b['address']
            if b['city'] == "":
                city = "No City"
            else:
                city = b['city']
            site_object_dict.setdefault(site_object, [])
            site_object_dict[site_object].append(f"- {name} ({category}): {address}, {city}")
            print(f"- {name} ({category}): {address}, {city}")
    else:
        print('Getting from cache')
        a = site_object_dict.get(site_object, "")
        for b in a:
            print(b)

def run_proj2(exit_words):
    x = input("Please enter a State or U.S. Territory: ")
    z = x.strip().lower()
    if z not in exit_words:
        if z in state_dict.keys():
            o = state_dict.get(z, "")
            get_sites_for_state(o)
        else: 
            print("That wasn't a valid state or territory. Please try again.")
            run_proj2(exit_words)
        a = input("Please choose a park for more details, or type 'back' to go back: ")
        if a in back_words:
            run_proj2(exit_words)
        elif a in exit_words:
            print("Goodbye")
            quit()
        else:
            pass
        if a.isnumeric() is True:
            b = int(a) - 1
            park_data_long = park_results_list[b]
            zipcode = park_data_long[-5:]
            print(f"---Getting places near {park_results_list[b]}---")
            get_nearby_places(zipcode)
        else:
            print("You did not enter a valid selection. Please try again.")
            run_proj2(exit_words)
        run_proj2(exit_words)
    else:
        print("Goodbye")
        quit()

if __name__ == "__main__":
    exit_words = ('quit', 'close', 'end', 'exit')
    back_words = ('back', 'return')
    site_object_dict = {}
    site_instance_dict = {}
    sites_dict = {}
    build_state_url_dict()
    park_results_list = []
    run_proj2(exit_words)