import math

# PnP discovery
# defaultString = 'https://www.pnp.co.za/c/pnpbase'

# suffix = '?currentPage='
# numberOfPages = 139

# for page in range(0, numberOfPages):
#     appendString = '' if page == 0 else suffix + str(page)
#     print(defaultString + appendString)


# Checkers discovery
# defaultString = 'https://www.checkers.co.za/c-2256/All-Departments'

# numberOfItems = 22683
# numberOfPages = math.ceil(numberOfItems/20)

# for page in range(0, numberOfPages):
#     appendString = '?q=%3Arelevance%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={}'.format(
#                         page) if page > 0 else ''
#     print(defaultString + appendString)


# Shoprite discovery
# defaultString = 'https://www.shoprite.co.za/c-2256/All-Departments'

# numberOfItems = 11386
# numberOfPages = math.ceil(numberOfItems/20)

# for page in range(0, numberOfPages):
#     appendString = '?q=%3Arelevance%3AbrowseAllStoresFacetOff%3AbrowseAllStoresFacetOff&page={}'.format(
#                         page) if page > 0 else ''
#     print(defaultString + appendString)


# Crazy store discovery
defaultString = 'https://www.crazystore.co.za/products'

suffix = '?items_per_page=36&sort_bef_combine=changed_DESC&page='
numberOfPages = 112

for page in range(0, numberOfPages):
    appendString = '' if page == 0 else suffix + str(page)
    print(defaultString + appendString)


# Dis-chem store discovery
# defaultString = 'https://www.dischem.co.za/shop-by-department'

# suffix = '?p='
# numberOfPages = 116

# for page in range(0, numberOfPages):
#     appendString = '' if page == 0 else suffix + str(page)
#     print(defaultString + appendString)