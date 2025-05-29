<?php
	ini_set('display_errors', 1);
	ini_set('display_startup_errors', 1);
	error_reporting(E_ALL);
	try{
		$pdo = new PDO('sqlite:/home/kariti/htdocs/kariti.online/src/database/database.db');
		print('OK\n');
		$sql = "update usuario set senha = '25d55ad283aa400af464c76d713c07ad' where id_usuario=4";
		$pdo->exec($sql);
		print("XXXXOK");
	}catch(PDOException $e){
		print('ERRO\n');
	}
