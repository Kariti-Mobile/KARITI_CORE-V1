# http://kariti.online/src/services/download_template/download_tester.php

import traceback
try:
    import cv2
    import numpy as np
    import os
    import os.path
    import sys
    from fpdf import FPDF
    from PIL import ImageFont, ImageDraw, Image
    #from util import * Já está sendo inportada em dbProva.py
    from libQr import *
    from dbProva import *
    import csv
except Exception as e:
    print(e)

def gerar_prova_corrigida(id_prova,
                          nome_prova,
                          nome_professor,
                          nome_turma,
                          data_prova,
                          qtd_questoes,
                          qtd_alternativas,
                          nota_prova,
                          respostas_dadas,
                          respostas_esperadas,
                          id_aluno,
                          nome_aluno,
                          notas_questoes,
                          basedir ='.'):
    path = ''
    prova = nome_prova
    prof = nome_professor
    turma = nome_turma
    data = data_prova
    qtd_quadrado_v = qtd_questoes
    qtd_quadrado_h = qtd_alternativas

    try:
        if(not os.path.isdir(f'{basedir}/')):
            os.mkdir(f'{basedir}/')



        respostas, gabarito = respostas_dadas, respostas_esperadas
        img = np.ones((1754,1240,3),np.uint8)*255 #imagem 1754x1240, com fundo branco e 3 canais para as cores

        altura = img.shape[0]
        largura = img.shape[1]

        fonte = cv2.FONT_HERSHEY_SIMPLEX
        escala = 0.7
        espessura = 2

        img = cv2.line(img,(160,270),(largura-160,270),(0,0,0),1)
        img = cv2.line(img,(80,560),(largura-80,560),(0,0,0),2)
        cv2.rectangle(img, (330, 320), (580, 470), (0, 0, 0), 2)
        cv2.rectangle(img, (largura-330, 320), (largura-580, 470), (0, 0, 0), 2)

        #Desenha as informações do cabecalho
        img = desenhaCabecalho(img, largura, altura, nome_aluno, prof, prova, turma, data, nota_prova)

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
        vermelho = (0, 0, 255)
        verde = (75, 255, 75)
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
        nota_aluno = 0
        for i in range(qtd_quadrado_v):
            #Calcula nota do aluno
            if(respostas[i] == gabarito[i]):
                nota_aluno += notas_questoes[i]
            for j in range(qtd_quadrado_h):
                cv2.circle(img, (270 + espaco_x, 710 + espaco_y), 14, cinza,2)
                if (str(j+1) in str(respostas[i])
                ):
                    #pass
                    # Draw green circle
                    cv2.circle(img, (270 + espaco_x, 710 + espaco_y), 14, vermelho, -1)
                    cv2.circle(img, (270 + espaco_x, 710 + espaco_y), 14, vermelho, 2)
                if (gabarito[i]-1 == j):
                    ratio = 14 if (len(str(respostas[i])) == 1) else 12
                    # Draw red circle
                    cv2.circle(img, (270 + espaco_x, 710 + espaco_y), ratio, verde,-1)
                    cv2.circle(img, (270 + espaco_x, 710 + espaco_y), ratio, verde,2)

                cv2.putText(img, f'{letras[j]}', (263 + espaco_x, 717 + espaco_y), fonte, escala, cinza, espessura)
                espaco_x += 120
            espaco_x = 0
            espaco_y += 45

        # print(respostas)

        #Coloca os campos de nota obtida pelo aluno
        img_pil = Image.fromarray(img) #Não sei o que faz
        draw = ImageDraw.Draw(img_pil) #Não sei o que faz

        font2 = ImageFont.truetype(fm.findfont(fm.FontProperties(family='DejaVu Sans')),72)
        peso_total_aluno = float(nota_aluno)#Peso total da prova
        if peso_total_aluno >= 100:
            draw.text((380 + 280,355), f'{peso_total_aluno:.2f}', font = font2, fill = (0, 0, 0, 0))
        elif peso_total_aluno >= 10:
            draw.text((405 + 280,355), f'{peso_total_aluno:.2f}', font = font2, fill = (0, 0, 0, 0))
        else:
            draw.text((425 + 280,355), f'{peso_total_aluno:.2f}', font = font2, fill = (0, 0, 0, 0))

        img = np.array(img_pil)

        #Redminsionando a imagem temporiamente apenas para os teste
        #img_new_h = resizeImg(img, 840)

        #cv2.imshow("Canvas", img)
        #cv2.waitKey(0)

        path = f'{basedir}/prova{id_prova}-{id_aluno}.png'
        cv2.imwrite(path, img)
        path = os.path.abspath(path)

    except Exception as e:
        print(traceback.format_exc())
        print(e)

    return path.replace("\\", "/")

