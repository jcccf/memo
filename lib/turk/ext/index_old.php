<!DOCTYPE html>
<html>
<head>
  <title>MTurk HIT</title>
  <link rel="stylesheet" href="default.css" />
</head>

<?php

$group_id = $_GET['gid'];

$db = new PDO('sqlite:./test.db');

$movies = $db->prepare('SELECT DISTINCT movie_title FROM questions WHERE group_id = '.$group_id);
$movies->execute();

?>

<form name="hello" action="http://www.mturk.com/mturk/externalSubmit" method="POST">

<input type="hidden" name="assignmentId" value="<?php echo $_GET['assignmentId'] ?>" />
<input type="hidden" name="groupId" value="<?php echo $group_id ?>" />
<input type="hidden" name="hitId" value="<?php echo $_GET['hitId'] ?>" />
<input type="hidden" name="workerId" value="<?php echo $_GET['workerId'] ?>" />

<div class="container">

<div id="movie_selector">
<h1>Pick <span id="numleft">5 movies</span> that you've seen</h1>
<div id="movies">
</div>
<div style="clear: both">
<input type="button" id="see_more" value="See More" />
</div>
</div>

<div id="loading">
  <h1>Loading Movie Quotes...</h1>
</div>

<div id="questions">
<input type="button" id="next" value="Next Question" />
<input type="submit" id="submit" value="Submit HIT" />
</div>

</div>

</form>