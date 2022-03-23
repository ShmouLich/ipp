<?php
/*
 * autor: Ondřej Kříž - xkrizo05
 * projekt: ipp
 */

class Instruction {
    public string $name;        //nazev instrukce
    public int $opNum;          //pocet operandu
    public array $operands;     //operandy
}

function is_label($string): bool {
    return preg_match("/^[_\-$&%*!?a-zA-Z][_\-$&%*!?a-zA-Z0-9]*$/", $string) != 0;
}

//
function is_type($string): bool {
    return ($string == "bool" or $string == "int" or $string == "string");
}

function is_var($string): bool {
    $line = explode("@", "$string");
    $frame = (str_contains($line[0], "GF") or str_contains($line[0], "LF") or str_contains($line[0], "TF"));
    return $frame and is_label($line[1]);
}

function is_const($string): bool {
    $line = explode("@", "$string");
    //$type = is_type($line[0]);
    $value = false;

    if ($line[0] == "bool") {
        $value = ($line[1] == "true" or $line[1] == "false");
    }
    else if ($line[0] == "int") {
        $value = is_numeric($line[1]);
    }
    else if ($line[0] == "nil") {
        $value = ($line[1] == "nil");
    }
    else if ($line[0] == "string") {
        $value = true;//is_string($line[1]);
    }

    return $value;// and $type;
}

function is_symb($string): bool {
    return is_var($string) or is_const($string);
}

function print_help() {
    echo "parses ippcode22 code and prints it into stdout xml formatting\n";
    echo "usage: parse.php\n";
    echo "   options:\n";
    echo "--h, --help   prints help\n";
}

function process_instruction($instruction, $line, $instructions_list) {

    if (!array_key_exists(strtoupper($line[0]), $instructions_list)) {
        exit(22);
    }

    $instruction->name = strtoupper($line[0]);
    $curr_instruction = $instructions_list[$instruction->name];
    $instruction->opNum = count($curr_instruction);

    if (count($line) - 1 != $instruction->opNum) {
        exit(23);
    }

    for ($i = 1; $i <= $instruction->opNum; $i++) {
        if ($curr_instruction[$i - 1] == "var" and !is_var($line[$i])) {
            exit(23);
        }
        else if ($curr_instruction[$i - 1] == "symb" and !is_symb($line[$i])) {
            exit(23);
        }
        else if ($curr_instruction[$i - 1] == "label" and !is_label($line[$i])) {
            exit(23);
        }
        else if ($curr_instruction[$i - 1] == "type" and !is_type($line[$i])) {
            exit(23);
        }


        if (!preg_match('/^(\\\[0-9]{3}|[^\\\])*$/', $line[1])) {
            exit(23);
        }

        $instruction->operands[$i - 1] = $line[$i];
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                                                 MAIN                                                               //
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//kontrola vstupnich argumentu
if ($argc == 2 and ($argv[1] == "--help" or $argv[1] == "--h")) {
    print_help();
    exit(0);
} else if ($argc > 2) {
    exit(10);
}

$file = fopen('php://stdin', 'r') or die (11);

$instructions_list = array(
    "MOVE" => ["var", "symb"],
    "CREATEFRAME" => [],
    "PUSHFRAME" => [],
    "POPFRAME" => [],
    "DEFVAR" => ["var"],
    "CALL" => ["label"],
    "RETURN" => [],
    "PUSHS" => ["symb"],
    "POPS" => ["var"],
    "ADD" => ["var", "symb", "symb"],
    "SUB" => ["var", "symb", "symb"],
    "MUL" => ["var", "symb", "symb"],
    "IDIV" => ["var", "symb", "symb"],
    "LT" => ["var", "symb", "symb"],
    "GT" => ["var", "symb", "symb"],
    "EQ" => ["var", "symb", "symb"],
    "AND" => ["var", "symb", "symb"],
    "OR" => ["var", "symb", "symb"],
    "NOT" => ["var", "symb"],
    "INT2CHAR" => ["var", "symb"],
    "STRI2INT" => ["var", "symb", "symb"],
    "READ" => ["var", "type"],
    "WRITE" => ["symb"],
    "CONCAT" => ["var", "symb", "symb"],
    "STRLEN" => ["var", "symb"],
    "GETCHAR" => ["var", "symb", "symb"],
    "SETCHAR" => ["var", "symb", "symb"],
    "TYPE" => ["var", "symb"],
    "LABEL" => ["label"],
    "JUMP" => ["label"],
    "JUMPIFEQ" => ["label", "symb", "symb"],
    "JUMPIFNEQ" => ["label", "symb", "symb"],
    "EXIT" => ["symb"],
    "DPRINT" => ["symb"],
    "BREAK" => []
);

//na zacatku souboru ocekavame hlavicku

$line = fgets($file);

while (str_contains($line, "#") or $line == "\n") {

    if (($pos = strpos($line, '#')) !== false) {
        $line = substr($line, 0, $pos);
    }

    if (str_contains($line, ".IPPcode22")) {
        break;
    }

    $line = fgets($file);
}

$code = explode("e", $line)[1] ?? null;
$line = trim($line);
$line = explode(" ", $line);

if (!str_contains($line[0], ".IPPcode22") or $code != "22") {
    exit(21);
}

$out = fopen('php://stdout', 'w') or die (12);

try {
    $xml = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?>'
        . '<program language="IPPcode22">'
        . '</program>');
} catch (Exception $e) {exit(0);}

$counter = 0;

//rozbiti souboru na radky a radku na tokeny
while (($line = fgets($file))) {

    //double header
    if (str_contains($line[0], ".IPPcode22")) {
        exit(22);
    }

    str_replace("<", "&lt;", $line);
    str_replace(">", "&gt;", $line);
    str_replace("&", "&amp;", $line);

    //detekce komentare v ramci radku a jeho pripadne odstraneni
    $pos = strpos($line, '#');

    if ($pos !== false) {
        if ($pos == 0) {
            continue;
        }
        $line = substr($line, 0, $pos);
    }

    $line = trim($line);
    $line = preg_replace("/[\x20]+/", " ", $line);

    $words = explode(" ", $line);
    if ($words[0] == "\n" or $words[0] == "") {
        //preskocime prazdne radky
        continue;
    }

    $instruction = new Instruction();
    process_instruction($instruction, $words, $instructions_list);

    $counter++;

    $xmlLine = $xml->addChild('instruction');
    $xmlLine->addAttribute('order', $counter);
    $xmlLine->addAttribute('opcode', $instruction->name);

    for ($i = 1; $i <= $instruction->opNum; $i++) {

        $name = "arg$i";

        //pokud je v nazvu argumentu specifikovany frame, jedna se o promennou
        if (is_var($instruction->operands[$i-1])) {
            $type = "var";
            $value = $instruction->operands[$i-1];
        }
        else if (is_type($instruction->operands[$i-1])) {
            $type = "type";
            $value = $instruction->operands[$i-1];
        }
        //jinak je v operandu urcen typ a hodnota promenne
        else {

            $tmp = explode("@", $instruction->operands[$i-1]);
            $type = $tmp[0];
            if (empty($tmp[1])) {
                continue;
            }
            $value = $tmp[1];
        }

        $value = str_replace("\n", "", $value);

        $xmlArg = $xmlLine->addChild($name, htmlspecialchars($value));
        $xmlArg->addAttribute('type', $type);
    }
}

$dom = dom_import_simplexml($xml)->ownerDocument;
$dom->formatOutput = true;
fwrite($out, $dom->saveXML());

fclose($file);
fclose($out);
