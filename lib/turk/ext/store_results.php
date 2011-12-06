<?php
require_once('config.php');

$res = $db->prepare('INSERT INTO results (worker_id, json) VALUES(?, ?)');
$res->execute(array($_GET['worker_id'], $_GET['json']));

?>