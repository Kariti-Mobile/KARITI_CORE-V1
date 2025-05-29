<?php

try{  
  $ini_file = parse_ini_file('../../settings.ini', true);
  $python_l = '/home/kariti/htdocs/kariti.online/' . $ini_file['SYSTEM']['python_linux_path'];
  $cut_path_l = $ini_file['SYSTEM']['cut_path_l'];
  $python_function = ' /home/kariti/htdocs/kariti.online/src/test_core/funcaoProvaOff.py ';  
  $uploaddir = $cut_path_l;
  $value = $_FILES["userfile"]["name"][0];
  $uploadfile = $uploaddir . basename($value);
  move_uploaded_file($_FILES["userfile"]["tmp_name"][0], $uploadfile);
  $arquivo_csv = $uploadfile;
  $tmpdir = tempnam('/home/kariti/htdocs/kariti.online/tmp','');
  if (file_exists($tmpdir)) { unlink($tmpdir); }
  mkdir($tmpdir);
  $out = array();
  $cmd = '';
  $cmd = "{$python_l}{$python_function} {$arquivo_csv} {$tmpdir}";
  exec($cmd, $out);
  //echo $cmd."<br>";
  //print_r($out);
  header("Content-type:application/pdf");
  header("Content-Disposition:attachment;filename=\"kariti.pdf\"");
  
  readfile($out[0]);
} catch (Throwable $e) {
  echo "Erro";
  die();
}
?>
