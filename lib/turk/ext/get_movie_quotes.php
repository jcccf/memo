<?php
require_once('config.php');

$group_id = htmlentities($_GET['gid']);
$movies = $_GET['movies'];
shuffle($movies);

// Print out questions
$a = array();
foreach($movies as $movie) {
  $posts = $db->prepare('SELECT id, movie_title, quote_1, quote_2 FROM quote_pairs WHERE group_id = ? AND movie_title = ?');
  $posts->execute(array($group_id, $movie));
  while($post = $posts->fetchObject()) {
	  $a['q'][] = array('m' => $post->movie_title, 'q1' => $post->quote_1, 'q2' => $post->quote_2, 'qid' => $post->id);
  }
}

// Select random short-term recall quote
$all_movies = $db->prepare('SELECT DISTINCT movie_title FROM quote_short_term');
$all_movies->execute();
$movie_candidates = array();
while($all_movie = $all_movies->fetchObject()) {
  if (!in_array($all_movie->movie_title, $movies)) {
    $movie_candidates[] = $all_movie->movie_title;
  }
}
shuffle($movie_candidates);
$strecall = $db->prepare('SELECT id, quote, quote_type FROM quote_short_term WHERE movie_title = ?');
$strecall->execute(array($movie_candidates[0]));
while($str = $strecall->fetchObject()) {
  if ($str->quote_type === 'positive' || $str->quote_type === 'negative') {
    $a['m']['c'][] = array('q' => $str->quote, 'id' => $str->id);
  }
  else {
    $a['m']['nc'][] = array('q' => $str->quote, 'id' => $str->id);
  }
}

echo json_encode($a);

// TODO LOG THIS REQUEST

?>