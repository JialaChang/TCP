import dearpygui.dearpygui as dpg
import socket
import threading
import platform
import os

class NetworkDPG:

    def __init__(self):
        self.s = None
        self.is_connected = False
        self.target_ip = ""
        self.target_port = ""

        self.setup_gui()

    def setup_gui(self):
        dpg.create_context()

        # 1. 處理中文字型 (DearPyGui 預設不支援中文，需手動載入字型檔)
        with dpg.font_registry():
            font_path = ""
            if platform.system() == "Windows":
                font_path = "C:/Windows/Fonts/msjh.ttc"  # 微軟正黑體
            elif platform.system() == "Darwin":
                font_path = "/System/Library/Fonts/PingFang.ttc" # Mac 蘋方體

            if font_path and os.path.exists(font_path):
                with dpg.font(font_path, 18) as default_font:
                    # 載入繁體中文與基礎英文/數字的編碼範圍
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Traditional_Chinese)
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.bind_font(default_font)
            else:
                print("[警告]: 找不到系統中文字型，介面可能出現亂碼。")

        # 2. 建立主要 UI 視窗
        with dpg.window(tag="Primary Window"):
            
            # 水平排列群組 (對應 Tkinter 的 grid 列)
            with dpg.group(horizontal=True):
                dpg.add_text("IP :")
                dpg.add_input_text(tag="entry_ip", width=150)
                
                dpg.add_text("port :")
                dpg.add_input_text(tag="entry_port", width=80)
                
                # DearPyGui 的 callback 會自動傳入 sender, app_data, user_data 三個參數
                dpg.add_button(label="設定", callback=self.save_ip)
                dpg.add_button(label="開始連線", tag="btn_connect", callback=self.toggle_connection)

            # 滾動文字框 (對應 Tkinter 的 ScrolledText)
            # 將寬度和高度設為 -1，代表填滿剩餘的視窗空間
            dpg.add_input_text(tag="log_window", multiline=True, readonly=True, width=-1, height=-1)

        # 3. 視窗設定 (對應原本的 setup_window 座標與大小計算)
        dpg.create_viewport(title="NET - DearPyGui", width=800, height=500)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        # 讓 "Primary Window" 成為主視窗，自動填滿畫面
        dpg.set_primary_window("Primary Window", True) 
        
        dpg.start_dearpygui()
        dpg.destroy_context()

    # ================== 以下為原本的邏輯區塊 ==================

    def save_ip(self, sender, app_data, user_data):
        """儲存IP及port"""
        self.target_ip = dpg.get_value("entry_ip")
        self.target_port = dpg.get_value("entry_port")
        self.output_message(f"[System]: IP saved -- {self.target_ip}:{self.target_port}")

    def establish_connect(self):
        """建立連線"""
        # 連線前確保抓到最新的輸入值
        self.target_ip = dpg.get_value("entry_ip")
        self.target_port = dpg.get_value("entry_port")

        if not self.target_ip or not self.target_port:
            self.output_message("[System]: Please enter IP and Port first.")
            return

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.target_ip, int(self.target_port)))
            self.output_message("[System]: Connect successfully")
            self.is_connected = True
            
            # 更新按鈕文字
            dpg.set_item_label("btn_connect", "中斷連線")

            # 用threading建立多執行緒
            t = threading.Thread(target=self.receive_data, daemon=True)
            t.start()
            
        except Exception as e:
            self.output_message(f"[System]: Connect failed -- {e}")
            if self.s:
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
        
        # 更新按鈕文字
        dpg.set_item_label("btn_connect", "開始連線")
        self.output_message("[System]: Disconnected")

    def toggle_connection(self, sender, app_data, user_data):
        """切換連線按鈕"""
        if not self.is_connected:
            self.output_message("[System]: Trying to connect...")
            self.establish_connect()
        else:
            self.stop_connect()

    def receive_data(self):
        """接收資料"""
        while self.is_connected:
            try:      
                self.data = self.s.recv(1024)
                if not self.data:
                    self.output_message("[System]: Server disconnect")
                    break

                hex_data = self.data.hex(' ').upper()
                self.output_message(f">> {hex_data}")

            except Exception as e:
                if self.is_connected:
                    self.output_message(f"[System]: Error -- {e}")
                break

        self.is_connected = False
        # 確保斷線後按鈕文字狀態正確
        dpg.set_item_label("btn_connect", "開始連線")

    def output_message(self, message):
        """"滾動窗輸出訊息"""
        # 取得目前的文字，將新訊息加上去後重新設定
        current_text = dpg.get_value("log_window")
        new_text = f"{current_text}{message}\n"
        dpg.set_value("log_window", new_text)
 
# 執行視窗
if __name__ == "__main__":
    NetworkDPG()