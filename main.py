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
    bot = BoarBot(token)
    boar = RandBoar()

    offset = bot.get_last_update_id(bot.get_updates(0)) + 1

    chinese_copypaste = '动态网自由门 天安門 天安门 法輪功 李洪志 Free Tibet 六四天安門事件 The Tiananmen Square protests of 1989 天安門大屠殺 The Tiananmen Square Massacre 反右派鬥爭 The Anti-Rightist Struggle 大躍進政策 The Great Leap Forward 文化大革命 The Great Proletarian Cultural Revolution 人權 Human Rights 民運 Democratization 自由 Freedom 獨立 Independence 多黨制 Multi-party system 台灣 臺灣 Taiwan Formosa 中華民國 Republic of China 西藏 土伯特 唐古特 Tibet 達賴喇嘛 Dalai Lama 法輪功 Falun Dafa 新疆維吾爾自治區 The Xinjiang Uyghur Autonomous Region 諾貝爾和平獎 Nobel Peace Prize 劉暁波 Liu Xiaobo 民主 言論 思想 反共 反革命 抗議 運動 騷亂 暴亂 騷擾 擾亂 抗暴 平反 維權 示威游行 李洪志 法輪大法 大法弟子 強制斷種 強制堕胎 民族淨化 人體實驗 肅清 胡耀邦 趙紫陽 魏京生 王丹 還政於民 和平演變 激流中國 北京之春 大紀元時報 九評論共産黨 獨裁 專制 壓制 統一 監視 鎮壓 迫害 侵略 掠奪 破壞 拷問 屠殺 活摘器官 誘拐 買賣人口 遊進 走私 毒品 賣淫 春畫 賭博 六合彩 天安門 天安门 法輪功 李洪志 Winnie the Pooh 劉曉波动态网自由门'
    chinese_re = re.compile(r'[\u4e00-\u9fff]{3,}')

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
                        bot.send_message(chat_id, chinese_copypaste, reply)

            except:
                print('Error occurred')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