def ler_csv_para_gerar_provas(caminho):
    provas = []
    with open(caminho, encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=";")
        for row in csv_reader:
            row[0] = int(row[0])
            row[5] = int(row[5])
            row[6] = int(row[6])
            row[7] = float(row[7])
            row[8] = [int(_) for _ in row[8].replace(' ', '').split(",")]
            row[9] = [int(_) for _ in row[9].replace(' ', '').split(",")]
            row[10] = int(row[10])
            row[12] = [float(_) for _ in row[12].replace(' ', '').split(",")]
            provas.append(row)
    return gerar_provas_corrigidas(provas)
    # provas = [
    #     [167,
    #      "Provinha do barulho",
    #      "Raimundinho",
    #      "Capetinhas da Berê",
    #      "2024-07-01",
    #      8,
    #      5,
    #      8.7,
    #      [1, 0, 3, 4, 5, 1, 2, 3],
    #      [5, 4, 3, 2, 1, 1, 2, 3],
    #      78,
    #      "Pestinha Pereira",
    #      [1.0, 0.5, 0.3, 0.7, 0.9, 1.0, 2.0, 0.2]],
    #     [168,
    #      "Provinha do quietinho",
    #      "Capitinga",
    #      "Anjinhos da febem",
    #      "2024-06-24",
    #      7,
    #      5,
    #      5.2,
    #      [1, 0, 2, 4, 5, 1, 2],
    #      [1, 4, 3, 4, 5, 1, 4],
    #      72,
    #      "Tchucky Santos",
    #      [1.0, 0.5, 0.3, 0.7, 0.9, 1.0, 2.0]],
    # ]
def gerar_provas_corrigidas(provas, basedir='.'):

    ids_provas = set()
    pdf = FPDF(format=(int(1240 / 2.7), int(1754 / 2.7)))  # Página definda para o tamanho da imagem
    for prova in provas:
        imagem_pagina = gerar_prova_corrigida(*prova)
        ids_provas.add(prova[0])
        pdf.add_page()
        pdf.set_auto_page_break(0)
        pdf.image(imagem_pagina)

        # Apaga imagem depois de adicioná-la ao pdf
        os.unlink(imagem_pagina)
    aux = "-".join([str(_) for _ in ids_provas])
    path = f'{basedir}/prova{aux}.pdf'
    pdf.output(path, "F")
    path = os.path.abspath(path)
    return path.replace("\\", "/")

