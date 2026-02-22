import tkinter as tk
from tkinter import scrolledtext
import socket
import threading

class Network:

    def __init__(self, root):

        self.root = root
        self.root.title("NET")
        self.s = None
        self.is_connected = False
        

        self.target_ip = tk.StringVar(value="")
        self.target_port = tk.StringVar(value="")

        self.setup_window()
        self.create_wingets()

    def setup_window(self):
        """視窗大小與位置"""
        
        window_width = self.root.winfo_screenwidth()
        window_height = self.root.winfo_screenheight()

        width = int(window_width * 0.5)
        height = int(window_height * 0.5)
        left = int((window_width - width) / 2)
        top = int((window_height - height) / 2)

        self.root.geometry(f'{width}x{height}+{left}+{top}')

    def create_wingets(self):
        """"建立物件"""

        # ip輸入
        self.frame_ip = tk.Frame(self.root)
        self.frame_ip.grid(row=0, column=0, columnspan=3, sticky='w')

        tk.Label(self.frame_ip, text="IP : ").grid(row=0, column=0, padx=10, pady=10)

        self.entry_ip = tk.Entry(self.frame_ip, width=16)
        self.entry_ip.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.frame_ip, text="port : ").grid(row=0, column=2, padx=10, pady=10)

        self.entry_port = tk.Entry(self.frame_ip, width=8)
        self.entry_port.grid(row=0, column=3, padx=10, pady=10)

        self.btn_saveip = tk.Button(self.frame_ip, text="設定", command=self.save_ip)
        self.btn_saveip.grid(row=0, column=4, padx=10, pady=10)

        # 滾動窗
        self.log_window = scrolledtext.ScrolledText(self.root, width=80, height=15, font=("Consolas", 10), state='disabled')
        self.log_window.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # 開始&暫停按鈕
        self.btn_connect = tk.Button(self.root, text="開始連線", command=self.toggle_connection)
        self.btn_connect.grid(row=0, column=2, padx=10, pady=10)

    def save_ip(self):
        """儲存IP及port"""

        self.target_ip.set(self.entry_ip.get()) # entry_ip 是物件 -> 用 get() 取完才是字串或數值
        self.target_port.set(self.entry_port.get())

        self.output_message(f"[System]: IP saved -- {self.target_ip.get()}:{self.target_port.get()}")

    def establish_connect(self):
        """建立連線"""

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET : IPv4 協定 ; SOCK_STREAM : TCP 協定
            self.s.connect((self.target_ip.get(), int(self.target_port.get())))
            self.output_message("[System]: Connect sucessfully")
            self.is_connected = True
            self.btn_connect.config(text="中斷連線")

            # 用threading建立多執行緒
            t = threading.Thread(target=self.receive_data, daemon=True) # daemon=True -> 主執行緒被關閉時，副執行緒也同樣會被關閉 
            t.start()
            
        except Exception as e:
            self.output_message(f"[System]: Connect failed -- {e}")
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
        
        self.btn_connect.config(text="開始連線")
        self.output_message("[System]: Disconnected")


    def toggle_connection(self):
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
                    self.output_message("[System]: Sever disconnect")
                    break

                hex_data = self.data.hex(' ').upper()
                self.output_message(f">> {hex_data}")

            except Exception as e:
                if self.is_connected:
                    self.output_message(f"[System]: Error -- {e}")
                break

        self.is_connected = False
        self.btn_connect.config(text="開始連線")

    def output_message(self, message):
        """"滾動窗輸出訊息"""

        self.log_window.config(state='normal')
        self.log_window.insert('end', f"{message}\n")
        self.log_window.config(state='disabled')
        self.log_window.see('end')      
 
# 執行視窗
if __name__ == "__main__":
    root = tk.Tk()
    Network(root)
    root.mainloop()