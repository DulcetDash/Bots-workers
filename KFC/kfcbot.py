'''
1. Get all the catalogue from KFC
'''
# prettier-ignore
import sys
sys.path.append('../')
import Utility
import SaveOrUpdateItem
import ImageDownloader
import uuid
import seedImages
from boto3.dynamodb.conditions import Key, Attr
import GetUrlDocument
import boto3
import json
import http.client
import datetime
from colorama import Back, Fore, Style, init
import requests
from bs4 import BeautifulSoup
import re
import csv
from tqdm import tqdm
from ast import Try
from tkinter import E
from unicodedata import category
from numpy import disp
import time
from random import randint
import sys
import os
import traceback
init()

dynamodb = boto3.resource('dynamodb', aws_access_key_id='AKIAVN5TJ6VCUP6F6QJW',
                          aws_secret_access_key='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',
                          region_name='us-west-1')

conn = http.client.HTTPSConnection("api.scrapingant.com")


driver = False
wait = False

client = False
db = False
_SHOP_NAME_ = 'KFC'
_CATEGORY_GENERAL = 'FOOD'
shop_fp = 'kfc9537807322322'
root_url = "https://www.kfcnamibia.com/en/menu.html"


def display_log(fore=Fore.GREEN, text=''):
    print(fore + '{}'.format(text))
    print(Style.RESET_ALL)


display_log(Fore.GREEN, 'ROBOT NAME: KFC-BOT')
display_log(Fore.GREEN, _SHOP_NAME_)

_DEALS_UNAUTHORISED = [
    'DELIVERY EXCLUSIVES',
    'PROMOTIONS'
]

# Create a ScrapingAntClient instance
headers = {
    'x-api-key': "9d1df42476e649968ddb8d58a18cb5c6",
    'content-type': "application/json",
    'accept': "application/json"
}


def getHTMLDocument(url):
    response = requests.get(url)
    return response.text


