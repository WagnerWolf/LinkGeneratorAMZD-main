import sys
import json
import pyshorteners
import pyshorteners.exceptions as excep
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QMessageBox, QHBoxLayout, QComboBox, QProgressBar
)
from PyQt5.QtGui import  QIcon, QIntValidator

import requests

EXTERNALURL = "http://177.130.49.208:9307/"
INSTANCIA = "main"
CONTATO = ('Vitória Assistente Virtual - Laboratório Amazônia','559391010040','+559391010040')
s = pyshorteners.Shortener()

def gerarLink(link):
    link = link.replace("http://192.168.1.225:9007/", EXTERNALURL)
    try:
        return s.dagd.short(link)
    except excep.BadAPIResponseException as e:
        return e
    except excep.ShorteningErrorException as e:
        return e

def envia_msgtxt(numero, nome, link):
    url = f"http://localhost:8084/message/sendText/{INSTANCIA}"
    payload = json.dumps({
        "number": numero,
        "options": {"delay": 5, "presence": "composing"},
        "textMessage": {"text": f"Olá. Conforme solicitado, segue o link de imagens do paciente '{nome}':\n{link}\nSalve o nosso contato para que o link fique clicável:"}
    })
    headers = {"Content-Type": "application/json", "apikey": "zYzP7ocstxh3Sscefew4FZTCu4ehnM8v4hu"}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

def envia_contato(instancia, numero, nomeContato, wuid, numeroContato ):#, cliente_id):
  url = "http://localhost:8084/message/sendContact/"+instancia
  payload = json.dumps({
  "number": numero,
  "contactMessage": [
    {
      "fullName": nomeContato,
      "wuid": wuid,#formato:"559399999999"
      "phoneNumber": numeroContato#formato:"+55 93 9 99999999"
    }
  ]
})
  headers = {
    'Content-Type': 'application/json',
    'apikey': 'zYzP7ocstxh3Sscefew4FZTCu4ehnM8v4hu'
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  #coloca_no_historico(cliente_id, fromMe=True, url_midia=urlmidia)
  return(response.text)

def envia_resultado(telefone, nome, link):
    resultado_mensagem = envia_msgtxt(telefone, nome, link)
    resultado_contato = envia_contato(INSTANCIA, telefone, CONTATO[0], CONTATO[1], CONTATO[2])
    return resultado_mensagem, resultado_contato


    

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AMZD Link Generator 2.0")
        self.setGeometry(100, 100, 400, 350)
        layout = QVBoxLayout()
        
        self.label_nome = QLabel("Nome do Paciente")
        self.input_nome = QLineEdit()
        
        self.label_telefone = QLabel("Número de Telefone")
        self.select_codigo = QComboBox()
        country_codes = {"Brasil": "55", "EUA": "1", "Reino Unido": "44", "Alemanha": "49", "Índia": "91"}
        for country, code in country_codes.items():
            self.select_codigo.addItem(QIcon(f"flags/{country.lower()}.png"), f"{country} (+{code})", code)
        self.select_codigo.setCurrentIndex(0)
        
        self.input_ddd = QLineEdit()
        self.input_ddd.setPlaceholderText("DDD (ex: 11)")
        self.input_ddd.setMaxLength(2)
        self.input_ddd.setValidator(QIntValidator(10, 99, self))  # Aceita apenas números de 10 a 99

        self.input_numero = QLineEdit()
        self.input_numero.setPlaceholderText("Número (8 dígitos)")
        self.input_numero.setMaxLength(8)
        self.input_numero.setValidator(QIntValidator(10000000, 99999999, self))  # Aceita apenas números de 8 dígitos

        
        telefone_layout = QHBoxLayout()
        telefone_layout.addWidget(self.select_codigo)
        telefone_layout.addWidget(self.input_ddd)
        telefone_layout.addWidget(self.input_numero)
        
        self.label_formato = QLabel("Formato esperado: Código País + DDD + Número (ex: 55 11 98765432)")
        
        self.label_link = QLabel("Link com o IP interno")
        self.input_link = QLineEdit()
        
        self.output_label = QLabel()
        self.output_label.setFixedHeight(60)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.button_ok = QPushButton("Gerar Link")
        self.button_ok.clicked.connect(self.generate_link)
        self.button_ok.setEnabled(False)
        
        self.button_limpar = QPushButton("Limpar")
        self.button_limpar.clicked.connect(self.clear_fields)
        
        self.button_sair = QPushButton("Sair")
        self.button_sair.clicked.connect(self.close)
        
        layout.addWidget(self.label_nome)
        layout.addWidget(self.input_nome)
        layout.addWidget(self.label_telefone)
        layout.addLayout(telefone_layout)
        layout.addWidget(self.label_formato)
        layout.addWidget(self.label_link)
        layout.addWidget(self.input_link)
        layout.addWidget(self.output_label)
        layout.addWidget(self.progress_bar)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button_ok)
        button_layout.addWidget(self.button_limpar)
        button_layout.addWidget(self.button_sair)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.input_nome.textChanged.connect(self.validate_fields)
        self.input_ddd.textChanged.connect(self.validate_fields)
        self.input_numero.textChanged.connect(self.validate_fields)
        self.input_link.textChanged.connect(self.validate_fields)
    
    def validate_fields(self):
        nome_preenchido = bool(self.input_nome.text())
        ddd_preenchido = len(self.input_ddd.text()) == 2
        numero_preenchido = len(self.input_numero.text()) == 8
        link_preenchido = bool(self.input_link.text())
        self.button_ok.setEnabled(nome_preenchido and ddd_preenchido and numero_preenchido and link_preenchido)
    
    def generate_link(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(50)
        
        link_longo = self.input_link.text()
        slink = gerarLink(link_longo)
        
        if slink and not isinstance(slink, Exception):
            self.progress_bar.setValue(100)
            
            codigo = self.select_codigo.currentData()
            ddd = self.input_ddd.text()
            numero = self.input_numero.text()
            telefone_completo = f"{codigo}{ddd}{numero}"
            
            self.confirm_send_message(telefone_completo, self.input_nome.text(), slink)
        else:
            self.output_label.setText("Erro na geração do link: " + str(slink))
            self.progress_bar.setVisible(False)
    
    def confirm_send_message(self, telefone, nome, link):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmação de Envio")
        msg_box.setText(f"Link gerado com sucesso!\n\nNúmero: {telefone}\n\nLink curto: {link}\n\nConfirma envio de mensagem?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        resposta = msg_box.exec_()
        if resposta == QMessageBox.Yes:
            resultado = envia_resultado(telefone, nome, link)
            QMessageBox.information(self, "Envio Concluído", f"Resposta do servidor:\n{resultado}")
        
        self.progress_bar.setVisible(False)
    
    def clear_fields(self):
        self.input_nome.clear()
        self.input_ddd.clear()
        self.input_numero.clear()
        self.input_link.clear()
        self.output_label.clear()
        self.progress_bar.setVisible(False)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icone.ico"))  # Define o ícone da aplicação
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())