import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import PhotoImage, Toplevel, Label
import serial
import serial.tools.list_ports
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import sys
from pymodbus.client import ModbusSerialClient as ModbusClient
import logging
from contator import Contator


# Configuração básica de logging
logging.basicConfig(filename='serialuz.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SeriaLuz:
    def __init__(self, root, lang="pt-br"):
        self.root = root
        self.translations = {}
        self.load_language(lang)
        self.root.title(self.translate('title'))
        self.root.iconbitmap("img/icons/logo.ico")
        self.root.iconphoto(False, tk.PhotoImage(file='img/logo.png'))

        self.lang = lang
        

        # Centralizar a janela
        window_width = 600
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        self.port = tk.StringVar()
        self.baudrate = tk.StringVar(value="9600")
        self.data_format = tk.StringVar(value="ASCII")
        self.protocol = tk.StringVar(value="")
        self.data_bits = tk.StringVar(value="8")
        self.parity = tk.StringVar(value="None")
        self.stop_bits = tk.StringVar(value="1")
        self.flow_control = tk.StringVar(value="None")

        # Configurar elementos da interface
        self.create_widgets()

        # Variáveis de estado
        self.ser = None
        self.modbus_client = None
        self.modbus_connected = False

        # Dados para o gráfico
        self.data_x = []
        self.data_y = []

        # Carregar configurações salvas
        self.load_settings()

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=1, fill="both")

        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)

        notebook.add(tab1, text=self.translate('settings'))
        notebook.add(tab2, text=self.translate('send_receive'))

        self.create_config_tab(tab1)
        self.create_send_receive_tab(tab2)

    def teste(self, tab):
        self.create_advanced_settings_tab(tab)
        self.create_config(tab)


    def create_config_tab(self, tab):

        config_frame = ttk.LabelFrame(tab, text=self.translate("settings"))
        config_frame.pack(padx=10, pady=10, fill="x", expand=True)

        # Porta serial
        ttk.Label(config_frame, text=self.translate("port")).grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        self.port_menu = ttk.Combobox(config_frame, textvariable=self.port)
        self.port_menu.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W)
        self.update_ports()

        # Botão para atualizar portas seriais
        update_ports_button = ttk.Button(config_frame, text=self.translate("update_ports"), command=self.update_ports)
        update_ports_button.grid(column=2, row=0, padx=5, pady=5)

        # Baudrate
        ttk.Label(config_frame, text=self.translate("baudrate")).grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
        baudrate_entry = ttk.Entry(config_frame, textvariable=self.baudrate)
        baudrate_entry.grid(column=1, row=1, padx=5, pady=5, sticky=tk.W)

        # Formato dos dados
        ttk.Label(config_frame, text=self.translate("data_format")).grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
        format_menu = ttk.Combobox(config_frame, textvariable=self.data_format, values=["ASCII", "Hexadecimal"])
        format_menu.grid(column=1, row=2, padx=5, pady=5, sticky=tk.W)

        # Protocolo
        ttk.Label(config_frame, text=self.translate("protocol")).grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)
        protocol_menu = ttk.Combobox(config_frame, textvariable=self.protocol, values=["Modbus", "Profibus", "Profinet", "EtherCAT", "CAN", "DeviceNet", "BACnet", "EtherNet/IP", "DNP3", "HART"])
        protocol_menu.grid(column=1, row=3, padx=5, pady=5, sticky=tk.W)

        # Data Bits
        ttk.Label(config_frame, text=self.translate("data_bits")).grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)
        data_bits_menu = ttk.Combobox(config_frame, textvariable=self.data_bits, values=["5", "6", "7", "8"])
        data_bits_menu.grid(column=1, row=4, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(config_frame, self.translate("data_bits_info")).grid(column=2, row=4, padx=5, pady=5)

        # Parity
        ttk.Label(config_frame, text=self.translate("parity")).grid(column=0, row=5, sticky=tk.W, padx=5, pady=5)
        parity_menu = ttk.Combobox(config_frame, textvariable=self.parity, values=["None", "Even", "Odd", "Mark", "Space"])
        parity_menu.grid(column=1, row=5, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(config_frame, self.translate("parity_info")).grid(column=2, row=5, padx=5, pady=5)

        # Stop Bits
        ttk.Label(config_frame, text=self.translate("stop_bits")).grid(column=0, row=6, sticky=tk.W, padx=5, pady=5)
        stop_bits_menu = ttk.Combobox(config_frame, textvariable=self.stop_bits, values=["1", "1.5", "2"])
        stop_bits_menu.grid(column=1, row=6, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(config_frame, self.translate("stop_bits_info")).grid(column=2, row=6, padx=5, pady=5)

        # Flow Control
        ttk.Label(config_frame, text=self.translate("flow_control")).grid(column=0, row=7, sticky=tk.W, padx=5, pady=5)
        flow_control_menu = ttk.Combobox(config_frame, textvariable=self.flow_control, values=["None", "RTS/CTS", "XON/XOFF"])
        flow_control_menu.grid(column=1, row=7, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(config_frame, self.translate("flow_control_info")).grid(column=2, row=7, padx=5, pady=5)

        # Botões de conectar e salvar configurações
        self.connect_button = ttk.Button(config_frame, text=self.translate("connect"), command=self.toggle_connection)
        self.connect_button.grid(column=0, row=8, pady=10, padx=5, sticky=tk.W)

        save_button = ttk.Button(config_frame, text=self.translate("save_settings"), command=self.save_settings)
        save_button.grid(column=1, row=8, pady=10, padx=5, sticky=tk.W)

        # Indicador de status de conexão
        self.status_label = ttk.Label(config_frame, text=self.translate("disconnected"), foreground="red")
        self.status_label.grid(column=2, row=8, padx=5)


    def create_advanced_settings_tab(self, tab):
        advanced_frame = ttk.LabelFrame(tab, text=self.translate("advanced_settings"))
        advanced_frame.pack(padx=10, pady=10, fill="x", expand=True)

        # Data Bits
        ttk.Label(advanced_frame, text=self.translate("data_bits")).grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        data_bits_menu = ttk.Combobox(advanced_frame, textvariable=self.data_bits, values=["5", "6", "7", "8"])
        data_bits_menu.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(advanced_frame, self.translate("data_bits_info")).grid(column=2, row=0, padx=5, pady=5)

        # Parity
        ttk.Label(advanced_frame, text=self.translate("parity")).grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
        parity_menu = ttk.Combobox(advanced_frame, textvariable=self.parity, values=["None", "Even", "Odd", "Mark", "Space"])
        parity_menu.grid(column=1, row=1, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(advanced_frame, self.translate("parity_info")).grid(column=2, row=1, padx=5, pady=5)

        # Stop Bits
        ttk.Label(advanced_frame, text=self.translate("stop_bits")).grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
        stop_bits_menu = ttk.Combobox(advanced_frame, textvariable=self.stop_bits, values=["1", "1.5", "2"])
        stop_bits_menu.grid(column=1, row=2, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(advanced_frame, self.translate("stop_bits_info")).grid(column=2, row=2, padx=5, pady=5)

        # Flow Control
        ttk.Label(advanced_frame, text=self.translate("flow_control")).grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)
        flow_control_menu = ttk.Combobox(advanced_frame, textvariable=self.flow_control, values=["None", "RTS/CTS", "XON/XOFF"])
        flow_control_menu.grid(column=1, row=3, padx=5, pady=5, sticky=tk.W)
        self.create_info_icon(advanced_frame, self.translate("flow_control_info")).grid(column=2, row=3, padx=5, pady=5)


    def create_config(self, tab):
        config_frame = ttk.LabelFrame(tab, text=self.translate("settings"))
        config_frame.pack(padx=10, pady=10, fill="x", expand=True)

        # Porta serial
        ttk.Label(config_frame, text=self.translate("port")).grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        self.port_menu = ttk.Combobox(config_frame, textvariable=self.port)
        self.port_menu.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W)
        self.update_ports()

        # Botão para atualizar portas seriais
        update_ports_button = ttk.Button(config_frame, text=self.translate("update_ports"), command=self.update_ports)
        update_ports_button.grid(column=2, row=0, padx=5, pady=5)

        # Baudrate
        ttk.Label(config_frame, text=self.translate("baudrate")).grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
        baudrate_entry = ttk.Entry(config_frame, textvariable=self.baudrate)
        baudrate_entry.grid(column=1, row=1, padx=5, pady=5, sticky=tk.W)

        # Formato dos dados
        ttk.Label(config_frame, text=self.translate("data_format")).grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
        format_menu = ttk.Combobox(config_frame, textvariable=self.data_format, values=["ASCII", "Hexadecimal"])
        format_menu.grid(column=1, row=2, padx=5, pady=5, sticky=tk.W)

        # Botões de conectar e salvar configurações
        self.connect_button = ttk.Button(config_frame, text=self.translate("connect"), command=self.toggle_connection)
        self.connect_button.grid(column=0, row=3, pady=10, padx=5, sticky=tk.W)

        save_button = ttk.Button(config_frame, text=self.translate("save_settings"), command=self.save_settings)
        save_button.grid(column=1, row=3, pady=10, padx=5, sticky=tk.W)

        # Indicador de status de conexão
        self.status_label = ttk.Label(config_frame, text=self.translate("disconnected"), foreground="red")
        self.status_label.grid(column=2, row=3, padx=5)



    def create_send_receive_tab(self, tab):
        # Frame de envio com cor de fundo
        send_frame = ttk.LabelFrame(tab, text=self.translate("send_data"))
        send_frame.pack(padx=10, pady=10, fill="x", expand=True)
        send_frame.configure(style="Custom.TLabelframe")

        self.send_entry = ttk.Entry(send_frame, width=50)
        self.send_entry.grid(column=0, row=0, padx=5, pady=5)
        send_button = ttk.Button(send_frame, text=self.translate("send"), command=self.send_data)
        send_button.grid(column=1, row=0, padx=5, pady=5)

        # Frame de recebimento com cor de fundo
        receive_frame = ttk.LabelFrame(tab, text=self.translate("receive_data"))
        receive_frame.pack(padx=10, pady=10, fill="both", expand=True)
        receive_frame.configure(style="Custom.TLabelframe")

        self.receive_text = scrolledtext.ScrolledText(receive_frame, width=60, height=10, state='disabled')
        self.receive_text.pack(padx=5, pady=5, fill="both", expand=True)

        # Alinhar botões na parte inferior do frame de recebimento
        button_frame = ttk.Frame(receive_frame)
        button_frame.pack(padx=5, pady=5, fill="x", expand=True)

        clear_button = ttk.Button(button_frame, text=self.translate("clear"), command=self.clear_received_data)
        clear_button.pack(side=tk.LEFT, padx=5, pady=5)

        modbus_button = ttk.Button(button_frame, text="Contator", command=self.show_contator)
        modbus_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Frame do gráfico com cor de fundo
        graph_frame = ttk.LabelFrame(tab, text=self.translate("real_time_graph"))
        graph_frame.pack(padx=10, pady=10, fill="both", expand=True)
        graph_frame.configure(style="Custom.TLabelframe")

        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'r-')
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.ani = FuncAnimation(self.fig, self.update_graph, init_func=self.init_graph, blit=True, cache_frame_data=False)


    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        try:
            self.ser = serial.Serial(
                port=self.port.get(),
                baudrate=self.baudrate.get(),
                bytesize=int(self.data_bits.get()),
                parity=self.parity.get()[0],
                stopbits=float(self.stop_bits.get()),
                xonxoff=(self.flow_control.get() == "XON/XOFF"),
                rtscts=(self.flow_control.get() == "RTS/CTS"),
                timeout=1
            )
            self.status_label.config(text=self.translate("connected"), foreground="green")
            self.connect_button.config(text=self.translate("disconnect"))

            if self.protocol.get() == "Modbus":
                self.modbus_client = ModbusClient(method='rtu', port=self.ser.port, baudrate=self.ser.baudrate)
                self.modbus_connected = self.modbus_client.connect()

        except serial.SerialException as e:
            messagebox.showerror(self.translate("error"), str(e))

    def disconnect(self):
        if self.ser:
            self.ser.close()
            self.ser = None
        if self.modbus_client:
            self.modbus_client.close()
            self.modbus_connected = False

        self.status_label.config(text=self.translate("disconnected"), foreground="red")
        self.connect_button.config(text=self.translate("connect"))

    def connect_modbus(self):
        try:
            self.modbus_client = ModbusClient(
                method='rtu',
                port=self.port.get(),
                baudrate=int(self.baudrate.get()),
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                timeout=1
            )
            connection = self.modbus_client.connect()
            if connection:
                self.modbus_connected = True
                self.log("Conexão Modbus estabelecida.")
            else:
                self.log("Erro ao conectar ao Modbus.")
            return connection
        except Exception as e:
            self.log(f"Erro ao conectar à porta serial: {e}")
            return False

    def disconnect_modbus(self):
        if self.modbus_client:
            self.modbus_client.close()
            self.modbus_connected = False
            self.log("Conexão Modbus encerrada.")

    def send_data(self):
        if self.ser and self.ser.is_open:
            data = self.send_entry.get()
            if self.data_format.get() == "Hexadecimal":
                data = bytes.fromhex(data)
            else:
                data = data.encode('utf-8')
            self.ser.write(data)
        else:
            messagebox.showerror(self.translate("error"), self.translate("not_connected"))

    def receive_data(self):
        if self.ser and self.ser.is_open:
            data = self.ser.read_all()
            if data:
                if self.data_format.get() == "Hexadecimal":
                    data = data.hex()
                self.receive_text.config(state='normal')
                self.receive_text.insert(tk.END, data + '\n')
                self.receive_text.config(state='disabled')
                self.receive_text.yview(tk.END)

    def update_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_menu['values'] = ports

    def clear_received_data(self):
        self.receive_text.config(state='normal')
        self.receive_text.delete('1.0', tk.END)
        self.receive_text.config(state='disabled')

    def init_graph(self):
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(-10, 10)
        self.line.set_data([], [])
        return self.line,

    def update_graph(self, frame):
        if self.ser and self.ser.is_open:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    try:
                        value = float(line)
                        self.data_x.append(len(self.data_x))
                        self.data_y.append(value)
                        if len(self.data_x) > 100:
                            self.data_x.pop(0)
                            self.data_y.pop(0)
                        self.line.set_data(self.data_x, self.data_y)
                        self.ax.relim()
                        self.ax.autoscale_view()
                    except ValueError:
                        pass
            except Exception as e:
                logging.error(f"Error reading from serial port: {e}")
        return self.line,

    def create_info_icon(self, parent, text):
        info_icon = PhotoImage(file="img/icons/info_icon.png")
        info_label = Label(parent, image=info_icon)
        info_label.image = info_icon
        info_label.bind("<Enter>", lambda e: self.show_tooltip(info_label, text))
        info_label.bind("<Leave>", lambda e: self.hide_info_tooltip())
        return info_label
    

    def show_tooltip(self, widget, message):
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{widget.winfo_rootx() + 20}+{widget.winfo_rooty() + 20}")
        label = ttk.Label(self.tooltip, text=message, padding=5, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()


    def hide_info_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = None

    def translate(self, text):
        return self.translations.get(text, text)

    def load_language(self, lang):
        try:
            with open(f'lang/{lang}.json', 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            logging.error(f"Language file for '{lang}' not found. Falling back to default.")
            self.translations = {}


    def save_settings(self):
        settings = {
            'port': self.port.get(),
            'baudrate': self.baudrate.get(),
            'data_format': self.data_format.get(),
            'data_bits': self.data_bits.get(),
            'parity': self.parity.get(),
            'stop_bits': self.stop_bits.get(),
            'flow_control': self.flow_control.get(),
            "protocol": self.protocol.get()
        }
        try:
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            messagebox.showinfo(self.translate('settings_saved'), self.translate('settings_saved_message'))
        except IOError as e:
            logging.error(f"Error saving settings: {e}")
            messagebox.showerror(self.translate('error'), self.translate('settings_save_error'))


    def load_settings(self):
        if os.path.exists('settings.json'):
            try:
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.port.set(settings.get('port', ''))
                self.baudrate.set(settings.get('baudrate', '9600'))
                self.data_format.set(settings.get('data_format', 'ASCII'))
                self.data_bits.set(settings.get('data_bits', '8'))
                self.parity.set(settings.get('parity', 'None'))
                self.stop_bits.set(settings.get('stop_bits', '1'))
                self.flow_control.set(settings.get('flow_control', 'None'))
                self.protocol.set(settings.get("protocol", ""))
            except IOError as e:
                logging.error(f"Error loading settings: {e}")

    def read_modbus_data(self):
        if not self.modbus_connected:
            self.log("Cliente Modbus não está conectado.")
            return

        try:
            rr = self.modbus_client.read_holding_registers(address=0, count=10, unit=1)
            if not rr.isError():
                self.log(f"Dados lidos: {rr.registers}")
                self.display_received_data(f"Dados Modbus: {rr.registers}")
            else:
                self.log(f"Erro ao ler dados Modbus: {rr}")
        except Exception as e:
            self.log(f"Erro ao ler dados Modbus: {e}")


    def show_contator(self):
            root = tk.Tk()
            app = Contator(root, self.lang)
            root.mainloop()

    def log(self, message):
        self.receive_text.config(state='normal')
        self.receive_text.insert(tk.END, message + '\n')
        self.receive_text.config(state='disabled')
        self.receive_text.yview(tk.END)

    def display_received_data(self, data):
        self.receive_text.config(state='normal')
        self.receive_text.insert(tk.END, data + '\n')
        self.receive_text.config(state='disabled')
        self.receive_text.yview(tk.END)


def show_language_selection():
    selection_window = tk.Tk()
    selection_window.title("Select Language")
    selection_window.geometry("300x150")

    # Centralizar a janela
    window_width = 300
    window_height = 150
    screen_width = selection_window.winfo_screenwidth()
    screen_height = selection_window.winfo_screenheight()
    position_top = int(screen_height/2 - window_height/2)
    position_right = int(screen_width/2 - window_width/2)
    selection_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    lang = tk.StringVar(value="en")

    ttk.Label(selection_window, text="Select Language:").pack(pady=10)

    pt_image = PhotoImage(file="img/icons/flags/pt-br.png")
    en_image = PhotoImage(file="img/icons/flags/en.png")
    es_image = PhotoImage(file="img/icons/flags/es.png")
    
    ttk.Radiobutton(selection_window, text="English",   image=en_image, compound=tk.LEFT,   variable=lang, value="en").pack(anchor=tk.W)
    ttk.Radiobutton(selection_window, text="Spanish",   image=es_image, compound=tk.LEFT,   variable=lang, value="es").pack(anchor=tk.W)
    ttk.Radiobutton(selection_window, text="Portuguese",image=pt_image, compound=tk.LEFT,   variable=lang, value="pt-br").pack(anchor=tk.W)

    def start_app():
        selected_lang = lang.get()
        settings = {"language": selected_lang}
        with open("lang.json", "w") as file:
            json.dump(settings, file)
        selection_window.destroy()
        root = tk.Tk()
        app = SeriaLuz(root, lang=selected_lang)
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

    ttk.Button(selection_window, text="START", command=start_app).pack(pady=10)
    selection_window.mainloop()

def on_closing():
    logging.info("Application closing...")
    sys.exit()

def main_app():
    if os.path.isfile("lang.json"):
        with open("lang.json", "r") as file:
            settings = json.load(file)
            lang = settings.get("language", "")
            if lang:
                root = tk.Tk()
                app = SeriaLuz(root, lang=lang)
                root.protocol("WM_DELETE_WINDOW", on_closing)
                root.mainloop()
            else:
                show_language_selection()
    else:
        show_language_selection()

if __name__ == "__main__":
    main_app()
