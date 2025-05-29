from util import *
import sys
import os
import zipfile
import shutil
from glob import glob
import tempfile

def decode_zip(zip_path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dst_dir = tempfile.mkdtemp(dir=dir_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dst_dir)
    output = []
    for img in glob(dst_dir + "/*"):
        b = os.path.basename(img)
        b = b.split(".")[:-1][0].split("_")
        # expect.: prova_aluno_qtdquestoes_qtdalternativas.jpg (ou png)
        if len(b) != 4:
            output = ["ERRO", "ERRO", img, "-6", "Nome do arquivo da imagem fora do esperado."]
        else:
            output.append(_decode_image(img, b[0], b[1], b[2], b[3]))
    shutil.rmtree(dst_dir)
    #os.remove(zip_path)
    return output

def decode_image(img_path):
    def clean_str(text):
        out = ""
        for i in text:
            try:
                i.encode('charmap')
                out += i
            except:
                pass
        return out
    b = os.path.basename(img_path)
    b = b.split(".")[:-1][0].split("_")
    tmp = _decode_image(img_path, b[0], b[1],
                                   b[2], b[3])
    return clean_str(tmp)
def teste1a(img):
    return img

#Dada a imagem original, o metodo retorna uma imagem em tons de cinza
def teste1b(img_orig):
    gray_image = cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
    return gray_image
#Dada uma imagem em tons de cinza, o metodo retorna em preto em branco
def teste1c(img_tc):
    im_bw = cv2.threshold(img_tc, 127, 255, cv2.THRESH_BINARY)[1]
    return im_bw
#Dada uma imagem original, o metodo retorna uma imagem cortada
def teste2(img):
    img_original = img.copy()
    GrayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #Transforma para tons de Cinza
    BlurredFrame = cv2.GaussianBlur(GrayImg, (5, 5), 1) #aplica um desfoque gaussiano na imagem
    _, binary = cv2.threshold(BlurredFrame, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #Determina os pontos dos contornos de interesse
    ContourFrame = img.copy()
    ContourFrame = cv2.drawContours(ContourFrame, contours[0], -1, (255, 0, 0), 25) #Desenha o contorno de interesse
    i = contours[0]
    peri = cv2.arcLength(i, True)
    edges = cv2.approxPolyDP(i, 0.02*peri, True)
    CornerFrame = img.copy()
    maxArea = 0
    biggest = []
    for i in contours :
        area = cv2.contourArea(i)
        if area > 1000 :
            peri = cv2.arcLength(i, True)
            edges = cv2.approxPolyDP(i, 0.02*peri, True)
            if area > maxArea:
                biggest = edges
                maxArea = area
    if len(biggest) != 0 :
        CornerFrame = cv2.drawContours(CornerFrame, biggest, -1, (255, 0, 255), 25)
    # cv2.drawContours(img, [biggest], -1, (0, 255, 0), 3)
    # Pixel values in the original image
    points = biggest.reshape(4, 2)
    input_points = np.zeros((4, 2), dtype="float32")

    points_sum = points.sum(axis=1)
    input_points[0] = points[np.argmin(points_sum)]
    input_points[3] = points[np.argmax(points_sum)]

    points_diff = np.diff(points, axis=1)
    input_points[1] = points[np.argmin(points_diff)]
    input_points[2] = points[np.argmax(points_diff)]

    (top_left, top_right, bottom_right, bottom_left) = input_points
    bottom_width = np.sqrt(((bottom_right[0] - bottom_left[0]) ** 2) + ((bottom_right[1] - bottom_left[1]) ** 2))
    top_width = np.sqrt(((top_right[0] - top_left[0]) ** 2) + ((top_right[1] - top_left[1]) ** 2))
    right_height = np.sqrt(((top_right[0] - bottom_right[0]) ** 2) + ((top_right[1] - bottom_right[1]) ** 2))
    left_height = np.sqrt(((top_left[0] - bottom_left[0]) ** 2) + ((top_left[1] - bottom_left[1]) ** 2))

    # Output image size
    max_width = max(int(bottom_width), int(top_width))
    # max_height = max(int(right_height), int(left_height))
    max_height = int(max_width * 1.414)  # for A4

    # Desired points values in the output image
    converted_points = np.float32([[0, 0], [max_width, 0], [0, max_height], [max_width, max_height]])

    # Perspective transformation
    matrix = cv2.getPerspectiveTransform(input_points, converted_points)
    #print(matrix)
    img_warp = cv2.warpPerspective(img_original, matrix, (max_width, max_height)) #Corta a imagem de acordo com o contorno determinado

    return img_warp
#Dada uma imagem cortada, o metodo retorna em tons de cinza
def teste3(img_warp):
    img_warp_tc = teste1b(img_warp)
    return img_warp_tc
#Dada uma imagem cortada em tons de cinza, o metodo retorna em preto em branco
def teste4(img_warp_tc):
    img_warp_pb = teste1c(img_warp_tc)
    return img_warp_pb
#Dada uma imagem cortada em tons de cinza, o metodo retorna em preto em branco usando o OTSU
def teste5(img_warp_tc):
    img_warp_tc = cv2.cvtColor(img_warp_tc, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(img_warp_tc, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    binary = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    return binary


def _decode_image(
        img_path, id_prova, id_aluno,
        num_questions_DB, num_alternatives_DB):
    img_orig = cv2.imread(img_path)

    # 1a
    img_atual = teste1a(img_orig.copy())
    tmp = _correct(img_atual, id_prova, id_aluno, num_questions_DB, num_alternatives_DB, '1a', img_path)
    if tmp.split(";")[3] == "0":
        return tmp

    # 1b
    img_atual = teste1b(img_atual)
    tmp = _correct(img_atual, id_prova, id_aluno, num_questions_DB, num_alternatives_DB, '1b', img_path)
    if tmp.split(";")[3] == "0":
        return tmp

    # 1c
    img_atual = teste1c(img_atual)
    tmp = _correct(img_atual, id_prova, id_aluno, num_questions_DB, num_alternatives_DB, '1c', img_path)
    if tmp.split(";")[3] == "0":
        return tmp

    # 2
    img_atual = teste2(img_orig.copy())
    tmp = _correct(img_atual, id_prova, id_aluno, num_questions_DB, num_alternatives_DB, '2', img_path)
    if tmp.split(";")[3] == "0":
        return tmp
    # 3
    img_atual = teste3(img_atual)
    img_warp_tc = img_atual
    tmp = _correct(img_atual, id_prova, id_aluno, num_questions_DB, num_alternatives_DB, '3', img_path)
    if tmp.split(";")[3] == "0":
        return tmp

    # 4
    img_atual = teste4(img_warp_tc)
    tmp = _correct(img_atual, id_prova, id_aluno, num_questions_DB, num_alternatives_DB, '4', img_path)
    if tmp.split(";")[3] == "0":
        return tmp

    # 5
    img_atual = teste5(img_warp_tc)
    tmp = _correct(img_atual, id_prova, id_aluno, num_questions_DB, num_alternatives_DB, '5', img_path)
    return tmp


def _correct(
        img, id_prova, id_aluno,
        num_questions_DB, num_alternatives_DB, version, img_path=''):
    tracker = 0
    num_questions_DB = int(num_questions_DB)
    num_alternatives_DB = int(num_alternatives_DB)
    file = os.path.basename(img_path) if img_path != '' else ''
    tracker += 1
    output = [
            str(id_prova),
            str(id_aluno),
            file + "[" + version + "]"]
    tracker += 2
    #print(version, " versao---------------------------------------------------------------------------------------------------------------------")
    try:
        tracker += 4
        if version in ["1a", "1b", "1c"]:
            a = paper90(img)
        else:
            a = img.copy()
        tracker += 8
        if a is None:
            output.append("-1")
            output.append("Quatro triângulos marcadores não localizados")
            return ";".join(output)
        tracker += 16
        question_squares, alternative_squares, _ = getOurSqr(a, num_questions_DB, num_alternatives_DB)
        #nome = version + "_" + str(len(question_squares)) + "_" + str(len(alternative_squares)) #MOD
        #cv2.imwrite(("version" + nome + ".jpg"), warp_img) #MOD
        if (len(question_squares) != num_questions_DB) and\
           (len(alternative_squares) != num_alternatives_DB
        ):
            output.append("-4")
            output.append(
                "Quantidades de questões (" +
                str(len(question_squares)) + " dif. " +
                str(num_questions_DB) + ") e alternativas (" +
                str(len(alternative_squares)) + " dif. " +
                str(num_alternatives_DB) + ") localizadas diferentes das esperadas")
            return ";".join(output)
        elif (len(alternative_squares) != num_alternatives_DB):
            output.append("-3")
            output.append(
                "Quantidade de alternativas localizadas (" +
                str(len(alternative_squares)) + ") diferente da esperada (" + str(num_alternatives_DB) +")")
            return ";".join(output)
        elif (len(question_squares) != num_questions_DB):
            output.append("-2")
            output.append(
                "Quantidade de questões localizadas (" +
                str(len(question_squares)) + ") diferente da esperada (" + str(num_questions_DB) + ")")
            return ";".join(output)
        tracker += 32
        respostas_aluno = getAnswers(a, num_questions_DB, num_alternatives_DB)
        tracker += 64
        output.append("0")
        output.append(",".join([str(x) for x in respostas_aluno]))
        return ";".join(output)
    except Exception as e:
        #tb = traceback.format_exc()
        #print(f"debug:\n{tb}")
        output.append("-5")
        #output.append("Erro desconhecido (cod.: " +
        #        str(tracker) + " - e: " + str(e) + ")")
        output.append("Erro desconhecido (cod.:  - e: " + str(e) + ")")
        return ";".join(output)
if len(sys.argv) < 2:
    print("Usage:   python -W ignore " + sys.argv[0] + " <caminho da imagem> <id_prova> <id_aluno> <num_questions> <num_alternatives>")
    ######## APAGAR
    #r = decode_image("img-teste/2_19_6_5.jpg")
    r = decode_image("img-teste/301_101_20_4.jpg")
    #print("[KARITI]", r)
elif sys.argv[1].upper().endswith(".ZIP"):
    r = decode_zip(sys.argv[1])
    for x in r:
        print("[KARITI]", x)
else:
    r = decode_image(sys.argv[1])
    print("[KARITI]", r)