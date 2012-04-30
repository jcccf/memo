<?php
require_once('../config.php');
header("Content-type: text/plain");

$improvements_only = false;
if(isset($_GET['improvements'])) {
  $improvements_only = true;
}
?>

<?php
$qps = $db->prepare('SELECT * FROM quote_pairs');
$qps->execute();
$quote_pairs = array();
while($qpsr = $qps->fetchObject()) {
  $quote_pairs[$qpsr->id] = array($qpsr->movie_title, $qpsr->quote_1, $qpsr->quote_2);
}

$results = $db->prepare('SELECT * FROM results ORDER BY time DESC');

$total_correct = 0;
$init_correct = 0;
$counter = 0;

$results->execute();
while($result = $results->fetchObject()) {  
  $ra = json_decode($result->json);
  
  if ($improvements_only && strlen(trim($ra->comments_box)) == 0) {
    continue;
  }

  echo sprintf("%d N %s\n", $result->id, $ra->name);

  $num_correct = 0;
  $init_correct = 0;
  
  for ($i = 0; $i < QUESTION_LIMIT; $i++) {
    $question_id = 'q'.$i.'_id';
    $question_response = 'q'.$i;
    $question_switched = 'q'.$i.'_sw';
    $response = (int)$ra->$question_response - 1;
    if ($ra->$question_switched == "1") {
      $response = ($response + 1) % 2;
    }
    $quote_text = $quote_pairs[$ra->$question_id];
    echo sprintf("%d Q %s %d %s|%s|%s\n", $result->id, $ra->$question_id, $response, $quote_text[0], $quote_text[1], $quote_text[2]);
    if (($ra->$question_switched == "1" && $ra->$question_response == "2") || ($ra->$question_switched == "0" && $ra->$question_response == "1")) {
      if($i <= 2) {
        $init_correct++;
      }
      else {
        $num_correct++;
      }
    }
  }
  
  if ($improvements_only) {
    echo sprintf("%d I %s\n", $result->id, preg_replace("[\r\n]", "", $ra->comments_box));
  }

  echo sprintf("%d R %d %d %d\n", $result->id, $init_correct+$num_correct, $num_correct, QUESTION_LIMIT);
  
  $counter++;
  
  $total_init += $init_correct;
  $total_correct += $num_correct;

}

echo sprintf("AVG %d %d %f %f\n", $total_correct, $counter, $total_correct/$counter, ($total_correct+$total_init)/$counter);

?>