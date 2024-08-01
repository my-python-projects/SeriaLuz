
# SeriaLuz

![Logo](img/logo.png)

**Welcome to SeriaLuz!**

To select your preferred language for reading this README, please choose one of the following options:

- [English](#serialuz)
- [Português](#serialuz-em-portuguese)

## SeriaLuz

**SeriaLuz** is a Python application for serial communication and data monitoring with support for real-time graphs and advanced settings. The application uses Tkinter for the graphical interface and Matplotlib for real-time plotting. Serial communication is managed through the `pyserial` library, and Modbus communication is facilitated by the `pymodbus` library.

### Features

- **Serial Communication**: Connect to devices via serial ports.
- **Modbus RTU**: Support for Modbus RTU communication.
- **Graphical Interface**: User interface with Tkinter for easy configuration and operation.
- **Real-Time Graphs**: Data visualization with real-time updating graphs using Matplotlib.
- **Advanced Settings**: Configuration of parameters such as baudrate, data format, parity, etc.

### Installation

#### Requirements

- Python 3.x
- Python Libraries:
  - `tkinter`
  - `matplotlib`
  - `pyserial`
  - `pymodbus`

#### Installation Steps

1. **Clone the Repository**

    ```bash
    git clone https://github.com/my-python-projects/SeriaLuz.git
    ```

2. **Navigate to the Project Directory**

    ```bash
    cd SeriaLuz
    ```

3. **Create and Activate a Virtual Environment (Optional but Recommended)**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4. **Install the Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

### Usage

1. **Run the Application**

    ```bash
    python main.py
    ```

2. **Configure the Serial Device**

   - Select the serial port, baudrate, and other parameters in the **Settings** tab.
   - Click "Connect" to establish communication.

3. **Send and Receive Data**

   - Use the **Send and Receive** tab to send commands and receive data from the connected device.
   - The graph in the send and receive tab will update in real-time with the received data.

### Additional Features

- **Save and Load Settings**: Settings can be saved and loaded from a JSON file for easy reconfiguration.
- **Information Interface**: Contextual tips are provided through info icons to assist with parameter configuration.

### Contributing

If you wish to contribute to the project, please follow these steps:

1. **Fork the Repository**
2. **Create a Branch for Your Feature**

    ```bash
    git checkout -b my-new-feature
    ```

3. **Commit Your Changes**

    ```bash
    git commit -am 'Add new feature'
    ```

4. **Push to the Remote Repository**

    ```bash
    git push origin my-new-feature
    ```

5. **Open a Pull Request**

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

### Contact

For any questions or suggestions, please contact [jeffersongomes81@gmail.com](mailto:jeffersongomes81@gmail.com).

---

## SeriaLuz em Português

![Logo](img/logo.png)

**SeriaLuz** é uma aplicação Python para comunicação serial e monitoramento de dados com suporte a gráficos e configurações avançadas. O aplicativo utiliza a biblioteca Tkinter para a interface gráfica e Matplotlib para gráficos em tempo real. A comunicação serial é gerenciada através da biblioteca `pyserial`, e a comunicação Modbus é facilitada pela biblioteca `pymodbus`.

### Recursos

- **Comunicação Serial**: Conexão com dispositivos através de portas seriais.
- **Modbus RTU**: Suporte a comunicação Modbus RTU.
- **Interface Gráfica**: Interface de usuário com Tkinter para fácil configuração e operação.
- **Gráficos em Tempo Real**: Visualização de dados com gráficos atualizados em tempo real usando Matplotlib.
- **Configurações Avançadas**: Configuração de parâmetros como baudrate, formato de dados, paridade, etc.

### Instalação

#### Requisitos

- Python 3.x
- Bibliotecas Python:
  - `tkinter`
  - `matplotlib`
  - `pyserial`
  - `pymodbus`

#### Passos para Instalação

1. **Clone o Repositório**

    ```bash
    git clone https://github.com/my-python-projects/SeriaLuz.git
    ```

2. **Navegue até o Diretório do Projeto**

    ```bash
    cd SeriaLuz
    ```

3. **Crie e Ative um Ambiente Virtual (Opcional, mas recomendado)**

    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    ```

4. **Instale as Dependências**

    ```bash
    pip install -r requirements.txt
    ```

### Uso

1. **Executar a Aplicação**

    ```bash
    python main.py
    ```

2. **Configurar o Dispositivo Serial**

   - Selecione a porta serial, baudrate e outros parâmetros na aba de **Configurações**.
   - Clique em "Conectar" para estabelecer a comunicação.

3. **Enviar e Receber Dados**

   - Use a aba **Envio e Recebimento** para enviar comandos e receber dados do dispositivo conectado.
   - O gráfico na aba de envio e recebimento será atualizado em tempo real com os dados recebidos.

### Funcionalidades Adicionais

- **Salvar e Carregar Configurações**: Configurações podem ser salvas e carregadas a partir de um arquivo JSON para facilitar a reconfiguração.
- **Interface de Informação**: Ícones de informação com dicas contextuais são fornecidos para ajudar na configuração dos parâmetros.

### Contribuição

Se você deseja contribuir para o projeto, siga os seguintes passos:

1. **Faça um Fork do Repositório**
2. **Crie uma Branch para sua Feature**

    ```bash
    git checkout -b minha-nova-feature
    ```

3. **Faça Commit das Suas Mudanças**

    ```bash
    git commit -am 'Adiciona nova feature'
    ```

4. **Envie para o Repositório Remoto**

    ```bash
    git push origin minha-nova-feature
    ```

5. **Abra um Pull Request**

### Licença

Este projeto é licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

### Contato

Para qualquer dúvida ou sugestão, entre em contato com [jeffersongomes81@gmail.com](mailto:jeffersongomes81@gmail.com).