# print(ler_csv_para_gerar_provas("C:\\Users\\padov\\Downloads\\apagar\\exemplo.csv"))
# print(gerar_provas_corrigidas())
# print(gerar_prova_corrigida(167,
#                           "Provinha do barulho",
#                           "Raimundinho",
#                           "Capetinhas da Berê",
#                           "2024-07-01",
#                           8,
#                           5,
#                           8.7,
#                           [1,0,3,4,5,1,2,3],
#                           [5,4,3,2,1,1,2,3],
#                           78,
#                           "Pestinha Pereira",
#                             [1.0, 0.5,0.3,0.7,0.9,1.0,2.0,0.2]))
# print("Aqui", os.path.dirname(__file__))
def gerar_prova(id_prova, basedir ='.', id_alunos = None):
    #Quando eu comecei a trabalhar no terminal do Ubuntu ele dizia que essa variável não havia sigo criada, então eu a criei aqui
    path = ''
    try:
        #Verifica se a pasta 'provas' já existe
        #Se não existir, ela será criada
        if(not os.path.isdir(f'{basedir}/')):
            os.mkdir(f'{basedir}/')

        #nome_prova, nome_professor, nome_turma, data, qtd_q, qtd_a, nome_alunos
        prova, prof, turma, data, qtd_quadrado_v, qtd_quadrado_h, nota_prova, aluno, id_aluno, id_usuario = dadosProva(id_prova, basedir, id_alunos)

        pdf = FPDF(format = (int(1240/2.7),int(1754/2.7))) #Página definda para o tamanho da imagem
        for m in range(len(aluno)):
            #Pega a prova E gabarito pra mostrar o que o aluno marcou e onde ele acertou
            respostas, gabarito, _, _ = obterProva(str(id_prova), str(id_aluno[m]))
            if respostas != []:
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
                img = desenhaCabecalho(img, largura, altura, aluno[m], prof, prova, turma, data, nota_prova)

                #Gera o qr
                #Nº da prova . Nº do aluno
                msg = formataQr(f'{id_prova}.{id_aluno[m]}')
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
                vermelho = (0, 0, 255)
                verde = (75, 255, 75)
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
                nota_aluno = 0
                for i in range(qtd_quadrado_v):
                    #Calcula nota do aluno
                    if(respostas[i][1] == gabarito[i][1]):
                        nota_aluno += gabarito[i][2]
                    for j in range(qtd_quadrado_h):
                        cv2.circle(img, (270 + espaco_x, 710 + espaco_y), 14, cinza,2)
                        if (respostas[i][0] == i+1 and respostas[i][1] == j+1):
                            # Just if there is a  answer in this question
                            if (respostas[i][1] != -1):
                                # Draw red circle
                                cv2.circle(img, (270 + espaco_x, 710 + espaco_y), 14, vermelho,-1)
                                cv2.circle(img, (270 + espaco_x, 710 + espaco_y), 14, vermelho,2)

                        if (gabarito[i][0] == i+1 and gabarito[i][1] == j+1):
                            # Just if there is a  answer in this question
                            if(respostas[i][1] != -1):
                                # Draw green circle
                                cv2.circle(img, (270 + espaco_x, 710 + espaco_y), 14, verde,-1)
                                cv2.circle(img, (270 + espaco_x, 710 + espaco_y), 14, verde,2)
                        cv2.putText(img, f'{letras[j]}', (263 + espaco_x, 717 + espaco_y), fonte, escala, cinza, espessura)
                        espaco_x += 120
                    espaco_x = 0
                    espaco_y += 45

                # print(respostas)

                #Coloca os campos de nota obtida pelo aluno
                img_pil = Image.fromarray(img) #Não sei o que faz
                draw = ImageDraw.Draw(img_pil) #Não sei o que faz

                font2 = ImageFont.truetype(fm.findfont(fm.FontProperties(family='DejaVu Sans')),72)
                peso_total_aluno = float(nota_aluno)#Peso total da prova
                if peso_total_aluno >= 100:
                    draw.text((380 + 280,355), f'{peso_total_aluno:.2f}', font = font2, fill = (0, 0, 0, 0))
                elif peso_total_aluno >= 10:
                    draw.text((405 + 280,355), f'{peso_total_aluno:.2f}', font = font2, fill = (0, 0, 0, 0))
                else:
                    draw.text((425 + 280,355), f'{peso_total_aluno:.2f}', font = font2, fill = (0, 0, 0, 0))

                img = np.array(img_pil)

                #Redminsionando a imagem temporiamente apenas para os teste
                #img_new_h = resizeImg(img, 840)

                #cv2.imshow("Canvas", img)
                #cv2.waitKey(0)
                cv2.imwrite(f'{basedir}/prova{m}.png', img)

                #Cria nova página, quebra a página, busca a imagem
                pdf.add_page()
                pdf.set_auto_page_break(0)
                pdf.image(f'{basedir}/prova{m}.png')

                #Apaga imagem depois de adicioná-la ao pdf
                os.unlink(f'{basedir}/prova{m}.png')

        pdf.output(f'{basedir}/prova{id_usuario}.pdf', "F")
        #COMANDO QUE BAIXA O PDF#
        #COMANDO QUE EXCLUI O PDF#
        path = os.path.abspath(f'{basedir}/prova{id_usuario}.pdf')

    except Exception as e:
        print(e)

    return path.replace("\\", "/")


print(ler_csv_para_gerar_provas(sys.argv[1]))