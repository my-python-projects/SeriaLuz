import tkinter as tk
from tkinter import messagebox
import threading
import time
from pymodbus.client import ModbusSerialClient as ModbusClient
import os
import json

class Contator:
    def __init__(self, master, lang):

        self.translations = {}
        self.load_language(lang)

        self.master = master
        self.master.title(self.translate("contact_simulate"))
        self.master.geometry("800x600")
        self.master.config(bg="#2e2e2e")

        self.counter = 0
        self.running = False
        self.serial_connected = False

        self.serial_port = tk.StringVar()
        self.baud_rate = tk.StringVar(value="9600")
        self.unit_id = 1  # ID do dispositivo Modbus
        self.register_address = 0  # Endereço do registro a ser lido

        self.load_settings()

        self.label = tk.Label(master, text=self.translate("score"), font=("Helvetica", 24), fg="#ffffff", bg="#2e2e2e")
        self.label.pack(pady=(20, 10))

        self.display = tk.Label(master, text=str(self.counter), font=("Helvetica", 48), fg="#00ff00", bg="#000000", width=6)
        self.display.pack(pady=(0, 20))

        button_frame = tk.Frame(master, bg="#2e2e2e")
        button_frame.pack()

        self.start_button = tk.Button(button_frame, text=self.translate("start"), command=self.start_counter, font=("Helvetica", 14), bg="#4caf50", fg="#ffffff", activebackground="#388e3c", activeforeground="#ffffff")
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = tk.Button(button_frame, text=self.translate("stop"), command=self.stop_counter, font=("Helvetica", 14), bg="#f44336", fg="#ffffff", activebackground="#d32f2f", activeforeground="#ffffff")
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        self.reset_button = tk.Button(button_frame, text=self.translate("reset"), command=self.reset_counter, font=("Helvetica", 14), bg="#2196f3", fg="#ffffff", activebackground="#1976d2", activeforeground="#ffffff")
        self.reset_button.grid(row=0, column=2, padx=5, pady=5)

        self.reconnect_button = tk.Button(button_frame, text=self.translate("reconnect"), command=self.reconnect, font=("Helvetica", 14), bg="#ff9800", fg="#ffffff", activebackground="#f57c00", activeforeground="#ffffff")
        self.reconnect_button.grid(row=0, column=3, padx=5, pady=5)

        self.exit_button = tk.Button(button_frame, text=self.translate("exit"), command=master.quit, font=("Helvetica", 14), bg="#9e9e9e", fg="#ffffff", activebackground="#757575", activeforeground="#ffffff")
        self.exit_button.grid(row=0, column=4, padx=5, pady=5)

        # Canvas para desenhar o diagrama elétrico
        self.canvas = tk.Canvas(master, width=600, height=400, bg="#ffffff")
        self.canvas.pack(pady=(20, 10))

        self.draw_diagram()

        # Área de texto para logs
        self.log_text = tk.Text(master, height=5, bg="#1e1e1e", fg="#00ff00", font=("Helvetica", 12), state=tk.DISABLED)
        self.log_text.pack(pady=(10, 0), fill=tk.X, padx=20)

    def draw_diagram(self):
        # Exemplo simples de diagrama elétrico
        self.canvas.create_rectangle(50, 50, 150, 150, outline="#000000", fill="#cccccc", width=2)
        self.canvas.create_text(100, 200, text=self.translate("resistor"), font=("Helvetica", 14))
        self.canvas.create_line(100, 150, 100, 250, fill="#000000", width=2)
        self.canvas.create_line(50, 250, 150, 250, fill="#000000", width=2)
        self.canvas.create_text(100, 270, text=self.translate("connections"), font=("Helvetica", 14))
        self.update_diagram()

    def update_diagram(self):
        # Atualizar o diagrama ao vivo
        self.canvas.delete("live")
        self.canvas.create_text(300, 100, text=f"{self.translate("score")} {self.counter}", font=("Helvetica", 24), tags="live")

    def start_counter(self):
        if not self.running:
            self.running = True
            self.serial_connected = self.connect_modbus()
            if self.serial_connected:
                self.counter_thread = threading.Thread(target=self.update_counter_modbus)
                self.counter_thread.start()
            else:
                self.running = False

    def stop_counter(self):
        self.running = False

    def reset_counter(self):
        self.running = False
        self.counter = 0
        self.display.config(text=str(self.counter))
        self.update_diagram()

    def reconnect(self):
        self.stop_counter()
        self.reset_counter()
        self.start_counter()

    def connect_modbus(self):
        try:
            self.client = ModbusClient(method='rtu', port=self.serial_port, baudrate=self.baud_rate, timeout=1)
            connection = self.client.connect()
            if connection:
                self.log(self.translate("connect_modbus"))
            else:
                self.log(self.translate("error_connect_modbus"))
            return connection
        except Exception as e:
            self.log(f"{self.translate("error_connect_port")} {e}")
            return False

    def update_counter_modbus(self):
        while self.running:
            try:
                result = self.client.read_holding_registers(self.register_address, 1, unit=self.unit_id)
                if not result.isError():
                    self.counter = result.registers[0]
                    self.display.config(text=str(self.counter))
                    self.update_diagram()
                else:
                    self.log(self.translate("error_read_read_modbus"))
                self.master.update_idletasks()
                time.sleep(1)  # Ajuste conforme necessário para a taxa de atualização
            except Exception as e:
                self.log(f"{self.translate("error_read_modbus")} {e}")
                self.running = False

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)


    def load_settings(self):
        if os.path.isfile("settings.json"):
            with open("settings.json", "r") as file:
                settings = json.load(file)
                self.serial_port.set(settings.get("port", ""))
                self.baud_rate.set(settings.get("baudrate", "9600"))

    def load_language(self, lang):
        lang_file = f"lang/{lang}.json"
        try:
            with open(lang_file, 'r', encoding='utf-8') as file:
                self.translations = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Language file '{lang_file}' not found.")

    def translate(self, text):
        return self.translations.get(text, text)

def main():
    lang = "pt-br"
    if os.path.isfile("lang.json"):
        with open("lang.json", "r") as file:
            settings = json.load(file)
            lang = settings.get("language", "")

    root = tk.Tk()
    app = Contator(root, lang)
    root.mainloop()

if __name__ == "__main__":
    main()
