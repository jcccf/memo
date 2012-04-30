<?php
require_once('../config.php');
?>
<html>

<head>
  <title>Admin!</title>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
  <script>
  $().ready(function() {
    $('table').each(function() {
      $table = $(this);
      $input = $('<input type="button" value="Show" />')
      $input.click(function() { 
        $(this).next().show();
      });
      $table.before($input);
      $table.hide();
    });
  });
  </script>
</head>
  
<body>
<?php
if (isset($_GET['end_id'])) {
  $end_id = $_GET['end_id'];
  $results = $db->prepare('SELECT * FROM results WHERE id < '.$end_id.' ORDER BY time DESC LIMIT 50');
}
else {
  $results = $db->prepare('SELECT * FROM results ORDER BY time DESC LIMIT 50');
}

$results->execute();
while($result = $results->fetchObject()) {
  $ended_id = $result->id;
  echo "<div>";
  $ra = json_decode($result->json);
  echo "<h1>".$ra->name."</h1>";
  //echo $ra->time.$result->id."<br />";
  echo "<h3>Memo Task</h3>";
  echo "<table>";
  echo "<thead><tr><td>#</td><td>QID</td><td>Response</td><td>Switched?</td><td>Movie</td><td>Quote 1</td><td>Quote 2</td></tr></thead><tbody>";
  
  $num_correct = 0;
  $init_correct = 0;
  
  for ($i = 0; $i < QUESTION_LIMIT; $i++) {
    echo "<tr>";
    echo "<td>".$i."</td>";
    $question_id = 'q'.$i.'_id';
    $question_response = 'q'.$i;
    $question_switched = 'q'.$i.'_sw';
    echo "<td>".$ra->$question_id."</td>";
    echo "<td>".$ra->$question_response."</td>";
    echo "<td>".$ra->$question_switched."</td>";
    if (($ra->$question_switched == "1" && $ra->$question_response == "2") || ($ra->$question_switched == "0" && $ra->$question_response == "1")) {
      if($i <= 2) {
        $init_correct++;
      }
      else {
        $num_correct++;
      }
    }
    $quote = $db->prepare('SELECT * FROM quote_pairs WHERE id = ?');
    $quote->execute(array($ra->$question_id));
    $q = $quote->fetchObject();
    echo "<td>".$q->movie_title."</td>";
    echo "<td>".$q->quote_1."</td>";
    echo "<td>".$q->quote_2."</td>";
    echo "</tr>";
  }
  
  echo "</tbody></table>";
  
  echo "<br />".($init_correct+$num_correct)."/".QUESTION_LIMIT."&nbsp;&nbsp;".$num_correct."/".(QUESTION_LIMIT-3);
  
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
<a href = "<?php echo $_SERVER['PHP_SELF']?>?end_id=<?php echo $ended_id ?>">Next</a>

</body>
</html>