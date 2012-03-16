<?php
require_once('config.php');

$group_id = $_POST['group_id'];

$movies = $db->prepare('SELECT movie_title, is_imdb_top FROM movies WHERE cleaned = 1');
$movies->execute();

$pop_movies = array();
$reg_movies = array();
while($movie = $movies->fetchObject()) {
  if ($movie->is_imdb_top == 1) {
    $pop_movies[] = $movie->movie_title;
  }
  else {
    $reg_movies[] = $movie->movie_title;
  }
}

shuffle($pop_movies);
shuffle($reg_movies);

// Interleave $pop_movies and $reg_movies
$i = 0;
$j = 0;
$final = array();
while ($i < sizeof($pop_movies)) {
  $final[] = $pop_movies[$i];
  for($k = 0; $k < 5; $k++) {
    if ($j < sizeof($reg_movies)) {
      $final[] = $reg_movies[$j];
      $j++;
    }
  }
  $i++;
}
// Append rest of $reg_movies if any
if ($j < sizeof($reg_movies)) {
  $final[] = $reg_movies[$j];
  $j++;
}

echo json_encode($final);

?>