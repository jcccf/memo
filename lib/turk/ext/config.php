<?php

try {
  $db = new PDO('mysql:host=localhost;dbname=memo_turk', 'cf_memo', 'memo3330');
}
catch (Exception $e) {
  die($e);
}

?>