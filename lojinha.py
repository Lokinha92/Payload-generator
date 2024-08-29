import tkinter as tk
from tkinter import messagebox
from pix import Payload
from PIL import Image, ImageTk
from requisicaoHTTP import req

# Dicionário de produtos com seus preços
produtos = {
    'Produto 1': 0.01,
    'Produto 2': 20.00,
    'Produto 3': 30.00,
    'Produto 4': 15.00,
    'Produto 5': 25.00,
    'Produto 6': 35.00,
}

# URL base do servidor para verificar o pagamento
URL_BASE = "http://192.168.2.110"  # Substitua pelo IP do seu servidor

# Inicializa as variáveis globais
estado_transacao_capturado = None
total = None  # Inicializa a variável global para o total da transação
mensagem_pagamento_mostrada = False

# Função para adicionar produto ao carrinho
def adicionar_ao_carrinho(produto, preco, quantidade):
    carrinho.append((produto, preco, quantidade))
    atualizar_lista_carrinho()
    atualizar_total()

# Função para atualizar o valor total
def atualizar_total():
    global total
    total = sum(preco * quantidade for produto, preco, quantidade in carrinho)
    total_label.config(text=f"Total: R$ {total:.2f}")

# Função para atualizar a lista de itens no carrinho
def atualizar_lista_carrinho():
    carrinho_texto = "\n".join([f"{quantidade}x {produto}: R$ {preco*quantidade:.2f}" for produto, preco, quantidade in carrinho])
    carrinho_label.config(text=carrinho_texto)

def iniciar_verificacao_pagamento():
    def polling():
        global estado_transacao_capturado, mensagem_pagamento_mostrada
        
        valor_recebido, id_recebido = req(URL_BASE)
        
        if valor_recebido and id_recebido:
            if estado_transacao_capturado:
                estado_valor, estado_id = estado_transacao_capturado
                if valor_recebido != estado_valor or id_recebido != estado_id:
                    if valor_recebido == str(total) and not mensagem_pagamento_mostrada:
                        messagebox.showinfo("Pagamento", "Pagamento confirmado com sucesso!")
                        mensagem_pagamento_mostrada = True
                        reiniciar_loja()
                    else:
                        # Se o valor não corresponder ao total, então é uma transação diferente
                        pass

        # Continua verificando a cada 3 segundos
        root.after(3000, polling)
    
    polling()

def exibir_qr_code():
    global qr_window
    qr_window = tk.Toplevel(root)
    qr_window.title("Pagamento")

    qr_img = Image.open("pixqrcodegen.png")
    qr_img = qr_img.resize((200, 200), Image.ANTIALIAS)
    qr_photo = ImageTk.PhotoImage(qr_img)

    qr_label = tk.Label(qr_window, image=qr_photo)
    qr_label.image = qr_photo
    qr_label.pack(pady=10)

    aviso_label = tk.Label(qr_window, text="Use seu aplicativo do banco para ler o QR Code e fazer o pagamento.", font=("Arial", 12))
    aviso_label.pack(pady=10)

    cancelar_button = tk.Button(qr_window, text="Cancelar", command=reiniciar_loja)
    cancelar_button.pack(pady=10)

    iniciar_verificacao_pagamento()

def finalizar_compra():
    if not carrinho:
        messagebox.showinfo("Carrinho", "Seu carrinho está vazio.")
        return

    global total, estado_transacao_capturado, mensagem_pagamento_mostrada
    total = sum(preco * quantidade for produto, preco, quantidade in carrinho)
    
    # Captura o estado da transação
    estado_transacao_capturado = req(URL_BASE)
    mensagem_pagamento_mostrada = False  # Resetar a mensagem de pagamento mostrada

    # Gera o QR Code Pix
    payload = Payload('Gustavo Henrique', 'a78f79c4-b03f-4a62-a298-23044251dfc6', f'{total:.2f}', 'Divinopolis', 'BAR')
    payload.gerarPayload()

    # Exibe o QR Code
    exibir_qr_code()

def reiniciar_loja():
    global carrinho, estado_transacao_capturado, total, mensagem_pagamento_mostrada
    carrinho = []
    estado_transacao_capturado = None  # Resetar o estado da transação capturado
    total = None  # Resetar o total
    mensagem_pagamento_mostrada = False  # Resetar a mensagem de pagamento mostrada
    atualizar_lista_carrinho()
    atualizar_total()
    
    # Resetar as variáveis de quantidade dos produtos
    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame):
            for subwidget in widget.winfo_children():
                if isinstance(subwidget, tk.Label) and subwidget.cget("textvariable") and isinstance(subwidget.cget("textvariable"), tk.IntVar):
                    subwidget.cget("textvariable").set(1)  # Reseta a quantidade para 1

    if 'qr_window' in globals():
        qr_window.destroy()

# Função para incrementar a quantidade
def incrementar(quantidade_var):
    quantidade_var.set(quantidade_var.get() + 1)

# Função para decrementar a quantidade
def decrementar(quantidade_var):
    if quantidade_var.get() > 1:  # Evitar que a quantidade seja menor que 1
        quantidade_var.set(quantidade_var.get() - 1)

# Inicialização da janela principal
root = tk.Tk()
root.title("Lojinha on")

# Lista para armazenar itens do carrinho
carrinho = []

# Layout da interface
linha = 0
coluna = 0
for produto, preco in produtos.items():
    frame = tk.Frame(root, borderwidth=1, relief="solid")
    frame.grid(row=linha, column=coluna, padx=10, pady=10)

    label = tk.Label(frame, text=f"{produto}\nR$ {preco:.2f}", font=("Arial", 12), padx=10, pady=10)
    label.pack()

    # Variável de quantidade e botões +/-
    quantidade_var = tk.IntVar(value=1)

    frame_quantidade = tk.Frame(frame)
    frame_quantidade.pack(pady=5)

    botao_menos = tk.Button(frame_quantidade, text="-", command=lambda q=quantidade_var: decrementar(q))
    botao_menos.pack(side=tk.LEFT)

    quantidade_label = tk.Label(frame_quantidade, textvariable=quantidade_var, width=5, font=("Arial", 12))
    quantidade_label.pack(side=tk.LEFT, padx=5)

    botao_mais = tk.Button(frame_quantidade, text="+", command=lambda q=quantidade_var: incrementar(q))
    botao_mais.pack(side=tk.LEFT)

    botao_adicionar = tk.Button(frame, text="Adicionar ao carrinho", command=lambda p=produto, pr=preco, q=quantidade_var: adicionar_ao_carrinho(p, pr, q.get()))
    botao_adicionar.pack(pady=5)

    coluna += 1
    if coluna > 2:  # Organiza os produtos em 3 colunas
        coluna = 0
        linha += 1

# Label para exibir os itens no carrinho
carrinho_label = tk.Label(root, text="", font=("Arial", 12), justify=tk.LEFT)
carrinho_label.grid(row=linha+1, column=0, columnspan=3, padx=10, pady=10)

# Label para o valor total
total_label = tk.Label(root, text="Total: R$ 0.00", font=("Arial", 14))
total_label.grid(row=linha+2, column=0, columnspan=3, pady=10)

# Botão para finalizar a compra e gerar o QR Code Pix
botao_finalizar = tk.Button(root, text="Finalizar Compra", command=finalizar_compra)
botao_finalizar.grid(row=linha+4, column=0, columnspan=3, pady=10)

# Iniciar o loop principal
root.mainloop()