def launchBot():
    try:
        staticImagesReference = '''
           <img src="https://cdn.tictuk.com/defaultThemes/brands/kfc/assets/images/pastOrdersEmpty.png"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/bed6702e-d4a6-8d0c-11a5-0f5ac99054d8.png?a=478ea4f8-426e-9d6f-0fe0-94282f60d0cd"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/311c4564-6d1b-57ab-7fd3-d55b1342a7fe.png?a=509ef318-1861-7b38-e107-fdebe47168bd"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/4f63fda1-5dc4-97e5-2b62-99606e3845d9.png?a=eb208ff6-6713-9ca7-7e3a-fe86de863e03"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/fef3ed1b-f687-e178-6dff-9107c1fa6666.png?a=54c2d4f1-e0aa-5536-e50c-f8af101ef68b"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/4baff724-cb02-32b1-10b4-321a03badf57.png?a=863bbedc-e4bf-f038-6d33-72be70dd1505"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/a4b20a64-6ef2-84d9-3043-b9bc07566ac3.png?a=1e77f6b0-97b7-0e68-04c6-91981689728f"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/132cbaa3-d51e-b822-d925-6f663f0ef87d.png?a=57137d20-7faa-7f75-4b53-c0a5742564ad"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/b2435ae5-ec52-34df-3b85-466505a6d955.png?a=45618046-ec53-0c70-5a85-a84635e5b4a4"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/b459e49f-1ef4-b224-6648-88f081adade8.png?a=697bda4d-9eb6-0225-91dc-2006b668fefd"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/9160f479-226f-800c-e8bb-1f20d9377e46.png?a=45ad515b-ef75-3bca-9310-c48220984d7e"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/6530109b-7d62-0e27-fcf4-ae87d256871c.jpeg?a=4c5bfea4-bc44-df1d-0d69-042f8fcdd688"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/f2a9101f-52bc-b48b-d263-e511d38d789a.jpeg?a=5b007854-42f0-bb1e-5326-5b34b9fad600"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/f1c6d14d-ad35-6039-b1fc-9efd391acce8.jpeg?a=30f092fa-28a1-7f0d-b1b9-8a192f7b7c56"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/8cf51aaa-b20f-eca0-7ec0-c1e5e050e839.jpeg?a=91d7d4ff-9f42-7570-3688-875bf8625762"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/bb0b14d5-e402-3a7b-59f0-57892f07bdb7.png?a=d31cfc87-47ae-98ad-f7d4-87b91293e219"/>
            <img src="https://www.kfcnamibia.com/assets/logoMobileHeader.svg"/>
            <img src="https://www.kfcnamibia.com/assets/logoDesktopHeader.svg"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/15ceb5fc-e48c-da7a-8505-c315acedfee8.png?a=1d1250d4-cb13-4705-6131-b8d1f400b209"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/429c65ed-728d-f489-3c5d-7a1ce99d9241.png?a=5f1fde79-3b7d-6b86-5111-db641a5a9822"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/52298c6d-2b79-84ff-531e-7abe18b4ad44.png?a=360bd1a7-2e06-27dd-5f87-90dcc0faeddd"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/1b6c497d-9e5e-2c15-3911-ebd5e3fc6df7.png?a=ea2ea952-bef9-1bc3-49a8-4044568c9470"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/230721c8-0dfe-1583-5b0e-2a4ee1f147bf.png?a=3fc4231b-36bd-1139-c1c0-070a19564573"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/96b9d30d-393a-cae5-5052-60a796833199.png?a=23056a2c-73e9-c9a6-3c05-5369ee9868c3"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/77589f8c-244c-35c1-0a0a-e65ff0f273c2.png?a=7b0cbbce-5327-7a07-2fb2-e76bf0bd9de6"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/061c41e1-caaf-e179-0d5f-27a356d7e80d.jpeg?a=42f8c1ef-6e71-a9e0-1e4a-0d8dbb6779a9"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/5b4fb261-b32d-903d-8470-8fca7226a3d9.jpeg?a=653a5930-c5c2-c8af-8be5-0554b8146dd7"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/a09f14e5-e9dd-3c8b-a01f-86866339926d.png?a=b0142f04-2771-ccb2-efcb-4a299757e325"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/43a41c42-75e6-2fdc-bf6f-7280ca48a7ce.png?a=120c02e2-c82d-af72-a834-78e9541374c8"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/262c59b2-b04f-0ede-044e-5d742b298ce9.png?a=4917fa21-73e0-e598-07ca-1cb26cfd3284"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/7965172e-9a4d-331a-2527-387c3a90aa44.png?a=6267c08b-6c27-8fbb-a482-b5267f32e1fb"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/9c970120-099e-8d3b-4353-e23072c22ca1.png?a=b8b16515-06d8-7c3c-db05-32a10ee7cedb"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/4b71a4e8-23b5-ed67-401c-e1a8a155f7fd.png?a=6115b079-2c57-4938-2cd0-06ff5c8098c6"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/2bb0d823-61a9-7121-e3dd-866860023acd.png?a=50d85666-f776-36af-5999-8d07bc7d8985"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/beba0b7c-f6bd-845f-edfc-160294b11ce3.jpeg?a=4b1e6fc4-4245-3a09-f451-426ba5a24795"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/84c6ac94-1d2b-c595-7515-d298dc4fef2a.jpeg?a=0cbc3bac-7e88-9840-a279-54224a0d80f0"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/59466fae-7a55-a745-bec2-6c72b3e1ff52.jpeg?a=c7af4873-51f2-9e86-e389-54501a06b7d2"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/b120dc5f-820d-54a9-c816-2a32024dfaaa.jpeg?a=b644ce2d-42b7-05c1-7db9-5afd57e7b978"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/9ab2011e-9e73-51c5-5338-2e8c9b760152.jpeg?a=7e3bafd0-c851-bce2-4f10-6829594b0f74"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/163d40d5-678b-7842-bb1f-d16f5c51c4c3.jpeg?a=26009d91-f3f0-56a4-c32a-5a2f889d0d7a"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/1d76f6fd-1a30-802f-7f54-0daa264395cb.png?a=7fe560b8-9c9f-cfac-d298-c9a5024d8a3a"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/eb26adae-afa5-835b-1518-70ab08bd52fb.jpeg?a=f376248a-6587-8706-32d7-a920eced0172"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/348c98e3-0269-f795-4342-df45659b98d8.jpeg?a=069de16e-f02e-1c77-a663-71283cde4dad"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/871fbd3a-cecd-383f-1afe-337480fa605b.png?a=85f12f07-b19a-030e-6186-49a39cf922eb"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/0192a13f-fdf9-ad01-f7b2-1b1c4111780b.jpeg?a=e6ff8a8e-24a8-edf4-e990-fe3fb6a1605c"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/7c3cf426-d41e-59ea-122a-3e4d410ff117.jpeg?a=9421f4f8-a762-ef29-e7b6-d8c4fec50e14"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/0644b965-9bf0-9ada-f08d-7cdf5356499a.jpeg?a=cbb149e7-13ab-d6e6-696f-02d5a69fc5fe"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/5d8c4017-b3f1-5c99-0e90-5e293e97d41b.jpeg?a=8ae31038-787c-b330-5d23-73c2b04ccb0f"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/56be308a-8586-6080-fab1-2e6d7af9ea84.jpeg?a=e1dc20c9-19e2-b704-a533-4c5bb1e816a6"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/8ae90d09-a36d-4e9a-c44e-52c71eb9ce18.jpeg?a=d14061b4-231c-a639-67c9-413b55d44dea"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/0db1ddf3-3794-d45d-58ab-45983d22880f.jpeg?a=640af98a-d427-ff8a-482d-645fed19c9a8"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/bbb58850-2495-2672-1704-e4139d25d3a6.jpeg?a=7204ccca-8d2c-cef6-6aff-759b4abc480d"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/39a05943-d683-5db2-67b1-3c347aa953ac.jpeg?a=98bf536c-ca33-65c4-93fc-12e19bbef38d"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/cef21613-5abe-4e54-e361-48e51fb146c8.jpeg?a=2346a0c5-d64e-53e3-64e3-cc73571c87fc"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/285be54b-0213-727a-2faa-276354f35608.jpeg?a=14fefa9d-21ae-ac7d-a767-439687cf737f"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/2e68dba3-1fd2-a7a6-01e7-d7057b572717.jpeg?a=143b81e7-7847-1eb6-8d82-b188de7fe8cc"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/061c41e1-caaf-e179-0d5f-27a356d7e80d.jpeg?a=b5055da6-b973-747e-b4bb-b563416f5806"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/60ed6c31-7942-cf91-8afd-4ec200c4d629.jpeg?a=96de0e7e-9321-5e45-4ddd-9a6cf94bfd93"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/e9e53b7c-89e6-ee33-c11b-da30e448be9b.jpeg?a=1bace5c5-55d1-ceb3-274e-596eccdb6080"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/d7f821da-1b36-eaa9-d1d5-41fe29fb98cb.jpeg?a=821dc391-1b98-1ebd-33ab-ebba31bf05eb"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/a74eac17-46d0-a07d-7c65-0c1c18bc216b.jpeg?a=52a7c106-5c45-fde6-7810-347c3c3c9e77"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/f82ba52a-b3a8-9b59-6c0c-1af710b9c7db.jpeg?a=81df7017-920e-cdc8-a7c1-90772c1145ea"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/e6c35c8c-d20c-57f3-6ab7-1d17719d7f88.png?a=4698d601-7f84-d0da-8d41-8c0069709b84"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/72237fdc-7899-845b-4fa9-7df806cf27fc.jpeg?a=1e51176b-1238-a3a5-afd3-fd3d16ed0c14"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/f2cde77e-aac5-6538-9f72-50f73ff800a8.jpeg?a=ddd81bd4-8a4c-a06d-d8e3-f00d120c714d"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/c03b0b2b-58a1-6c38-45e8-ed4c25c47976.jpeg?a=5f88e764-0d9a-9bce-8c14-f757d54398e8"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/96dfdcfe-8910-7be7-c319-f474f962c8b8.jpeg?a=0fbae9a2-f037-d120-ea7e-102ddd69abda"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/21f19f20-d50e-3523-99cc-5a055feb94b3.jpeg?a=fa638d47-30bb-546f-8cb7-3af075fd9a48"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/5bad64d1-92c7-74b9-8f80-c264370e7394.jpeg?a=45e16f82-5775-795b-f39b-654913fc37c1"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/872487a5-2f0a-a904-8a1e-77ff70168156.jpeg?a=a2b64673-738a-d2a5-94cd-3341100f5680"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/55041837-9518-fe8a-748f-c7d2967f63c8.jpeg?a=03867a1b-5835-8b6b-6c76-920d69c43983"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/22eddc3e-e05b-ac59-525d-0e67cc856956.jpeg?a=e8495592-fb5d-9ed8-6811-ce7c85dbd98d"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/eed8edc4-8c1f-a987-43c3-3fd69b239815.png?a=294bae67-fcad-3ff2-2680-44b49184a188"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/e7e4bc4a-e0cd-75b0-789e-26421ce9a743.png?a=24516df8-298b-9bec-2b9a-4ad7fe23812c"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/46cb9982-a79c-abf7-b1b7-1f17b405510c.png?a=2eec75fc-f87c-baf9-e929-e745fd339f5b"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/75b26a83-4270-e84e-4f44-cf3a83d476e5.jpeg?a=f2027a7d-1ec2-9268-b5b7-00cbb5da333c"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/d69fa03e-55cf-3432-2849-cd881f5fad91.jpeg?a=7c1e347b-c66b-1161-dbdf-83bdefd15fc4"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/4f2201f0-d663-186c-0b61-f5aa732d0a1c.jpeg?a=b7c7fee4-a605-e6a1-fdc6-32d9fc879e36"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/584ec588-2540-3d6d-9524-f489bdfa1b6f.jpeg?a=086d8124-154a-080f-9a05-b24a9f69d674"/>
            <img src="https://cdn.tictuk.com/ab3b346f-2ae6-5cfb-e5c6-3e3ffb9844ee/fe727cd4-3226-49da-4ff9-b6dda2c82bdc.jpeg?a=7322700e-799c-b11e-636d-e6d038cef8bf"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/60273b61-ee19-42ef-9e6c-02865e8ff314.png?a=b3706226-3010-b28c-84bb-8c9cdff41907"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/f73c4fc4-71f6-78b4-5638-f34e532a09a6.png?a=c837e47e-b857-c529-dc43-5b3bc435883b"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/37697356-4051-0be0-6638-3a8a2120bd00.png?a=e7b1faff-4d04-39df-ebfa-e8917422734c"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/1aac9693-c2da-36f6-f682-9f5d49d0dcfa.png?a=bc1f3863-9fa4-8163-2711-06ae241f90d2"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/a9106c98-fc97-8972-153f-4bb0ca227130.png?a=e7935314-11a6-e256-8b14-afb19d1c6283"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/c7837e7a-6611-95a1-6853-4faae07e5934.png?a=253a3ce7-f767-8188-5bf2-276975c166d8"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/f9fd5746-8546-5a32-6fe4-c4f43f9fc36a.png?a=4e7c53eb-e03e-7725-0b5e-f6f3564a8865"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/b5184766-50e0-e9ca-7c94-ad7c7a03b618.png?a=5e0a23ab-80bd-c9c7-9dcb-c791240bd710"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/14ed5c56-c374-1bb8-20ae-60b385d0c47c.png?a=c718c3a8-e1f6-5de0-9e9b-75e923865067"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/02f8bacd-1e84-4e18-bd49-8293f882a520.png?a=9a7c5ece-fb8f-8db6-5bf9-11867493c53b"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/a40c41af-9a3e-43f6-8c0b-bf5b0feab190.png?a=ce38f591-8997-a6f4-e689-720f14e526ce"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/39b744e6-0dfd-40a5-bbc6-43214e08b9e2.png?a=299e3461-3b4f-dbbb-a6d0-c7172e52c770"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/ff0f2516-f38a-f740-e4ed-39017cbc333c.png?a=4e5ae5b9-ffd2-9d4c-7748-9b76509cdb04"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/99647698-edec-40ac-9963-35faa7a225e6.jpeg?a=f46236e7-f2ee-47d5-7e25-7b534b2491ed"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/1885c46e-fd49-415d-9e6c-fed1dc0f723d.png?a=c39d177f-76fd-245b-e62e-35fddb823f8a"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/b224ea9b-aedb-42e3-82ec-bd0bf52ff184.png?a=868547d3-8928-eca2-2a01-5dea46036d29"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/e986244d-7c21-4db2-9c2d-7081209fdab2.png?a=d78a36f9-1a1b-0531-aae6-fcccb60e83f5"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/5887fd73-10c4-4543-8946-96092ef72ad2.png?a=2f20463a-b2b1-5d61-7fb4-33554e1bd95e"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/670ae272-a0c0-16a7-4333-8b0b84710352.jpeg?a=516a709a-e9bb-593d-7ddc-b6abe6d6e8e2"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/3e5f99fb-92e6-4c93-335d-b5da6e9f3b44.png?a=ef6f8548-9f79-a765-20a2-8bf14cb6a608"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/1f02c2ff-949c-47af-82fd-0ec21af3ae60.png?a=fafa41a1-6466-4a1f-d18e-fb10bb5349f5"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/f19d2c2c-28d2-633c-95d3-463015b60416.jpeg?a=b629d756-3a5c-90ea-6509-755dec0d0d30"/>
            <img src="https://cdn.tictuk.com/staging/6977b8a1-4b21-36af-b465-b08b7a13e7ee/3cffbb9c-6417-9c00-a662-d946c757997b.jpeg?a=757a7093-91ca-ba81-d99c-19488228a9c4"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/5d1e5e38-3653-19d1-4b75-a7052b757e32.png?a=19aebc58-2568-1ed2-19f6-9d10ec3060cd"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/7eb810df-7c68-c2d3-f67d-c6540d532f3b.png?a=c016b012-bb00-a3a6-9bda-b3d907543e18"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/f00b596f-f9cb-47b3-f40c-12ceab7b9648.png?a=92f9717e-0752-c09c-4e88-782017212047"/>
            <img src="https://cdn.tictuk.com/562ff848-1e3b-b3f7-fccd-7fa9ff01db34/8da9234d-2c1d-fbfe-4240-b0400c4710a7.png?a=0fcf64d5-16f9-d8b8-117c-9d90ed9338d0"/>     
            '''

        soup = GetUrlDocument.getHTMLSOUPEDDocument(
            root_url)
        # #List all the vailable deals and iterate
        parent_data = soup.find_all('div', {'class':'TabSection__StyledRoot-sc-wk122a-5 dcncwH'})

        productImagesReference = Utility.extract_image_sources(staticImagesReference)

        imageScriptStack = seedImages.test['menu']['items']

        for j, product in enumerate(parent_data):
            # ?1. Get the category name
            category = str(product.find('div', {"class": "Title__StyledTitleContainer-sc-13coufu-0 HooCZ app-title"}).find(
                'h2').get_text()).strip()
        

            if category not in _DEALS_UNAUTHORISED:
                try:
                    display_log(
                        Fore.YELLOW, '[{}]. {}'.format(j + 1, category))
                    #! Go through the indiviual products
                    meals_types = product.find('div', {'class':"MuiGrid-root TabSection__StyledItemsGrid-sc-wk122a-2 jGknSx MuiGrid-container"}).find_all('div', {'class': 'MuiGrid-root TabSection__StyledItem-sc-wk122a-6 dxAZHj MuiGrid-item MuiGrid-grid-xs-6 MuiGrid-grid-sm-6 MuiGrid-grid-md-auto MuiGrid-grid-lg-auto'})

                    for k, meal in enumerate(meals_types):
                        # Extract the picture, name, price and id?
                        product_site_id = meal['data-menu-item-id']

                        product_name = str(meal.find(
                            'h5', {"class": "MuiTypography-root MenuItem__StyledItemTitle-sc-gzsioo-5 hhROrr MuiTypography-h5"}).get_text()).strip()
                        product_price = str(meal.find(
                            'div', {"class": "MuiTypography-root jss4 MenuItem__StyledPrice-sc-gzsioo-0 iEaMQi MuiTypography-body1"}).find('span').get_text()).strip()
                        
                        currency, price = Utility.extract_currency_and_price(product_price)

                        product_price = price
                        
                        product_picture = 'placeholder'

                        try:
                            product_picture = imageScriptStack[product_site_id]['media']['logo']
                        except:
                            product_picture = Utility.find_image_by_id(productImagesReference, product_site_id)

                        
                        productId = str(uuid.uuid4())
                        sku = str(product_name).upper().replace(' ', '_')

                        # # Download the image to the Image Repository
                        newProductImage = ImageDownloader.upload_image_to_s3_and_save_to_dynamodb(image_url=product_picture, storeId=shop_fp, productId=productId, sku=sku, useProxy=False)

                       
                        # # ? SAVE in the db
                        # # Compile the whole product data model
                        TMP_DATA_MODEL = {
                            'id': productId,
                            'shop_fp': shop_fp,
                            'brand': _SHOP_NAME_,
                            'product_name': product_name,
                            'product_price': product_price,
                            'currency': currency,
                            'product_picture': [newProductImage],
                            'sku': sku,
                            'used_link': root_url,
                            'category': str(category).upper().strip(),
                            'subcategory': str(category).upper().strip(),
                            'shop_name': _SHOP_NAME_,
                            'website_link': root_url,
                            'createdAt': int(time.time()) * 1000,
                            'updatedAt': int(time.time()) * 1000
                        }

                        SaveOrUpdateItem.saveOrUpdateItem(TMP_DATA_MODEL=TMP_DATA_MODEL)
                        print(60*'-')
                except Exception as e:
                    print("An error occurred:", str(e))
                    traceback.print_exc()
            else:
                display_log(
                    Fore.RED, 'Unauthorised package [{}]'.format(category))

    except Exception as e:
        print("An error occurred:", str(e))
        traceback.print_exc()


#!Debug
launchBot()
