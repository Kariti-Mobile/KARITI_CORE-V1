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
    b = os.path.basename(img_path)
    b = b.split(".")[:-1][0].split("_")
    return _decode_image(img_path, b[0], b[1],
                                   b[2], b[3])
def _decode_image(
        img_path, id_prova, id_aluno, 
        num_questions_DB, num_alternatives_DB):
    tracker = 0
    num_questions_DB = int(num_questions_DB)
    num_alternatives_DB = int(num_alternatives_DB)
    file = os.path.basename(img_path)
    tracker += 1        
    output = [
            str(id_prova), 
            str(id_aluno), 
            file]
    try:
        tracker += 2
        img = cv2.imread(img_path)
        tracker += 4
        a = paper90(img)
        tracker += 8
        if a is None:
            output.append("-1")
            output.append("Quatro triângulos marcadores não localizados")
            return ";".join(output)
        tracker += 16
        question_squares, alternative_squares, _ = getOurSqr(a)
        if (len(question_squares) != num_questions_DB) and\
           (len(alternative_squares) != num_alternatives_DB
        ):
            output.append("-4")
            output.append(
                "Quantidades de questões (" + 
                str(len(question_squares)) + " ≠ " +
                str(num_questions_DB) + ") e alternativas (" +
                str(len(alternative_squares)) + " ≠ " +
                str(num_alternatives_DB) + ") localizadas diferentes das esperadas")
            return ";".join(output)
        if (len(alternative_squares) != num_alternatives_DB):
            output.append("-3")
            output.append(
                "Quantidade de alternativas (" +
                str(len(alternative_squares)) + " ≠ " +
                str(num_alternatives_DB) + ") localizada diferente da esperada")
            return ";".join(output)
        if (len(question_squares) != num_questions_DB):
            output.append("-2")
            output.append(
                "Quantidade de questões (" + 
                str(len(question_squares)) + " ≠ " +
                str(num_questions_DB) + ") localizada diferente da esperada")
            return ";".join(output)
            
        tracker += 32
        respostas_aluno = getAnswers(a)
        tracker += 64
        output.append("0")
        output.append(",".join([str(x) for x in respostas_aluno]))
        return ";".join(output)
    except Exception as e:
        output.append("-5")
        output.append("Erro desconhecido (cod.: " + 
                str(tracker) + " - e: " + str(e) + ")")
        return ";".join(output)

if len(sys.argv) < 2:
    print("Usage:   python -W ignore " + sys.argv[0] + " <caminho da imagem> <id_prova> <id_aluno> <num_questions> <num_alternatives>")
elif sys.argv[1].upper().endswith(".ZIP"):
    r = decode_zip(sys.argv[1])
    for x in r:
        print("[KARITI]", x)
else:
    r = decode_image(sys.argv[1])
    print("[KARITI]", r)