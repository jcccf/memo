<?php
require_once('config.php');

$group_id = htmlentities($_POST['gid']);
$movies = $_POST['movies'];
$unseen = $_POST['unseen'];
shuffle($movies);
shuffle($unseen);

$a = array();

// Select random short-term recall quote
$strecall = $db->prepare('SELECT id, quote, quote_type FROM quote_short_term WHERE movie_title = ?');
$strecall->execute(array($unseen[0]));
while($str = $strecall->fetchObject()) {
  if ($str->quote_type === 'positive' || $str->quote_type === 'negative') {
    $a['m']['c'][] = array('q' => $str->quote, 'id' => $str->id);
  }
  else {
    $a['m']['nc'][] = array('q' => $str->quote, 'id' => $str->id);
  }
}

// Print out questions
// for($i=0; $i<MIN_SEEN; $i++) {
//   $posts = $db->prepare('SELECT id, movie_title, quote_1, quote_2 FROM quote_pairs WHERE group_id = ? AND movie_title = ?');
//   $posts->execute(array($group_id, $movies[$i]));
//   while($post = $posts->fetchObject()) {
//    $a['q'][] = array('m' => $post->movie_title, 'q1' => $post->quote_1, 'q2' => $post->quote_2, 'qid' => $post->id, 's' => 1);
//   }
// }
for($i=1; $i<MIN_UNSEEN; $i++) {
  $posts = $db->prepare('SELECT id, movie_title, quote_1, quote_2 FROM quote_pairs WHERE group_id = ? AND movie_title = ?');
  $posts->execute(array($group_id, $unseen[$i]));
  while($post = $posts->fetchObject()) {
   $a['q'][] = array('m' => $post->movie_title, 'q1' => $post->quote_1, 'q2' => $post->quote_2, 'qid' => $post->id, 's' => 0);
  }
}

echo json_encode($a);

?>