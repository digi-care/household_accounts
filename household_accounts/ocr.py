import pyocr
import pyocr.builders
import re
import time
from datetime import datetime
from PIL import Image

from get_file_path_list import get_input_path_list


class OcrReceipt:
    date_regex = r'.{4}(/|年).{1,2}(/|月)[0-9]{1,2}'
    total_regex = r'(合計|小計|ノヽ言十|消費税).*[0-9]*'
    item_price_regex = r'([0-9]|\*|＊|※|[a-z]|[A-Z])\Z'  # 末尾が数字か軽減税率の記号かアルファベット（数字が読み取れていない場合用）
    price_regex = r'([0-9]|[a-z]|[A-Z])*\Z'  # アルファベットは数値が誤って変換されていることがあるため
    reduced_tax_regex = r'(\*|＊|※|W|w)'
    top_num_regex = r'^[0-9]*'
    tax_ex_regex = r'外税'
    tax_in_regex = r'(内税|内消費税等)'
    conversion_num_before = ['O', 'U', 'b', 'Z', '<', 'i']  # アルファベットとして認識されている価格を変換するため
    conversion_num_after = ['0', '0', '6', '2', '2', '1']


    def __init__(self, input_file):
        self.input_file = input_file
        receipt_content = self.ocr(self.input_file)
        self.payment_date = self.get_payment_date(receipt_content)
        self.tax_excluded = self.get_tax_excluded_included(receipt_content)
        main_contents = self.get_main_contents(receipt_content)
        self.reduced_tax_rate_flg = self.get_reduced_tax_rate_flg(main_contents)
        self.item, self.price = self.get_item_and_price(main_contents)
        self.price = self.modify_price(self.price)


    def ocr(self, input_file):
        tool = pyocr.get_available_tools()[0]
        receipt_ocr = tool.image_to_string(
            Image.open(input_file),
            lang='jpn',
            builder=pyocr.builders.LineBoxBuilder(tesseract_layout=4)
            )
        receipt_content = []
        for i in range(len(receipt_ocr)):
            content = receipt_ocr[i].content
            content = re.sub(r' ', r'', content)
            if content != '':
                receipt_content.append(content)
        return receipt_content


    def get_payment_date(self, receipt_content):
        payment_date = [re.search(self.date_regex, s).group() for s in receipt_content if re.search(self.date_regex+r'(\(|日)', s)]
        payment_date = payment_date[0] if payment_date != [] else '0000/00/00'
        payment_date = re.sub(r'(年|月)', r'/', payment_date)
        payment_date = datetime.strptime(payment_date, '%Y/%m/%d').strftime('%Y/%m/%d')
        return payment_date


    def get_tax_excluded_included(self, receipt_content):
        tax_excluded_flg = [1 for s in receipt_content if re.search(self.tax_ex_regex,s)]
        tax_included_flg = [1 for s in receipt_content if re.search(self.tax_in_regex,s)]
        tax_excluded = 1 if len(tax_excluded_flg)>len(tax_included_flg) else 0  # 外税判断の文字列が内税判断の文字列を超えた数存在すれば外税とする
        return tax_excluded


    def get_main_contents(self, receipt_content):
        try:
            start_low = [receipt_content.index(s) for s in receipt_content if re.search(self.date_regex, s)][0] + 1  # payment_dateの次の行が開始行とする
        except IndexError:
            start_low = 0  # payment_dateがない場合は最初の行を開始行とする

        sum_lows = [receipt_content.index(s) for s in receipt_content if re.search(self.total_regex, s)]
        end_low = sum_lows[0] if sum_lows != [] else len(receipt_content)

        main_contents = receipt_content[start_low:end_low]
        main_contents = [s for s in main_contents if re.search(self.item_price_regex, s)]  
        return main_contents


    def get_reduced_tax_rate_flg(self, main_contents):
        reduced_tax_rate_flg = [1 if re.search(self.reduced_tax_regex, s) else 0 for s in main_contents]
        return reduced_tax_rate_flg


    def get_item_and_price(self, main_contents):
        item_and_price = [re.sub(self.reduced_tax_regex, r'', s) for s in main_contents]  # 軽減税率の記号は取り除く
        item = [re.sub(self.price_regex, r'', s) for s in item_and_price]
        item = [re.sub(self.top_num_regex, r'', s) for s in item]
        item = [re.sub(r'\\', r'', s) for s in item]
        price = [re.search(self.price_regex, s).group() for s in item_and_price]
        return item, price
    

    def modify_price(self, price):
        for before, after in zip(self.conversion_num_before, self.conversion_num_after):
            price = [re.sub(before, after, p) for p in price]
        price = [re.sub(r'([A-Z]|[a-z])', r'', p) for p in price]
        return price


def summing_up_ocr_results(ocr):
    result = {}
    result['payment_date'] = ocr.payment_date
    result['item'] = ocr.item
    result['price'] = ocr.price
    result['reduced_tax_rate_flg'] = ocr.reduced_tax_rate_flg
    result['tax_excluded_flg'] = ocr.tax_excluded
    return result


def indicate_processing_status(no, num):
    process_per = round(no / num * 100, 0)
    process_bar = ('=' * no) + (' ' * (num - no))
    print('\r処理状況: [{}] {}%'.format(process_bar, process_per), end='')
    time.sleep(0.1)


def main():
    input_path_list = get_input_path_list('../img/interim/each_receipt', 'png')
    ocr_results = {}
    for i, input_file in enumerate(input_path_list):
        ocr = OcrReceipt(input_file)
        ocr_results[input_file] = summing_up_ocr_results(ocr)
        indicate_processing_status(i, len(input_path_list))
    return ocr_results

if __name__ == '__main__':
    main()