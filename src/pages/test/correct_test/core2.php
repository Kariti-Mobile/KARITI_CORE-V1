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
//Root path till file
if (strtolower($ini_file["SYSTEM"]["OS"]) == "windows") {
    $uploaddir = $cut_path_w;
} elseif (strtolower($ini_file["SYSTEM"]["OS"]) == "linux") {
    $uploaddir = $cut_path_l;
}
$python_function =
    " " . "/home/kariti/htdocs/kariti.online/" . "src/test_core/core2.py ";

$linhas = [];
$i = 0;
foreach ($_FILES["userfile"]["name"] as $key => $value) {
    $out = "";
    $i++;
    $j = 0;
    $uploadfile = $uploaddir . basename($value);
    if (
        move_uploaded_file($_FILES["userfile"]["tmp_name"][$key], $uploadfile)
    ) {
        if (strtolower($ini_file["SYSTEM"]["OS"]) == "windows") {
            $cmd = $python_w . " -W ignore " . $python_function . $uploadfile;
            exec($cmd, $out);
        } elseif (strtolower($ini_file["SYSTEM"]["OS"]) == "linux") {
            $cmd = $python_l . " -W ignore " . $python_function . $uploadfile;
            exec($cmd, $out);
        }
        foreach ($out as $valor) {
            $j++;
            $KARITOKEN = "[KARITI] ";
            if (str_starts_with($valor, $KARITOKEN)) {
                $aux = explode($KARITOKEN, $valor)[1];
                $aux = explode(";", $aux);
                array_push($linhas, [
                    "id_prova" => $aux[0],
                    "id_aluno" => $aux[1],
                    "arquivo" => $aux[2],
                    "resultado" => $aux[3],
                    "mensagem" => $aux[4]
                ]);
            }
        }
    }
}
header("Content-Type: application/json; charset=utf-8");
echo json_encode($linhas);

?>
