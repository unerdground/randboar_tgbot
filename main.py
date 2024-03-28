import base64
import random
import re
import time

import numpy as np
from PIL import Image, ImageEnhance
from blendmodes.blend import blendLayers, BlendType
from io import BytesIO
import requests
import colorsys


class RandBoar:
    random.seed()

    def __init__(self):
        self.rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
        self.hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)
        # Manually selected blend modes with funny output
        self.blend_type = [BlendType.MULTIPLY,
                           BlendType.ADDITIVE,
                           BlendType.COLOURBURN,
                           BlendType.DIFFERENCE,
                           BlendType.NEGATION,
                           BlendType.XOR,
                           BlendType.OVERLAY,
                           BlendType.GRAINEXTRACT,
                           BlendType.GRAINMERGE,
                           BlendType.DIVIDE,
                           BlendType.EXCLUSION]

    # Hue shifting for main image
    def shift_hue(self, arr, hout):
        r, g, b, a = np.rollaxis(arr, axis=-1)
        h, s, v = self.rgb_to_hsv(r, g, b)
        h = hout
        r, g, b = self.hsv_to_rgb(h, s, v)
        arr = np.dstack((r, g, b, a))
        return arr

    # Mask creation
    def make_mask(self, img):
        # Make mask Black and White
        bnw = ImageEnhance.Color(img)
        img = bnw.enhance(0)

        # Set random brightness
        brightness = ImageEnhance.Brightness(img)
        factor = random.randrange(0, 25000) * .0001
        print('B:{}'.format(factor))

        img = brightness.enhance(factor)

        # Set max contrast
        contrast = ImageEnhance.Contrast(img)
        img = contrast.enhance(100.0)

        return img

    # Colorizing main image with random value
    def colorize(self, img):
        img = img.convert('RGBA')
        arr = np.array(np.asarray(img).astype('float'))
        factor = random.randrange(4000)
        print('H:{}'.format(factor))
        img = Image.fromarray(self.shift_hue(arr, factor / 360.).astype('uint8'), 'RGBA')

        return img

    # Blend images with random blend mode
    def combine(self, img1, img2):
        factor = random.choice(self.blend_type)
        print(factor)
        dst = blendLayers(img1, img2, factor)
        return dst

    # Main function, handles boar creation
    def boar(self):
        sticker = Image.open('sticker.webp')
        result = self.combine(self.make_mask(sticker), self.colorize(sticker))

        return result


# Just a bot handler
class BoarBot:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset):
        try:
            method = 'getUpdates'
            parameters = {'timeout': 30, 'offset': offset, 'allowed_updates': ["message"]}
            response = requests.get(self.api_url + method, parameters)
            return response.json()['result']
        except:
            print('updates error')

    def send_sticker(self, chat_id, boar, reply):
        try:
            parameters = {'chat_id': chat_id, 'reply_to_message_id': reply, 'allow_sending_without_reply': True}
            files = {'sticker': boar}
            method = 'sendSticker'
            response = requests.post(self.api_url + method, data=parameters, files=files)
            return response
        except:
            print('sticker error')

    # def leave_group(self):
    #     method = 'leaveChat'
    #     parameters = {'chat_id': '@THIS_IS_JUST_A_TEST'}
    #     response = requests.get(self.api_url + method, parameters)

    def send_message(self, chat_id, text, reply):
        try:
            parameters = {'chat_id': chat_id, 'text': text, 'reply_to_message_id': reply, 'allow_sending_without_reply': True}
            method = 'sendMessage'
            response = requests.post(self.api_url + method, parameters)
            return response
        except:
            print('message error')

    @staticmethod
    def get_last_update_id(data):
        return data[-1]['update_id']


# Convert Image to form-data for telegram
def convert_to_data(img):
    buffer = BytesIO()
    buffer.name = 'image.webp'
    img.save(buffer, 'WEBP')
    buffer.seek(0)

    return buffer


