<?php
$group_id = htmlentities($_GET['gid']);
$movies = $_GET['movies'];
shuffle($movies);

// Connect to DB or Die
try {
  $db = new PDO('sqlite:./test.db');
}
catch (Exception $e) {
  die($e);
}

// Print out Questions
$i = 0;
foreach($movies as $movie) {
  $posts = $db->prepare('SELECT * FROM questions WHERE group_id = ? AND movie_title = ?');
  $posts->execute(array($group_id, $movie));

  while($post = $posts->fetchObject()) {
    ?>
    <div class="question">
      Q<?php echo $i+1 ?>
      <div class="qmovie">From <b><?php echo $post->movie_title ?></b></div>
      <div class="quote"><div class="num">1</div><?php echo $post->quote_1 ?></div>
      <div class="quote"><div class="num">2</div><?php echo $post->quote_2 ?></div>
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
}

?>