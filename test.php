<?php

class TestingSuit {
    private $path_to_tests = "./tests";
    private $test_folders;
    private $tests;
    private $jexmal_location = "./jexaml"; // TODO
    private $focus_on = "#";
    private $passed = 0;
    private $failed = 0;

    function __construct($focus_on)
    {
        $this->focus_on = $focus_on;
        $this->test_folders = preg_grep('/^([^.])/', scandir($this->path_to_tests));

        if ($this->test_folders == false) {
            echo "error";
            // TODO error
        }
        exec("find ./tests -name \*.xml -type f -delete");
        exec("find ./tests -name \*.xml.log -type f -delete");
        $current_test = "\n";
        foreach ($this->test_folders as $test_folder) {
            if ($this->focus_on != "#" && $test_folder != $this->focus_on) {
                continue;
            }
            $test_groups = preg_grep('/^([^.])/', scandir("$this->path_to_tests/$test_folder"));
            foreach ($test_groups as $test_group) {
                $tests = preg_grep('/^([^.])/', scandir("$this->path_to_tests/$test_folder/$test_group"));
                foreach ($tests as $test) {
                    if (explode(".", $test)[0] != $current_test) {
                        $current_test = explode(".", $test)[0];
                        $out = [];
                        exec("cat $this->path_to_tests/$test_folder/$test_group/$current_test.rc",
                            $out, $rc);
                        $this->tests[] = array("$this->path_to_tests/$test_folder/$test_group", $current_test, (int)$out[0]);
                    }
                }
            }
        }
    }

    private function parse_files() {
        foreach ($this->tests as &$test){
            $test[] = $this->parse_file($test);
        }
    }

    private function run_tests() {
        foreach ($this->tests as $test) {
            $ret = $this->test_match($test);
            if ($ret == 0) {
                echo "Test $test[0]/$test[1] passed\n";
                $this->passed++;
            } elseif ($test[2] == $test[3]) {
                echo "Test $test[0]/$test[1] passed\n";
                $this->passed++;
            } else {
                echo "Test $test[0]/$test[1] failed exit code: $test[3] should be $test[2]\n";
                $this->failed++;
            }
        }

        echo "Result: $this->passed PASSED and $this->failed FAILED\n";
    }

    private function test_match($in) {
        exec("java -jar $this->jexmal_location/jexamxml.jar $in[0]/$in[1].xml $in[0]/$in[1].out $this->jexmal_location/options",
            $out, $ret_code);

        return (int)$ret_code;
    }

    private function parse_file($file) {
        exec("php parse.php < $file[0]/$file[1].src > $file[0]/$file[1].xml",$out, $ret_code);

        return (int)$ret_code;
    }

    public function begin_testing() {
        $this->parse_files();
        $this->run_tests();
    }
}

$test = new TestingSuit("parse-only");
$test->begin_testing();

?>