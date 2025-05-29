<?php
    $ini_file = parse_ini_file("../../../settings.ini", true);
    $python_w =
        "/home/kariti/htdocs/kariti.online/" .
        $ini_file["SYSTEM"]["python_windows_path"];
    $python_l =
        "/home/kariti/htdocs/kariti.online/" .
        $ini_file["SYSTEM"]["python_linux_path"];
    $cut_path_l = $ini_file["SYSTEM"]["cut_path_l"];
    $cut_path_w = $ini_file["SYSTEM"]["cut_path_w"];

    /*
    ini_set("display_errors", 1);
    ini_set("display_startup_errors", 1);
    error_reporting(E_ALL);
    */

    /*
    $uploadfile = "/home/kariti/htdocs/kariti.online/tmp/toy1.jpg";
    $python_function = ' ' . "/home/kariti/htdocs/kariti.online/" . 'src/test_core/correctTest.py ';
    */
    //$uploadfile = "/home/kariti/htdocs/kariti.online/tmp/toy.zip";
    $uploadfile = "/home/kariti/htdocs/kariti.online/tmp/77_88_7_5.jpg";
    //$uploadfile = "/home/kariti/htdocs/kariti.online/tmp/toy1.jpg 77 88 7 5";

    $python_function =
        " " . "/home/kariti/htdocs/kariti.online/" . "src/test_core/core.py ";

    if (strtolower($ini_file["SYSTEM"]["OS"]) == "windows") {
        $cmd = $python_w . " -W ignore " . $python_function . $uploadfile;
        exec($cmd, $out);
    } elseif (strtolower($ini_file["SYSTEM"]["OS"]) == "linux") {
        $cmd = $python_l . " -W ignore " . $python_function . $uploadfile;
        exec($cmd, $out);
    }

    //print_r($out);
    $linhas = array();
    foreach ($out as $valor){
        $KARITOKEN = "[KARITI] ";
        if (str_starts_with($valor, $KARITOKEN)){
            $aux = explode($KARITOKEN, $valor)[1];
            $aux = explode(";",$aux);
            array_push($linhas, array("id_prova" => $aux[0], "id_aluno" => $aux[1], "arquivo" => $aux[2], "resultado" => $aux[3], "mensagem" => $aux[4]));
        }
    }
	//echo "<br><br>";
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($linhas);
    /*
    $aux = array( array("ch1" => "a1", "ch2" => "a2"), array("ch1" => "b1", "ch2" => "b2"), array("ch1" => "c1", "ch2" => "c2"));
    print_r($aux);
    echo "<br><br>";
    echo json_encode($aux);
    */
?>
