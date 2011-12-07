<?php
require_once('config.php');

$res = $db->prepare('INSERT INTO results (worker_id, json) VALUES(?, ?)');
$res->execute(array($_POST['worker_id'], $_POST['json']));

?>