'''
    ./img/unprocessed/ フォルダに保存した１つ目のjpg形式ファイルを読み取り、
    ./img/interim/each_receipt/ フォルダに切り取ったレシート画像(png形式ファイル)を
    ./csv/ 読み取った結果(csv形式ファイル)を
    出力します。
'''
import sys
sys.path.append('./household_accounts')

import os
import cut_out_receipts
import ocr
import write_csv

class _P:
    def __init__(self, v):
        self._v = v
    
    def get(self):
        return self._v

def main():
    
    print("1.", "cut_out_receipts.main()")
    cut_out_receipts.main()
    print()

    print("2.", "results = ocr.main()")
    results = ocr.main()
    n = len(results)
    ocr.indicate_processing_status(n,n)
    print(" -->", n, "件")

    i=0
    for filepath, result in results.items():
        filename = os.path.basename(filepath)
        info_places = {}
        info_places['date']=_P(result['payment_date'])
        info_places['shop']=_P(filename)
        result['required'] = [1] * len(result['item'])
        item_places = {}
        for key, value in result.items():
            if not hasattr(value, '__iter__'):
                continue
            item_places[key] = []
            for v in value:
                item_places[key].append(_P(v))
        i += 1
        print()
        print("3.", i, ") write_csv.write_modified_result()", filepath)
        print(result)
        write_csv.write_modified_result(info_places, item_places)
    
    print()
    print("-----------------------------------")
    print(" Output Folders")
    print("-----------------------------------")
    print("    ./img/interim/each_receipt/")
    print("    ./csv/")
    print("-----------------------------------\n")
    
if __name__ == '__main__':
    main()
