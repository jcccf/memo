<?php
$group_id = htmlentities($_GET['gid']);
?>
<!DOCTYPE html>
<html>
<head>
  
  <title>MTurk HIT</title>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js"></script>
  <script>
    $.fn.serializeObject = function()
    {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };
  
    function shuffle(array) {
        var tmp, current, top = array.length;

        if(top) while(--top) {
            current = Math.floor(Math.random() * (top + 1));
            tmp = array[current];
            array[current] = array[top];
            array[top] = tmp;
        }

        return array;
    }
  
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
      $('#questions_wrapper').hide();
      $('#next_final').hide();
      
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
          $('#next_final').show();
        }
      });
      
      //
      // Movie Selector Code
      //
      
      var numToPick = 5;
      var movie_list = [];
      var selected = [];
      var i = 0;
      
      $.getJSON('get_movies.php', {group_id: <?php echo $group_id ?>}, function(data) {
        movie_list = data;
        show_movies(0, 4);
      });
      
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
          load_data();
        }
      }
      
      function show_instructions() {
        $('#movie_selector').hide();
        $('#instructions').show();
      }
      
      $('#start_questions').click(function(){
        $('#instructions').hide();
        $('.question').hide();
        $('.question:eq('+n+')').show();
        $('#questions_wrapper').show();
      });
      
      $('#next_final').click(function() {
        $('#next_final').hide();
        $('.question').hide();
        $('#final_instructions').show();
      });
      
      $('#submit').click(function() {
        $.ajax({
          url: 'store_results.php',
          data: { worker_id: '<?php echo $_GET['workerId'] ?>', json: JSON.stringify($('form').serializeObject()) },
          async: false,
          success: function(data) {
            //alert(data);
          }
        });
        return true;
      });
      
      function load_data() {
        $('#loading').show();
        $.getJSON('get_movie_quotes.php', {gid: <?php echo $group_id ?>, 'movies[]': selected},
          function(data) {
            function build_question(movie_title, quote_1, quote_2, quote_id, i) {
              var text = [
                '<div class="question">Q'+(i+1),
                '<div class="qmovie">From <b>'+movie_title+'</b></div>',
                '<div class="quote"><div class="num">1</div>'+quote_1+'</div>',
                '<div class="quote"><div class="num">2</div>'+quote_2+'</div>',
                '<div class="qoption">',
                '<label><input type="radio" name="q'+i+'" value="Q1" /><b>Only the first quote</b> is memorable.</label>',
                '</div>',
                '<div class="qoption">',
                '<label><input type="radio" name="q'+i+'" value="Q2" /><b>Only the second quote</b> is memorable.</label>',
                '</div>',
                '<div class="qoption">',
                '<label><input type="radio" name="q'+i+'" value="B" /><b>Both quotes</b> are memorable.</label>',
                '</div>',
                '<div class="qoption">',
                '<label><input type="radio" name="q'+i+'" value="N" /><b>Neither quote</b> is memorable.</label>',
                '<input type="hidden" name="q'+i+'_id" value="'+quote_id+'" />',
                '</div>',
                '</div>'
              ].join('');
              $('#questions').append(text);
            }
            $.each(data.q, function(i,question) {
              build_question(question.m, question.q1, question.q2, question.qid, i);
            });
            
            var before = [];
            var after = [];
            $.each(data.m.c, function(i,quote){
              before.push(quote);
              after.push(quote);
            });
            $.each(data.m.nc, function(i,quote) {
              if (i < 2) {
                before.push(quote);
              }
              else {
                after.push(quote);
              }
            });
            shuffle(before);
            shuffle(after);
            $.each(before, function(i,quote) {
              $('#instructions_quotes').append('<div class="quote">'+quote.q+'</div>');
            });
            $.each(after, function(i,quote) {
              $('#final_instructions_quotes_2').append('<div class="quote"><div class="num">'+(i+1)+'</div>'+quote.q+'</div>');
              $('#final_instructions_quotes_2').append('<input type="hidden" name="rec'+(i+1)+'" value="'+quote.id+'" />');
            });
            
            $('#loading').hide();
            
            show_instructions();
          }
        );
      }
      
    });
  </script>
  <link rel="stylesheet" href="default.css" />
</head>

<body>

<?php if ($_GET['assignmentId'] == 'ASSIGNMENT_ID_NOT_AVAILABLE') {  ?>
  
<div class="container">
<img src="question_sample.png" />
</div>

<?php } else { ?>

<form name="hello" action=" http://www.mturk.com/mturk/externalSubmit" method="POST">
<input type="hidden" name="assignmentId" value="<?php echo $_GET['assignmentId'] ?>" />
<!-- <input type="hidden" name="groupId" value="<?php echo $group_id ?>" /> -->

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

<div id="instructions">
  <h1>Instructions</h1>
  <br />
  You will be asked to evaluate how memorable quotes are. <br /><br />
  Here are some examples of quotes that you will be asked to evaluate:<br />
  <div id="instructions_quotes">
  </div>
  <input type="button" id="start_questions" value="Start" />
</div>

<div id="final_instructions">
  <h1>Finally,</h1>
  <br />
  Do you recall whether any of these quotes were previously shown? <br />
  <div id="final_instructions_quotes">
    <div id="final_instructions_quotes_2"></div>
    <label><input type="checkbox" name="rec[]" value="1" /> I remember the <b>1<sup>st</sup></b> quote.</label>
    <label><input type="checkbox" name="rec[]" value="2" /> I remember the <b>2<sup>nd</sup></b> quote.</label>
    <label><input type="checkbox" name="rec[]" value="3" /> I remember the <b>3<sup>rd</sup></b> quote.</label>
    <label><input type="checkbox" name="rec[]" value="4" /> I remember the <b>4<sup>th</sup></b> quote.</label>
  </div>
  
  <input type="submit" id="submit" value="Submit HIT" />
  
</div>

<div id="questions_wrapper">
<div id="questions">
</div>
<input type="button" id="next" value="Next Question" />
<input type="button" id="next_final" value="Final Question" />
</div>

</div>

</div>

</form>

<?php } ?>

</body>
</html>