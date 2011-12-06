<?php
require_once('config.php');

$group_id = $_GET['group_id'];

$movies = $db->prepare('SELECT DISTINCT movie_title FROM quote_pairs WHERE group_id = ?');
$movies->execute(array($group_id));

$movie_candidates = array();
while($movie = $movies->fetchObject()) {
  $movie_candidates[] = $movie->movie_title;
}

shuffle($movie_candidates);
echo json_encode($movie_candidates);

?>