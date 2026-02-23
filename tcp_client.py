import dearpygui.dearpygui as dpg
import socket
import threading
import platform
import os


class Network:

    def __init__(self):

        self.s = None
        self.is_connected = False
        self.target_ip = ""
        self.target_port = ""
        self.data_format = ""

        self.setup_gui()


    def setup_gui(self):
        """建立視窗 UI """

        dpg.create_context()

        # 文字設定
        with dpg.font_registry():
            font_path = ""
            if platform.system() == "Windows":
                font_path = "C:/Windows/Fonts/msjh.ttc"  # 微軟正黑體
            elif platform.system() == "Darwin":
                font_path = "/System/Library/Fonts/PingFang.ttc" # Mac 蘋方體

            if font_path and os.path.exists(font_path):
                with dpg.font(font_path, 18) as default_font:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)

                dpg.bind_font(default_font)

        # 建立主視窗 UI, DearPyGui 底層是 C++ 因此不用 (用self) 儲存 Python 物件
        with dpg.window(tag="primary_window"):

            # 水平輸入欄
            with dpg.group(horizontal=True):
                dpg.add_text("IP :")
                dpg.add_input_text(tag="entry_ip", width=150)

                dpg.add_text("port :")
                dpg.add_input_text(tag="entry_port", width=80)

                dpg.add_text(" " * 5)   # 用空格做間距
                dpg.add_combo(
                    items=["Text(UTF-8)", "Hex", "Binary"],
                    tag="combo_format",
                    width=120
                )

                dpg.add_text(" " * 5) 
                dpg.add_button(label="Save", tag="btn_setip", callback=self.save_setting) # callback 會傳入 sender, app_data, user_data 三個參數

                dpg.add_text(" " * 20)
                dpg.add_button(label="Connect", tag="btn_connect", callback=self.toggle_connection)

            # 滾動窗
            with dpg.child_window(tag="log_window", width=-1, height=-1):    # 寬高設 -1 填滿剩下的空間
                pass

        # 建立視窗
        dpg.create_viewport(title="Network", width=800, height=500)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        dpg.set_primary_window("primary_window", True)
        dpg.maximize_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


    def save_setting(self, *args):   # args 接收傳來的其他參數
        """儲存設定"""

        self.target_ip = dpg.get_value("entry_ip")
        self.target_port = dpg.get_value("entry_port")
        self.data_format = dpg.get_value("combo_format")

        self.output_message(f"[System] : IP saved -- {self.target_ip}:{self.target_port}")
        self.output_message(f"[System] : Data formate set to {self.data_format}")

    def establish_connect(self):
        """建立連線"""

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET : IPv4 協定 ; SOCK_STREAM : TCP 協定
            self.s.connect((self.target_ip, int(self.target_port)))
            self.output_message("[System] : Connect sucessfully")
            self.is_connected = True
            dpg.set_item_label("btn_connect", "Disconnect")

            # 用threading建立多執行緒
            t = threading.Thread(target=self.receive_data, daemon=True) # daemon=True -> 主執行緒被關閉時，副執行緒也同樣會被關閉 
            t.start()
            
        except Exception as e:
            self.output_message(f"[System] : Connect failed -- {e}")
            self.s.close()


    def stop_connect(self):
        """中斷連線"""

        self.is_connected = False
        if self.s:
            try:
                self.s.shutdown(socket.SHUT_RDWR)
                self.s.close()
            except:
                pass
        
        dpg.set_item_label("btn_connect", "Connect")        
        self.output_message("[System] : Disconnected")


    def toggle_connection(self):
        """切換連線按鈕"""
        if not self.is_connected:
            self.output_message("[System] : Trying to connect...")
            self.establish_connect()
        else:
            self.stop_connect()


    def receive_data(self):
        """接收資料"""

        while self.is_connected:
            try:      
                self.data = self.s.recv(1024)
                if not self.data:
                    self.output_message("[System] : Sever disconnect")
                    break
                
                # 資料輸出型態
                if self.data_format == "Text(UTF-8)":
                    self.output_message(f">> {self.data.decode('utf-8', errors='replace')}")
                elif self.data_format == "Hex":
                    self.output_message(f">> {self.data.hex(' ').upper()}") # hex(' ') 的作用是在每個 Byte 之間插空格
                elif self.data_format == "Binary":
                    # for 跑 bytes (self.data) 會把每個 byte 變成 0~255 的整數
                    # '08b' : b -> 二進位, 8 -> 讓字串是八個字元, 0 -> 如果有缺補零
                    self.output_message(f">> {' '.join(format(byte, '08b') for byte in self.data)}")

            except Exception as e:
                if self.is_connected:
                    self.output_message(f"[System] : Error -- {e}")
                break

        self.is_connected = False
        dpg.set_item_label("btn_connect", "Connect")        


    def output_message(self, message):
        """"滾動窗輸出訊息 & 整理頁面"""

        dpg.add_text(message, parent="log_window")
        dpg.set_y_scroll("log_window", 999)

        if len(dpg.get_item_children("log_window", 1)) > 500:
            dpg.delete_item(dpg.get_item_children("log_window", 1)[0]) # [0] -> 最上面的一行
        

# 執行視窗
if __name__ == "__main__":
    Network()