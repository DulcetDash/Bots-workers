__ROOT_DIR__='/Users/Dominique/Documents-dev/Playground/Alexander/ChromeDriverInit/'

def getProxyList():
    try:
        proxy = False
        with open(str(__ROOT_DIR__)+ 'proxies.txt', 'r') as file:
            proxy = [ line.rstrip() for line in file.readlines()]
        return proxy
    except FileNotFoundError:
        raise Exception('proxies.txt not found.')