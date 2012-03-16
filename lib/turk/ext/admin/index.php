<?php
require_once('../config.php');

$results = $db->prepare('SELECT * FROM results ORDER BY time DESC');
$results->execute();
while($result = $results->fetchObject()) {
  echo "<div>";
  $ra = json_decode($result->json);
  echo "<h1>".$ra->name."</h1>";
  echo $ra->time."<br />";
  
  echo "<table>";
  echo "<thead><tr><td>#</td><td>QID</td><td>Response</td><td>Switched?</td><td>Movie</td><td>Quote 1</td><td>Quote 2</td></tr></thead><tbody>";
  
  for ($i = 0; $i < QUESTION_LIMIT; $i++) {
    echo "<tr>";
    echo "<td>".$i."</td>";
    $question_id = 'q'.$i.'_id';
    $question_response = 'q'.$i;
    $question_switched = 'q'.$i.'_sw';
    echo "<td>".$ra->$question_id."</td>";
    echo "<td>".$ra->$question_response."</td>";
    echo "<td>".$ra->$question_switched."</td>";
    $quote = $db->prepare('SELECT * FROM quote_pairs WHERE id = ?');
    $quote->execute(array($ra->$question_id));
    $q = $quote->fetchObject();
    echo "<td>".$q->movie_title."</td>";
    echo "<td>".$q->quote_1."</td>";
    echo "<td>".$q->quote_2."</td>";
    echo "</tr>";
  }
  
  echo "</tbody></table>";
  
  echo "<table>";
  echo "<thead><tr><td>ID</td><td>Type</td><td>Quote</td><td>Yes</td></tr></thead><tbody>";
  
  $st_movie_name = '';
  $seen = array();
  for ($i = 1; $i < 5; $i++) {
    echo "<tr>";
    $rec = "rec".$i;
    $rec_rem = "rec".$i."c";
    $seen[] = $ra->$rec;
    $quote = $db->prepare('SELECT * FROM quote_short_term WHERE id = ?');
    $quote->execute(array($ra->$rec));
    $q = $quote->fetchObject();
    echo "<td>".$ra->$rec."</td>";
    echo "<td>".($q->quote_type == "negative_rest" ? "Negative (Before)" : $q->quote_type)."</td>";
    echo "<td>".$q->quote."</td>";
    echo "<td>".$ra->$rec_rem."</td>";
    $st_movie_name = $q->movie_title;
    echo "</tr>";
  } 
  
  echo "<h3>Short Term Task</h3>";
  
  $quote = $db->prepare('SELECT * FROM quote_short_term WHERE movie_title = ?');
  $quote->execute(array($st_movie_name));
  while($q = $quote->fetchObject()) {
    if(!in_array($q->id, $seen)) {
     echo "<tr><td>{$q->id}</td><td>Negative (After)</td><td>{$q->quote}</td><td>-</td></tr>";
    }
  }
  
  echo "</tbody></table>";
  
  echo "<h3>Improvements</h3>";
  echo $ra->memorable_box;
  echo "<h3>Comments</h3>";
  echo $ra->comments_box;
  echo "</div><br /><br />";
}

?>