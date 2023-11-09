# from google_images_search import GoogleImagesSearch

# # you can provide API key and CX using arguments,
# # or you can set environment variables: GCS_DEVELOPER_KEY, GCS_CX
# gis = GoogleImagesSearch('AIzaSyD9ysI5aF8R58Ar6_NtXVdvz6yqAR0anrA', 'dulcetdash')

# # define search params
# # option for commonly used search param are shown below for easy reference.
# # For param marked with '##':
# #   - Multiselect is currently not feasible. Choose ONE option only
# #   - This param can also be omitted from _search_params if you do not wish to define any value
# _search_params = {
#     'q': 'Sensai Ultimate Concentrate',
#     # 'num': 10,
#     # 'fileType': 'jpg|gif|png',
#     # 'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived',
#     # 'safe': 'active|high|medium|off|safeUndefined', ##
#     # 'imgType': 'clipart|face|lineart|stock|photo|animated|imgTypeUndefined', ##
#     # 'imgSize': 'huge|icon|large|medium|small|xlarge|xxlarge|imgSizeUndefined', ##
#     # 'imgDominantColor': 'black|blue|brown|gray|green|orange|pink|purple|red|teal|white|yellow|imgDominantColorUndefined', ##
#     # 'imgColorType': 'color|gray|mono|trans|imgColorTypeUndefined' ##
# }

# # this will only search for images:
# # gis.search(search_params=_search_params)

# # this will search and download:
# gis.search(search_params=_search_params, path_to_dir='./')

# # this will search, download and resize:
# # gis.search(search_params=_search_params, path_to_dir='/path/', width=500, height=500)

# # search first, then download and resize afterwards:
# # gis.search(search_params=_search_params)
# # for image in gis.results():
# #     image.url  # image direct url
# #     image.referrer_url  # image referrer url (source) 
    
# #     image.download('/path/')  # download image
# #     image.resize(500, 500)  # resize downloaded image

# #     image.path  # downloaded local file path

import requests

def google_image_search(search_term, api_key, cse_id, num=1):
    """
    Search for images using Google Custom Search JSON API.

    :param search_term: The search term to search for.
    :param api_key: Your Google API key.
    :param cse_id: The custom search engine ID to scope this search.
    :param num: Number of search results to return (1-10).
    :return: List of image URLs.
    """
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": search_term,  # search term
        "cx": cse_id,  # custom search engine ID
        "key": api_key,  # API key
        "searchType": "image",  # search for images
        "num": num,  # number of results
        "imgSize": "large",  # request large images
        "fileType": "jpg",  # search for jpg images
    }
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    search_results = response.json()
    
    # Extract the URLs of images
    image_urls = [item["link"] for item in search_results.get("items", [])]
    return image_urls

# Use the function
api_key = 'YOUR_API_KEY'
cse_id = 'YOUR_CSE_ID'
search_term = 'example search'

image_urls = google_image_search(search_term, api_key, cse_id)
for url in image_urls:
    print(url)
