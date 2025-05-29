<!DOCTYPE html>
<html>
<body>

<form action="core.php" method="post" enctype="multipart/form-data">
  Selecione arquivos ZIP ou de imagens. <br><br>Os nomes dos arquivos de imagens devem estar na forma idprova_id_aluno_qtdquestoes_qtd_alternativas (ex.: 77_89_9_7.jpg):<br><br />
  <input name="userfile[]" type="file" /><br />
  <input name="userfile[]" type="file" /><br />
  <input name="userfile[]" type="file" /><br />
  <input name="userfile[]" type="file" /><br />
  <input name="userfile[]" type="file" /><br /><br>
  <input type="submit" value="Enviar para corrigir" />
</form>
  
</body>
</html>
