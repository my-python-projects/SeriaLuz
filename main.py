import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import serial.tools.list_ports

class SerialMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SeriaLuz - Monitor Serial")
        self.root.resizable(width=0, height=0)

        self.port = tk.StringVar()
        self.baudrate = tk.StringVar(value="9600")
        self.data_format = tk.StringVar(value="ASCII")
        
        # Configurar elementos da interface
        self.create_widgets()

        # Variáveis de estado
        self.ser = None

    def create_widgets(self):
        # Frame de configurações
        config_frame = ttk.LabelFrame(self.root, text="Configurações")
        config_frame.grid(column=0, row=0, padx=10, pady=10)

        # Porta serial
        ttk.Label(config_frame, text="Porta:").grid(column=0, row=0, sticky=tk.W)
        ports = self.get_serial_ports()
        port_menu = ttk.Combobox(config_frame, textvariable=self.port, values=ports)
        port_menu.grid(column=1, row=0)
        
        # Baudrate
        ttk.Label(config_frame, text="Baudrate:").grid(column=0, row=1, sticky=tk.W)
        baudrate_entry = ttk.Entry(config_frame, textvariable=self.baudrate)
        baudrate_entry.grid(column=1, row=1)
        
        # Formato dos dados
        ttk.Label(config_frame, text="Formato dos Dados:").grid(column=0, row=2, sticky=tk.W)
        format_menu = ttk.Combobox(config_frame, textvariable=self.data_format, values=["ASCII", "Hexadecimal"])
        format_menu.grid(column=1, row=2)

        # Botão de conectar
        self.connect_button = ttk.Button(config_frame, text="Conectar", command=self.toggle_connection)
        self.connect_button.grid(column=0, row=3, columnspan=2, pady=5)
        
        # Frame de envio
        send_frame = ttk.LabelFrame(self.root, text="Enviar Dados")
        send_frame.grid(column=0, row=1, padx=10, pady=10)

        self.send_entry = ttk.Entry(send_frame, width=50)
        self.send_entry.grid(column=0, row=0, padx=5, pady=5)
        send_button = ttk.Button(send_frame, text="Enviar", command=self.send_data)
        send_button.grid(column=1, row=0, padx=5, pady=5)

        # Frame de recebimento
        receive_frame = ttk.LabelFrame(self.root, text="Receber Dados")
        receive_frame.grid(column=0, row=2, padx=10, pady=10)

        self.receive_text = scrolledtext.ScrolledText(receive_frame, width=60, height=20, state='disabled')
        self.receive_text.grid(column=0, row=0, padx=5, pady=5)
        
    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def toggle_connection(self):
        if self.ser is None:
            try:
                self.ser = serial.Serial(self.port.get(), self.baudrate.get())
                self.connect_button.config(text="Desconectar")
                self.root.after(100, self.read_data)
            except Exception as e:
                messagebox.showerror("Erro de Conexão", str(e))
        else:
            self.ser.close()
            self.ser = None
            self.connect_button.config(text="Conectar")
        
    def read_data(self):
        if self.ser is not None and self.ser.in_waiting > 0:
            data = self.ser.read(self.ser.in_waiting)
            if self.data_format.get() == "ASCII":
                data = data.decode('utf-8')
            elif self.data_format.get() == "Hexadecimal":
                data = data.hex()
            
            self.receive_text.config(state='normal')
            self.receive_text.insert(tk.END, data + '\n')
            self.receive_text.config(state='disabled')
        self.root.after(100, self.read_data)

    def send_data(self):
        if self.ser is not None:
            data = self.send_entry.get()
            if self.data_format.get() == "ASCII":
                self.ser.write(data.encode('utf-8'))
            elif self.data_format.get() == "Hexadecimal":
                try:
                    hex_data = bytes.fromhex(data)
                    self.ser.write(hex_data)
                except ValueError:
                    messagebox.showerror("Erro de Formato", "Formato hexadecimal inválido.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitorApp(root)
    root.mainloop()