def main():

    # Using base64 string to avoid storing chinese symbols directly
    chinese_copypaste_base64 = "5Yqo5oCB572R6Ieq55Sx6ZeoIOWkqeWuiemWgCDlpKnlronpl6gg5rOV6Lyq5YqfIOadjua0quW/lyBGcmVlIFRpYmV0IOWFreWbm+WkqeWuiemWgOS6i+S7tiBUaGUgVGlhbmFubWVuIFNxdWFyZSBwcm90ZXN0cyBvZiAxOTg5IOWkqeWuiemWgOWkp+WxoOauuiBUaGUgVGlhbmFubWVuIFNxdWFyZSBNYXNzYWNyZSDlj43lj7PmtL7prKXniK0gVGhlIEFudGktUmlnaHRpc3QgU3RydWdnbGUg5aSn6LqN6YCy5pS/562WIFRoZSBHcmVhdCBMZWFwIEZvcndhcmQg5paH5YyW5aSn6Z2p5ZG9IFRoZSBHcmVhdCBQcm9sZXRhcmlhbiBDdWx0dXJhbCBSZXZvbHV0aW9uIOS6uuasiiBIdW1hbiBSaWdodHMg5rCR6YGLIERlbW9jcmF0aXphdGlvbiDoh6rnlLEgRnJlZWRvbSDnjajnq4sgSW5kZXBlbmRlbmNlIOWkmum7qOWItiBNdWx0aS1wYXJ0eSBzeXN0ZW0g5Y+w54GjIOiHuueBoyBUYWl3YW4gRm9ybW9zYSDkuK3oj6/msJHlnIsgUmVwdWJsaWMgb2YgQ2hpbmEg6KW/6JePIOWcn+S8r+eJuSDllJDlj6TnibkgVGliZXQg6YGU6LO05ZaH5ZibIERhbGFpIExhbWEg5rOV6Lyq5YqfIEZhbHVuIERhZmEg5paw55aG57at5ZC+54i+6Ieq5rK75Y2AIFRoZSBYaW5qaWFuZyBVeWdodXIgQXV0b25vbW91cyBSZWdpb24g6Ku+6LKd54i+5ZKM5bmz542OIE5vYmVsIFBlYWNlIFByaXplIOWKieaageazoiBMaXUgWGlhb2JvIOawkeS4uyDoqIDoq5Yg5oCd5oOzIOWPjeWFsSDlj43pnanlkb0g5oqX6K2wIOmBi+WLlSDpqLfkuoIg5pq05LqCIOmot+aTviDmk77kuoIg5oqX5pq0IOW5s+WPjSDntq3mrIog56S65aiB5ri46KGMIOadjua0quW/lyDms5XovKrlpKfms5Ug5aSn5rOV5byf5a2QIOW8t+WItuaWt+eoriDlvLfliLbloJXog44g5rCR5peP5reo5YyWIOS6uumrlOWvpumplyDogoXmuIUg6IOh6ICA6YKmIOi2mee0q+mZvSDprY/kuqznlJ8g546L5Li5IOmChOaUv+aWvOawkSDlkozlubPmvJToroog5r+A5rWB5Lit5ZyLIOWMl+S6rOS5i+aYpSDlpKfntIDlhYPmmYLloLEg5Lmd6KmV6KuW5YWx55Sj6buoIOeNqOijgSDlsIjliLYg5aOT5Yi2IOe1seS4gCDnm6PoppYg6Y6u5aOTIOi/q+WusyDkvrXnlaUg5o6g5aWqIOegtOWjniDmi7fllY8g5bGg5q66IOa0u+aRmOWZqOWumCDoqpjmi5Ag6LK36LOj5Lq65Y+jIOmBiumAsiDotbDnp4Eg5q+S5ZOBIOizo+a3qyDmmKXnlasg6LOt5Y2aIOWFreWQiOW9qSDlpKnlronploAg5aSp5a6J6ZeoIOazlei8quWKnyDmnY7mtKrlv5cgV2lubmllIHRoZSBQb29oIOWKieabieazouWKqOaAgee9keiHqueUsemXqA=="
    chinese_re = re.compile(r'[\u4e00-\u9fff]{3,}')

    bot = BoarBot(token)
    boar = RandBoar()

    offset = bot.get_last_update_id(bot.get_updates(0)) + 1

    while True:
        updates = bot.get_updates(offset)

        if len(updates) > 0:
            offset = bot.get_last_update_id(updates) + 1

        for i in range(0, len(updates)):
            try:
                try:
                    update_text = updates[i]['message']['text']
                except:
                    print('Not a text')
                    break
                chat_id = updates[i]['message']['chat']['id']
                reply = updates[i]['message']['message_id']

                if update_text in ['/randboar', '/randboar@beshenyboar_bot']:
                    chance = random.randrange(200, 1001)
                    print(chance)
                    if chance == 1000:
                        img = Image.open('rare_sticker.webp')
                        bot.send_sticker(chat_id, convert_to_data(img), reply)
                    if 990 <= chance < 1000:
                        bot.send_message(chat_id, 'oink oink', reply)
                    if 980 <= chance < 990:
                        bot.send_message(chat_id, '🐗', reply)
                    if 970 <= chance < 980:
                        bot.send_message(chat_id, 'boar', reply)
                    if 940 <= chance < 970:
                        img = Image.open('rare_sticker_2.webp')
                        bot.send_sticker(chat_id, convert_to_data(img), reply)
                    if 930 <= chance < 940:
                        img = Image.open('rare_sticker_3.webp')
                        bot.send_sticker(chat_id, convert_to_data(img), reply)
                    if 920 <= chance < 930:
                        img = Image.open('rare_sticker_4.webp')
                        bot.send_sticker(chat_id, convert_to_data(img), reply)
                    if 910 <= chance < 920:
                        img = Image.open('rare_sticker_5.webp')
                        bot.send_sticker(chat_id, convert_to_data(img), reply)
                    if chance < 910:
                        img = boar.boar()
                        bot.send_sticker(chat_id, convert_to_data(img), reply)

                else:
                    if (chinese_re.search(update_text)):
                        bot.send_message(chat_id, base64.b64decode(chinese_copypaste_base64).decode('utf-8'), reply)
                        bot.send_sticker(chat_id, convert_to_data(boar.boar()), None)

            except:
                print('Error occurred')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
