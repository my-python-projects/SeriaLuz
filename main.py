import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import PhotoImage, Toplevel, Label
import serial
import serial.tools.list_ports
import json
import os

class SeriaLuz:
    def __init__(self, root):
        self.root = root
        self.root.title("SeriaLuz - Monitor Serial")

        # Centralizar a janela
        window_width = 550
        window_height = 550
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height/2 - window_height/2)
        position_right = int(screen_width/2 - window_width/2)
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        self.port = tk.StringVar()
        self.baudrate = tk.StringVar(value="9600")
        self.data_format = tk.StringVar(value="ASCII")
        self.data_bits = tk.StringVar(value="8")
        self.parity = tk.StringVar(value="None")
        self.stop_bits = tk.StringVar(value="1")
        self.flow_control = tk.StringVar(value="None")

        # Configurar elementos da interface
        self.create_widgets()

        # Variáveis de estado
        self.ser = None

        # Carregar configurações salvas
        self.load_settings()

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=1, fill="both")

        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)
        notebook.add(tab1, text='Configuração')
        notebook.add(tab2, text='Enviar/Receber')
        notebook.add(tab3, text='Configurações Avançadas')

        self.create_config_tab(tab1)
        self.create_send_receive_tab(tab2)
        self.create_advanced_settings_tab(tab3)

    def create_config_tab(self, tab):
        config_frame = ttk.LabelFrame(tab, text="Configurações")
        config_frame.pack(padx=10, pady=10, fill="x", expand=True)

        # Porta serial
        ttk.Label(config_frame, text="Porta:").grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        self.port_menu = ttk.Combobox(config_frame, textvariable=self.port)
        self.port_menu.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W)
        self.update_ports()

        # Botão para atualizar portas seriais
        update_ports_button = ttk.Button(config_frame, text="Atualizar Portas", command=self.update_ports)
        update_ports_button.grid(column=2, row=0, padx=5, pady=5)

        # Baudrate
        ttk.Label(config_frame, text="Baudrate:").grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
        baudrate_entry = ttk.Entry(config_frame, textvariable=self.baudrate)
        baudrate_entry.grid(column=1, row=1, padx=5, pady=5, sticky=tk.W)

        # Formato dos dados
        ttk.Label(config_frame, text="Formato dos Dados:").grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
        format_menu = ttk.Combobox(config_frame, textvariable=self.data_format, values=["ASCII", "Hexadecimal"])
        format_menu.grid(column=1, row=2, padx=5, pady=5, sticky=tk.W)

        # Botões de conectar e salvar configurações
        self.connect_button = ttk.Button(config_frame, text="Conectar", command=self.toggle_connection)
        self.connect_button.grid(column=0, row=3, pady=10, padx=5, sticky=tk.W)

        save_button = ttk.Button(config_frame, text="Salvar Configurações", command=self.save_settings)
        save_button.grid(column=1, row=3, pady=10, padx=5, sticky=tk.W)

        # Indicador de status de conexão
        self.status_label = ttk.Label(config_frame, text="Desconectado", foreground="red")
        self.status_label.grid(column=2, row=3, padx=5)

    def create_send_receive_tab(self, tab):
        # Frame de envio
        send_frame = ttk.LabelFrame(tab, text="Enviar Dados")
        send_frame.pack(padx=10, pady=10, fill="x", expand=True)

        self.send_entry = ttk.Entry(send_frame, width=50)
        self.send_entry.grid(column=0, row=0, padx=5, pady=5)
        send_button = ttk.Button(send_frame, text="Enviar", command=self.send_data)
        send_button.grid(column=1, row=0, padx=5, pady=5)

        # Frame de recebimento
        receive_frame = ttk.LabelFrame(tab, text="Receber Dados")
        receive_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.receive_text = scrolledtext.ScrolledText(receive_frame, width=60, height=20, state='disabled')
        self.receive_text.pack(padx=5, pady=5, fill="both", expand=True)

        clear_button = ttk.Button(receive_frame, text="Limpar", command=self.clear_received_data)
        clear_button.pack(padx=5, pady=5)

    def create_advanced_settings_tab(self, tab):
        advanced_frame = ttk.LabelFrame(tab, text="Configurações Avançadas")
        advanced_frame.pack(padx=10, pady=10, fill="x", expand=True)

        # Data Bits
        ttk.Label(advanced_frame, text="Bits de Dados:").grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        data_bits_menu = ttk.Combobox(advanced_frame, textvariable=self.data_bits, values=["5", "6", "7", "8"])
        data_bits_menu.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(advanced_frame, "Bits de Dados:\nNúmero de bits usados para representar cada caractere (normalmente 8).").grid(column=2, row=0, padx=5, pady=5)

        # Parity
        ttk.Label(advanced_frame, text="Paridade:").grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
        parity_menu = ttk.Combobox(advanced_frame, textvariable=self.parity, values=["None", "Even", "Odd", "Mark", "Space"])
        parity_menu.grid(column=1, row=1, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(advanced_frame, "Paridade:\nMétodo de verificação de erros.\nNone: Sem paridade\nEven: Paridade par\nOdd: Paridade ímpar\nMark: Bit fixo em 1\nSpace: Bit fixo em 0").grid(column=2, row=1, padx=5, pady=5)

        # Stop Bits
        ttk.Label(advanced_frame, text="Bits de Parada:").grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
        stop_bits_menu = ttk.Combobox(advanced_frame, textvariable=self.stop_bits, values=["1", "1.5", "2"])
        stop_bits_menu.grid(column=1, row=2, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(advanced_frame, "Bits de Parada:\nNúmero de bits usados para indicar o fim de um byte (1, 1.5, 2).").grid(column=2, row=2, padx=5, pady=5)

        # Flow Control
        ttk.Label(advanced_frame, text="Controle de Fluxo:").grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)
        flow_control_menu = ttk.Combobox(advanced_frame, textvariable=self.flow_control, values=["None", "RTS/CTS", "XON/XOFF"])
        flow_control_menu.grid(column=1, row=3, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(advanced_frame, "Controle de Fluxo:\nMétodo para controlar o fluxo de dados.\nNone: Sem controle de fluxo\nRTS/CTS: Controle de fluxo por hardware\nXON/XOFF: Controle de fluxo por software").grid(column=2, row=3, padx=5, pady=5)

    def create_info_icon(self, parent, message):
        def show_info(event):
            top = Toplevel()
            top.title("Informação")
            Label(top, text=message, padx=10, pady=10).pack()
            top.geometry(f'+{self.root.winfo_pointerx()}+{self.root.winfo_pointery()}')
        info_icon = ttk.Label(parent, text="i", foreground="blue", cursor="hand2")
        info_icon.bind("<Button-1>", show_info)
        return info_icon

    def update_ports(self):
        ports = self.get_serial_ports()
        self.port_menu['values'] = ports
        if ports:
            self.port_menu.current(0)

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def toggle_connection(self):
        if self.ser is None:
            try:
                self.ser = serial.Serial(
                    port=self.port.get(),
                    baudrate=int(self.baudrate.get()),
                    bytesize=int(self.data_bits.get()),
                    parity=self.parity.get()[0],  # 'N', 'E', 'O', 'M', 'S'
                    stopbits=float(self.stop_bits.get()),
                    xonxoff=(self.flow_control.get() == "XON/XOFF"),
                    rtscts=(self.flow_control.get() == "RTS/CTS")
                )
                self.connect_button.config(text="Desconectar")
                self.status_label.config(text="Conectado", foreground="green")
                self.root.after(100, self.read_data)
            except Exception as e:
                messagebox.showerror("Erro de Conexão", str(e))
        else:
            self.ser.close()
            self.ser = None
            self.connect_button.config(text="Conectar")
            self.status_label.config(text="Desconectado", foreground="red")

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
                encoded_data = data.encode('utf-8')
                self.ser.write(encoded_data)
            elif self.data_format.get() == "Hexadecimal":
                try:
                    encoded_data = bytes.fromhex(data)
                    self.ser.write(encoded_data)
                except ValueError:
                    messagebox.showerror("Erro de Formato", "Formato hexadecimal inválido.")
                    return

            # Exibir dados enviados na área de recebimento
            self.receive_text.config(state='normal')
            self.receive_text.insert(tk.END, f"Enviado: {data}\n")
            self.receive_text.config(state='disabled')
            self.send_entry.delete(0, tk.END)

    def clear_received_data(self):
        self.receive_text.config(state='normal')
        self.receive_text.delete(1.0, tk.END)
        self.receive_text.config(state='disabled')

    def save_settings(self):
        settings = {
            "port": self.port.get(),
            "baudrate": self.baudrate.get(),
            "data_format": self.data_format.get(),
            "data_bits": self.data_bits.get(),
            "parity": self.parity.get(),
            "stop_bits": self.stop_bits.get(),
            "flow_control": self.flow_control.get()
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        messagebox.showinfo("Configurações", "Configurações salvas com sucesso.")

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.port.set(settings.get("port", ""))
                self.baudrate.set(settings.get("baudrate", "9600"))
                self.data_format.set(settings.get("data_format", "ASCII"))
                self.data_bits.set(settings.get("data_bits", "8"))
                self.parity.set(settings.get("parity", "None"))
                self.stop_bits.set(settings.get("stop_bits", "1"))
                self.flow_control.set(settings.get("flow_control", "None"))

if __name__ == "__main__":
    root = tk.Tk()
    app = SeriaLuz(root)
    root.mainloop()
