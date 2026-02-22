import tkinter as tk
from tkinter import scrolledtext
import socket
import threading

class Network:

    def __init__(self, root):

        self.root = root
        self.root.title("NET")
        self.root.grid_columnconfigure(0, weight=1)

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
        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, columnspan=3)

        tk.Label(self.frame, text="IP : ").grid(row=0, column=0, padx=10, pady=10)

        self.entry_ip = tk.Entry(self.frame)
        self.entry_ip.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.frame, text="port : ").grid(row=0, column=2, padx=10, pady=10)

        self.entry_port = tk.Entry(self.frame)
        self.entry_port.grid(row=0, column=3, padx=10, pady=10)

        self.btn_saveip = tk.Button(self.frame, text="設定", command=self.save_ip)
        self.btn_saveip.grid(row=0, column=4, padx=10, pady=10)

        # 滾動窗
        self.log_window = scrolledtext.ScrolledText(self.root, width=80, height=15, font=("Consolas", 10), state='disabled')
        self.log_window.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # 開始按鈕
        self.btn_start = tk.Button(self.root, text="開始連線", command=self.establish_connect)
        self.btn_start.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    def save_ip(self):
        """儲存IP及port"""

        self.target_ip.set(self.entry_ip.get()) # entry_ip 是物件 -> 用 get() 取完才是字串或數值
        self.target_port.set(self.entry_port.get())

        self.output_message(f"IP saved : {self.target_ip.get()}:{self.target_port.get()}")

    def establish_connect(self):
        """建立連線"""
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET : IPv4 協定 ; SOCK_STREAM : TCP 協定

        try:
            self.output_message("Trying to connect...")
            self.s.connect((self.target_ip.get(), int(self.target_port.get())))
            self.output_message("Connect sucessfully! Start to receive data...")
            
            # 用threading建立多執行緒
            t = threading.Thread(target=self.receive_data, daemon=True) # daemon=True -> 主執行緒被關閉時，副執行緒也同樣會被關閉 
            t.start()

        except Exception as e:
            self.output_message(f"Connection failed : {e}")
            self.s.close()

    def receive_data(self):
        """接收資料"""

        try:      
            while True:
                self.data = self.s.recv(1024)
                if not self.data:
                    self.output_message("Disconnect...")
                    break
                self.output_message(f">> {self.data.decode(errors='ignore')}")

        except Exception as e:
            self.output_message(f"error : {e}")

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