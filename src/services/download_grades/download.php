<?php
  $ini_file = parse_ini_file('../../settings.ini', true);
  $python_l = '/home/kariti/htdocs/kariti.online/' . $ini_file['SYSTEM']['python_linux_path'];
  $cut_path_l = $ini_file['SYSTEM']['cut_path_l'];
  $python_function = ' /home/kariti/htdocs/kariti.online/src/test_core/baixarCorrigidas.py ';  
  $uploaddir = $cut_path_l;

  $value = $_FILES["userfile"]["name"][0];
  $uploadfile = $uploaddir . basename($value);
  move_uploaded_file($_FILES["userfile"]["tmp_name"][0], $uploadfile);
  $arquivo_csv = $uploadfile;
  
  $out = array();
  $cmd = '';
  $cmd = "{$python_l}{$python_function} {$arquivo_csv}";
  exec($cmd, $out);
  
  header("Content-type:application/pdf");
  header("Content-Disposition:attachment;filename=\"kariti.pdf\"");
  readfile($out[0]);
?>
