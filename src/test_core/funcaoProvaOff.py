try:
    # Python imports
    import os
    import os.path
    import sys
    import csv

    #Pip imports
    import cv2
    from fpdf import FPDF
    import numpy as np
    from PIL import ImageFont, ImageDraw, Image

    # Local Import
    from dbProva import dadosProva
    from libQr import formataQr, escreveQr
    from util import desenhaCabecalho
except Exception as e:
    print(e)

def carregar_dados(arquivo_csv):
    flag = True
    dados = []
    with open(arquivo_csv, encoding='UTF-8') as f:
        csv_reader = csv.reader(f, delimiter=";")
        for row in csv_reader:
            if flag:
                flag = False
                continue
            dados.append(row)
    return dados
def gerar_prova(arquivo_csv, pasta_output):
    id_usuario = 666
    dados = carregar_dados(arquivo_csv)
    #Quando eu comecei a trabalhar no terminal do Ubuntu ele dizia que essa variável não havia sigo criada, então eu a criei aqui
    path = ''
    try:
        pdf = FPDF(format = (int(1240/2.7),int(1754/2.7))) #Página definda para o tamanho da imagem
        m = 0
        for linha in dados:
            id_prova = int(linha[0])
            prova = linha[1]
            prof = linha[2]
            turma = linha[3]
            data = linha[4]
            nota_prova = float(linha[5])
            qtd_quadrado_v = int(linha[6])
            qtd_quadrado_h = int(linha[7])
            id_aluno = int(linha[8])
            aluno = linha[9]
            
            img = np.ones((1754,1240,3),np.uint8)*255 #imagem 1754x1240, com fundo branco e 3 canais para as cores

            altura = img.shape[0]
            largura = img.shape[1]

            fonte = cv2.FONT_HERSHEY_SIMPLEX
            escala = 0.7
            espessura = 2

            #Desenha linha e
            img = cv2.line(img,(160,270),(largura-160,270),(0,0,0),1)
            #Segunda linha
            img = cv2.line(img,(80,560),(largura-80,560),(0,0,0),2)
            #Desenha retângulos das notas
            cv2.rectangle(img, (330, 320), (580, 470), (0, 0, 0), 2)
            cv2.rectangle(img, (largura-330, 320), (largura-580, 470), (0, 0, 0), 2)
            #Desenha as informações do cabecalho
            img = desenhaCabecalho(img, largura, altura, aluno, prof, prova, turma, data, nota_prova)
            #Gera o qr
            #Nº da prova . Nº do aluno
            msg = formataQr(f'{id_prova}.{id_aluno}')
            qr_code = escreveQr(msg)

            #Coloca o qr na imagem
            img[0 : qr_code.shape[0], largura-qr_code.shape[1] : largura] = qr_code

            #Apaga qrcode depois de adicioná-lo ao pdf
            os.unlink(f'qr.png')

            #Valors originais dos topos dos triângulos (último campo, posição x): 40,largura-70, 40,
            #Cria marcadores triângulo
            t1 = np.array([[40,640],[70,640],[40,610]], np.int32)
            t2 = np.array([[largura-70,640],[largura-40,640],[largura-70,610]], np.int32)
            t3 = np.array([[40,altura-60],[70,altura-60],[40,altura-90]], np.int32)
            t4 = np.array([[largura-70,altura-60],[largura-40,altura-60],[largura-70,altura-90]], np.int32)
            t = [t1, t2, t3, t4]
            for i in range(len(t)):
                cv2.fillPoly(img, [t[i]], (0, 0, 0))

            #Coloca os marcadores quadrados na vertical
            espaco = int(0)
            cinza = (210, 210, 210)
            for i in range(qtd_quadrado_v):
                cv2.rectangle(img, (120,700 + espaco), (140, 720 + espaco), (0, 0, 0), -1)
                cv2.putText(img, f'{i+1}', (150,720 + espaco), fonte, escala, cinza, espessura)
                espaco += 45

            #Coloca os marcadores quadrados na horizontal
            espaco = 0
            for i in range(qtd_quadrado_h):
                cv2.rectangle(img, (260 + espaco,650), (280 + espaco, 670), (0, 0, 0), -1)
                espaco += 120

            #Colocando os círculos e letras
            letras = ['A','B','C','D','E','F','G']
            espaco_x = espaco_y = 0
            for i in range(qtd_quadrado_v):
                for j in range(qtd_quadrado_h):
                    cv2.circle(img, (270 + espaco_x, 710 + espaco_y), 14, cinza,2)
                    cv2.putText(img, f'{letras[j]}', (263 + espaco_x, 717 + espaco_y), fonte, escala, cinza, espessura)
                    espaco_x += 120
                espaco_x = 0
                espaco_y += 45

            #Redminsionando a imagem temporiamente apenas para os teste
            #img_new_h = resizeImg(img, 840)

            #cv2.imshow("Canvas", img)
            #cv2.waitKey(0)
            cv2.imwrite(f'{pasta_output}/prova{m}.png', img)

            #Cria nova página, quebra a página, busca a imagem
            pdf.add_page()
            pdf.set_auto_page_break(0)
            pdf.image(f'{pasta_output}/prova{m}.png')

            #Apaga imagem depois de adicioná-la ao pdf
            os.unlink(f'{pasta_output}/prova{m}.png')
            m += 1
        pdf.output(f'{pasta_output}/prova{id_usuario}.pdf', "F")
        #COMANDO QUE EXCLUI O PDF#
        path = os.path.abspath(f'{pasta_output}/prova{id_usuario}.pdf')
    except Exception as e:
        print(e)

    return path.replace("\\", "/")

try:
    path = gerar_prova(sys.argv[1], sys.argv[2])
    print(path)
except Exception as e:
    print(e)
