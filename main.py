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

class SeriaLuz:
    def __init__(self, root, lang="pt-br"):
        self.root = root
        self.translations = {}
        self.load_language(lang)
        self.root.title(self.translate('title'))
        self.root.iconbitmap("img/icons/logo.ico")
        self.root.iconphoto(False, tk.PhotoImage(file='img/logo.png'))

        # Centralizar a janela
        window_width = 600
        window_height = 600
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
        tab3 = ttk.Frame(notebook)
        notebook.add(tab1, text=self.translate('settings'))
        notebook.add(tab2, text=self.translate('send_receive'))
        notebook.add(tab3, text=self.translate('advanced_settings'))

        self.create_config_tab(tab1)
        self.create_send_receive_tab(tab2)
        self.create_advanced_settings_tab(tab3)

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

        # Botões de conectar e salvar configurações
        self.connect_button = ttk.Button(config_frame, text=self.translate("connect"), command=self.toggle_connection)
        self.connect_button.grid(column=0, row=3, pady=10, padx=5, sticky=tk.W)

        save_button = ttk.Button(config_frame, text=self.translate("save_settings"), command=self.save_settings)
        save_button.grid(column=1, row=3, pady=10, padx=5, sticky=tk.W)

        # Indicador de status de conexão
        self.status_label = ttk.Label(config_frame, text=self.translate("disconnected"), foreground="red")
        self.status_label.grid(column=2, row=3, padx=5)

    def create_send_receive_tab(self, tab):
        # Frame de envio
        send_frame = ttk.LabelFrame(tab, text=self.translate("send_data"))
        send_frame.pack(padx=10, pady=10, fill="x", expand=True)

        self.send_entry = ttk.Entry(send_frame, width=50)
        self.send_entry.grid(column=0, row=0, padx=5, pady=5)
        send_button = ttk.Button(send_frame, text=self.translate("send"), command=self.send_data)
        send_button.grid(column=1, row=0, padx=5, pady=5)

        # Frame de recebimento
        receive_frame = ttk.LabelFrame(tab, text=self.translate("receive_data"))
        receive_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.receive_text = scrolledtext.ScrolledText(receive_frame, width=60, height=10, state='disabled')
        self.receive_text.pack(padx=5, pady=5, fill="both", expand=True)

        clear_button = ttk.Button(receive_frame, text=self.translate("clear"), command=self.clear_received_data)
        clear_button.pack(padx=5, pady=5)

        # Frame do gráfico
        graph_frame = ttk.LabelFrame(tab, text=self.translate("real_time_graph"))
        graph_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'r-')
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.ani = FuncAnimation(self.fig, self.update_graph, init_func=self.init_graph, blit=True, cache_frame_data=False)

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

    def create_info_icon(self, parent, tooltip_text):
        icon = PhotoImage(file="img/icons/info_icon.png")
        info_button = ttk.Label(parent, image=icon)
        info_button.image = icon
        info_button.bind("<Enter>", lambda e: self.show_tooltip(info_button, tooltip_text))
        info_button.bind("<Leave>", lambda e: self.hide_tooltip())
        return info_button

    def show_tooltip(self, widget, text):
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + 20
        self.tooltip = Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = Label(self.tooltip, text=text, background="YELLOW", relief='solid', borderwidth=1, justify='left')
        label.pack(ipadx=1)

    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = None

    def update_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_menu['values'] = [port.device for port in ports]
        if ports:
            self.port.set(ports[0].device)

    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None
            self.status_label.config(text=self.translate("disconnected"), foreground="red")
            self.connect_button.config(text=self.translate("connect"))
        else:
            try:
                self.ser = serial.Serial(
                    port=self.port.get(),
                    baudrate=int(self.baudrate.get()),
                    bytesize=int(self.data_bits.get()),
                    parity=self.parity.get()[0],
                    stopbits=float(self.stop_bits.get()),
                    xonxoff=self.flow_control.get() == "XON/XOFF",
                    rtscts=self.flow_control.get() == "RTS/CTS"
                )
                self.status_label.config(text=self.translate("connected"), foreground="green")
                self.connect_button.config(text=self.translate("disconnected"))
            except Exception as e:
                messagebox.showerror(self.translate("connection_error"), f"{self.translate('unable_to_connect')} {self.port.get()}:\n{str(e)}")

    def send_data(self):
        if self.ser and self.ser.is_open:
            data = self.send_entry.get()
            if self.data_format.get() == "ASCII":
                self.ser.write(data.encode('ascii'))
            elif self.data_format.get() == "Hexadecimal":
                try:
                    hex_data = bytes.fromhex(data)
                    self.ser.write(hex_data)
                except ValueError:
                    messagebox.showerror(self.translate("send_error"), self.translate("format_hex_error"))
            self.send_entry.delete(0, tk.END)
        else:
            messagebox.showwarning(self.translate("no_connection"), self.translate("connect_port_first"))

    def clear_received_data(self):
        self.receive_text.configure(state='normal')
        self.receive_text.delete('1.0', tk.END)
        self.receive_text.configure(state='disabled')

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as file:
                settings = json.load(file)
                self.port.set(settings.get("port", ""))
                self.baudrate.set(settings.get("baudrate", "9600"))
                self.data_format.set(settings.get("data_format", "ASCII"))
                self.data_bits.set(settings.get("data_bits", "8"))
                self.parity.set(settings.get("parity", "None"))
                self.stop_bits.set(settings.get("stop_bits", "1"))
                self.flow_control.set(settings.get("flow_control", "None"))

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
        with open("settings.json", "w") as file:
            json.dump(settings, file)
        messagebox.showinfo(self.translate("save_config"), self.translate("settings_saved"))

    def init_graph(self):
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 1024)
        self.line.set_data([], [])
        return self.line,

    def update_graph(self, frame):
        if self.ser and self.ser.is_open:
            line = self.ser.readline().decode('ascii').strip()
            if line.isdigit():
                self.data_y.append(int(line))
                self.data_x.append(len(self.data_y))
                if len(self.data_x) > 100:
                    self.data_x.pop(0)
                    self.data_y.pop(0)
                self.line.set_data(self.data_x, self.data_y)
                self.ax.set_xlim(min(self.data_x), max(self.data_x) + 1)
        return self.line,

    def load_language(self, lang):
        if os.path.exists(f"locales/{lang}.json"):
            with open(f"locales/{lang}.json", "r") as file:
                self.translations = json.load(file)

    def translate(self, text):
        return self.translations.get(text, text)

