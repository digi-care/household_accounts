import ocr
import cut_out_images
import gui_each_receipt
from gui_make_pages import MakePages
from gui_show_receipt_contours import MakePage1 
from get_file_path_list import get_input_path_list


cut_out_images.main()
input_path_list = get_input_path_list(relative_path='../img/interim/each_receipt', extension='png')
ocr_result = ocr.main(input_path_list)
gui = MakePages(input_path_list, ocr_result)
MakePage1(gui.page1, gui)

gui.mainloop()