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

$movies = $db->prepare('SELECT DISTINCT movie_title FROM questions WHERE group_id = '.$group_id);
$movies->execute();

?>

<!DOCTYPE html>
<html>
<head>
  <title>MTurk HIT</title>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js"></script>
  <script>
    function oc(a) {
      var o = {};
      for(var i=0;i<a.length;i++)
        o[a[i]]='';
      return o;
    }
  
    $().ready(function(){
      
      //
      // Questions Code
      //
      
      var n = 0;
      $('#questions').hide();
      $('#submit').hide();
      
      $('#next').click(function(){
        if (!$('input[name=q'+n+']:checked').val()) {
          $('input[name=q'+n+']').each(function(){
            $(this).parent().animate({color: 'red'}, 300);
          });
          return false;
        }
        $('.question:eq('+n+')').hide();
        n++;
        if ($('.question:eq('+n+')').length > 0) {
          $('.question:eq('+n+')').show();
        }
        if ($('.question:eq('+(n+1)+')').length == 0) {
          $('#next').hide();
          $('#submit').show();
        }
      });
      
      //
      // Movie Selector Code
      //
      
      var numToPick = 5;
      
      var movie_list = [];
      <?php
      while($movie = $movies->fetchObject()) {
        echo "movie_list.push('".addslashes($movie->movie_title)."');";
      }
      ?>
      movie_list.sort(function() {return 0.5 - Math.random()})
      var selected = [];
      var i = 0;
      
      function show_movies(index, number) {
        $('#movies').html('');
        for (var j=index;j<index+number;j++) {
          if (j < movie_list.length) {
            mname = movie_list[j];
            var nl = $('<input type=\"button\" class=\"movie movie_hov\" />').val(mname).appendTo($('#movies'));    
            if (mname in oc(selected)) {
              nl.removeClass('movie_hov').attr('disabled','disabled');
            }       
          }
        }
      }
      
      show_movies(0, 4);

      $('#see_more').click(function(){
        if (i+4 > movie_list.length) {
          i = -4;
        }
        i = (i+4) % movie_list.length;
        show_movies(i, 4);
      });
      
      $('.movie').live('click', function(){
        mname = $(this).val();
        if(!(mname in oc(selected))){
          $(this).removeClass('movie_hov').attr('disabled','disabled');
          selected.push(mname);
          finished_selecting();
        }
      });
      
      function finished_selecting() {
        numToPick--;
        $('#numleft').text(numToPick+' more movies');
        if(numToPick == 1) {
          $('#numleft').text('1 more movie')
        }
        if (numToPick == 0) {
          $('#movie_selector').hide();
          $('#loading').show();
          $.get('get_movie_quotes.php', {gid: <?php echo $group_id ?>, 'movies[]': selected},
            function(data) {
              $('#loading').hide();
              $('#questions').prepend(data);
              $('.question').hide();
              $('.question:eq('+n+')').show();
              $('#questions').show();
            }
          );
        }
      }
      
    });
  </script>
  <link rel="stylesheet" href="default.css" />
</head>

<form name="hello" action="http://www.mturk.com/mturk/externalSubmit" method="POST">

<input type="hidden" name="assignmentId" value="<?php echo $_GET['assignmentId'] ?>" />
<input type="hidden" name="groupId" value="<?php echo $group_id ?>" />

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