def show_language_selection():
    root = tk.Tk()
    root.iconbitmap("img/icons/logo.ico")
    root.title("Seleção de Idioma")

    # Centralizar a janela
    window_width = 300
    window_height = 150
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height/2 - window_height/2)
    position_right = int(screen_width/2 - window_width/2)
    root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    lang = tk.StringVar(value="pt-br")

    ttk.Label(root, text="Selecione o Idioma:").pack(pady=10)

    # Carregar imagens das bandeiras
    flag_en = PhotoImage(file='img/icons/english.png')
    flag_es = PhotoImage(file='img/icons/spanish.png')
    flag_pt = PhotoImage(file='img/icons/brasil.png')
    
    ttk.Radiobutton(root, text="Português", image=flag_pt, compound=tk.LEFT, variable=lang, value="pt-br").pack(anchor=tk.W)
    ttk.Radiobutton(root, text="Inglês", image=flag_en, compound=tk.LEFT, variable=lang, value="en").pack(anchor=tk.W)
    ttk.Radiobutton(root, text="Espanhol", image=flag_es, compound=tk.LEFT, variable=lang, value="es").pack(anchor=tk.W)
    
    def start_app():
        selected_lang = lang.get()
        root.destroy()
        main_app(selected_lang)

    ttk.Button(root, text="Iniciar", command=start_app).pack(pady=10)
    root.mainloop()

def main_app(lang):
    root = tk.Tk()
    app = SeriaLuz(root, lang)
    root.protocol("WM_DELETE_WINDOW", root.quit)  # Ensure the serial port is closed on exit
    root.mainloop()

if __name__ == "__main__":
    show_language_selection()
