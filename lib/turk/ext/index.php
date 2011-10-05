<?php

$group_id = htmlentities($_GET['gid']);

try {
  $db = new PDO('sqlite:./test.db');
}
catch (Exception $e) {
  die($e);
}

$posts = $db->prepare('SELECT * FROM questions WHERE group_id = '.$group_id);
$posts->execute();

?>

<!DOCTYPE html>
<html>
<head>
  <title>MTurk HIT</title>
  <style type="text/css">
    body {
      font-family: Helvetica, Arial;
    }
    .question {
      padding-bottom: 20px;
      margin-bottom: 30px;
      border-bottom: 1px dashed gray;
    }
    .question .quote {
      font-size: larger;
      background-color: #efefef;
      margin-bottom: 10px;
      padding: 5px;
    }
    .question .qmovie {
      margin-bottom: 10px;
      padding-top: 5px;
    }
    .qoption {
    }
    input[type=submit]{
      font-size: x-large;
      background-color: #f0f0f0;
      border: 1px solid black;
    }
    label {
      display: block;
      margin: 0;
      padding: 5px;
      border: 0;
    }
    input[type=radio] {
      margin-right: 5px;
    }
  </style>
</head>

<form name="hello" action="http://www.mturk.com/mturk/externalSubmit" method="POST">

<input type="hidden" name="assignmentId" value="<?php echo $_GET['assignmentId'] ?>" />
<input type="hidden" name="groupId" value="<?php echo $group_id ?>" />

<?php
$i = 0;
while($post = $posts->fetchObject()) {
  ?>
  <div class="question">
    Q<?php echo $i+1 ?>
    <div class="qmovie">From <b><?php echo $post->movie_title ?></b></div>
    <div class="quote"><?php echo $post->quote_1 ?></div>
    <div class="quote"><?php echo $post->quote_2 ?></div>
  <div class="qoption">
  <label><input type="radio" name="q<?php echo $i ?>" value="Q1" /><b>Only the first quote</b> is memorable.</label>
  </div>
  <div class="qoption">
  <label><input type="radio" name="q<?php echo $i ?>" value="Q2" /><b>Only the second quote</b> is memorable.</label>
  </div>
  <div class="qoption">
  <label><input type="radio" name="q<?php echo $i ?>" value="B" /><b>Both quotes</b> are memorable.</label>
  </div>
  <div class="qoption">
  <label><input type="radio" name="q<?php echo $i ?>" value="N" /><b>Neither quote</b> is memorable.</label>
  </div>
  </div>
  <?php
  $i++;
}

?>

<br />
<input type="submit" value="Submit HIT" />

</form>