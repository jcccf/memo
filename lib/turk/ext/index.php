<?php
$group_id = htmlentities($_GET['gid']);
require_once('config.php');
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
        
        function continueThis() {
          $('.question:eq('+n+')').hide();
          n++;
          if ($('.question:eq('+n+')').length > 0) {
            $('.question:eq('+n+')').show();
          }
          if ($('.question:eq('+(n+1)+')').length == 0) {
            $('#next').hide();
            $('#next_final').show();
          }
        }
        
        var corr = '1';
        var corr_oth = '2';
        if ($('input[name=q'+n+'_sw]').val() == '1') {
          corr = '2';
          corr_oth = '1';
        }
        if ($('input[name=q'+n+']:checked').val() != corr) {
          $('input[name=q'+n+'][value='+corr_oth+']').parent().animate({color: 'red'}, 300);
          num_incorrect++;
        }
        $('input[name=q'+n+'][value='+corr+']').parent().animate({color: 'green'}, 300).delay(600).queue(continueThis);
      });
      
      $('#next_final').click(function() {
        var corr = '1';
        var corr_oth = '2';
        if ($('input[name=q'+n+'_sw]').val() == '1') {
          corr = '2';
          corr_oth = '1';
        }
        if ($('input[name=q'+n+']:checked').val() != corr) {
          $('input[name=q'+n+'][value='+corr_oth+']').parent().animate({color: 'red'}, 300);
          num_incorrect++;
        }
        $('input[name=q'+n+'][value='+corr+']').parent().animate({color: 'green'}, 300).delay(600).queue(function() {
          $('#next_final').hide();
          $('.question').hide();
          $('#final_instructions').show();
        });
      });
      
      $('#next_comments').click(function() {
        var someRed = false;
        for (var k=1; k<5; k++) {
          if (!$('input[name=rec'+k+'c]:checked').val()) {
            $('input[name=rec'+k+'c]').each(function(){
              $(this).parent().animate({color: 'red'}, 300);
            });
            someRed = true;
          }
        }
        if (someRed) {
          return false;
        }
        $('#final_instructions').hide();
        $('#comments').show();
        $('#num_correct').html(num_total-num_incorrect + ' out of ' + num_total);
      });
      
      $('#submit').click(function() {
        $.ajax({
          url: 'store_results.php',
          data: { worker_id: '<?php echo $_GET['workerId'] ?>', json: JSON.stringify($('form').serializeObject()) },
          async: false,
          type: "POST",
          success: function(data) {
            $('#submit').val('Submitted! Thanks for your time!').attr('disabled','disabled');
          }
        });
        $('#comments').hide();
        $('#post_submit').show();
        return false;
      });
      
      //
      // Hello World Code
      //
      
      $('#hello_continue').click(function(){ 
        $('#hello_there').hide();
        $('#movie_selector').show();
        $('#your_name').html($('#name').val());
      });
      
      //
      // Movie Selector Code
      //

      var movie_list = [];
      var selected_yes = [];
      var selected_no = [];
      var selected_np = 0;
      var i = 0;
      var num_incorrect = 0;
      var num_total = 0;
      
      $.post('get_movies.php', {group_id: <?php echo $group_id ?>}, function(data) {
        movie_list = data;
        show_next_movie();
      }, 'json');
      
      function show_next_movie() {
        if (selected_yes.length >= <?php echo MIN_SEEN ?> && selected_no.length >= <?php echo MIN_UNSEEN ?>) {
          load_data();
        }
        else {
          if (<?php echo MIN_SEEN ?> - selected_yes.length <= 2 && <?php echo MIN_UNSEEN ?> - selected_no.length <= 2) {
            $('.info .extra').show();
          }
          $('#movie_name').html(movie_list[i++]);
        }
      }
      
      $('#movie_yes').click(function() {
        selected_yes.push(movie_list[i-1]);
        show_next_movie();
      });
      
      $('#movie_no').click(function() {
        if (i % 5 != 0) {
          selected_no.push(movie_list[i-1]);
        }
        show_next_movie();
      });
      
      //
      // Instructions Code
      //
      
      function show_instructions() {
        $('#movie_selector').hide();
        $('.container').addClass('highlight');
        $('#instructions').show();
      }
      
      $('#recb').keypress(function(e) {
        if (e.which == 13) { // Prevent enter key from submitting
          return false;
        }
        $('#inst_questions').show();
      });
      
      $('#inst_questions').click(function() {
        if (!((parseInt($("#recb").val()) <= 4 && parseInt($("#recb").val()) >= 1 ) || $("#recb").val() == '0')) {
          alert("Sorry, but you entered an invalid entry and cannot proceed. Thank you for your time!");
          $('#submit').click();
        }
        $('#instructions').hide();
        $('.container').removeClass('highlight');
        $('#question_instructions').show();
      });
      
      $('#inst_questions').hide();
      
      $('#start_questions').click(function(){
        $('#question_instructions').hide();
        $('.question').hide();
        $('.question:eq('+n+')').show();
        $('#questions_wrapper').show();
      });
      
      //
      // Load Data
      //
      
      function load_data() {
        $('#movie_selector').hide();
        $('#loading').show();
        $.post('get_movie_quotes.php', {gid: <?php echo $group_id ?>, 'movies[]': selected_yes, 'unseen[]': selected_no}, function(data) {
          function build_question(movie_title, quote_1, quote_2, quote_id, i, swapped, seen) {
            var text = [
              '<div class="question">Question '+(i+1)+' out of <?php echo QUESTION_LIMIT ?>',
              '<div class="qmovie">Here are two quotes from <b>'+movie_title+'</b>. Which of these quotes seems more memorable?</div>',
              '<div class="quote"><div class="num">1</div>'+quote_1+'</div>',
              '<div class="quote"><div class="num">2</div>'+quote_2+'</div>',
              '<div class="qoptions">',
              '<div class="qoption">',
              '<label><input type="radio" name="q'+i+'" value="1" />The <b>first quote</b> seems more memorable.</label>',
              '</div>',
              '<div class="qoption">',
              '<label><input type="radio" name="q'+i+'" value="2" />The <b>second quote</b> seems more memorable.</label>',
              '</div>',
              '<input type="hidden" name="q'+i+'_id" value="'+quote_id+'" />',
              '<input type="hidden" name="q'+i+'_sw" value="'+swapped+'" />',
              '<input type="hidden" name="q'+i+'_s" value="'+seen+'" />',
              '</div></div>'
            ].join('');
            $('#questions').append(text);
          }
          data.q = shuffle(data.q);
          num_total = <?php echo QUESTION_LIMIT ?>; //data.q.length;
          $.each(data.q, function(i,question) {
            if(i < <?php echo QUESTION_LIMIT ?>) {
              if (Math.random() < 0.5) {
                build_question(question.m, question.q1, question.q2, question.qid, i, 0, question.s);
              }
              else {
                build_question(question.m, question.q2, question.q1, question.qid, i, 1, question.s);
              }
            }
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
          before = shuffle(before);
          after = shuffle(after);
          // alert(JSON.stringify(before));
          // alert(JSON.stringify(after));
          $.each(before, function(i,quote) {
            $('#instructions_quotes').append('<div class="quote">'+quote.q+'</div>');
          });
          $.each(after, function(i,quote) {
            $('#final_instructions_quotes_2').append('<div class="quote"><div class="num">'+(i+1)+'</div>'+quote.q+'</div>');
            $('#final_instructions_quotes_2').append('<input type="hidden" name="rec'+(i+1)+'" value="'+quote.id+'" />');
          });
          
          $('#loading').hide();
          
          show_instructions();
        }, "json");
      }
      
    });
  </script>
  <link rel="stylesheet" href="default.css" />
</head>

<body>

<?php if ($_GET['assignmentId'] == 'ASSIGNMENT_ID_NOT_AVAILABLE') {  ?>
  
<div class="container">
<div class="infoheader">This task is for native English speakers only.</div>
<div class="infoheader">If you use Internet Explorer, click "NO" if you see this box.</div><img src="ie_warning.png" />
<div class="infoheader">Here's a sample question.</div><img src="question_sample.png" />
</div>

<?php } else { ?>

<form name="hello" action=" http://www.mturk.com/mturk/externalSubmit" method="POST">
<input type="hidden" name="assignmentId" value="<?php echo $_GET['assignmentId'] ?>" />
<!-- <input type="hidden" name="groupId" value="<?php echo $group_id ?>" /> -->

<div class="container">
	
<div id="hello_there">
	<h1>Hi there! What's your name?</h1><br /><br />
	<input type="text" name="name" id="name" placeholder="Type in here!" size="20" /><br /><br /><br />
	<input type="button" id="hello_continue" value="Continue" />
</div>

<div id="movie_selector">
<div class="info">Hi! <span id="your_name"></span>! For this study, we'll first need to find out the names of a few movies you've seen and a few you haven't seen. <span class="extra">Hang in there! You're almost done!</span></div>
<h2>Have you seen...</h2>
<div id="movies">
  <span id="movie_name"></span>&nbsp;<span class="smaller"></span>
</div>
<div style="clear: both">
<input type="button" id="movie_yes" value="Yes, I've seen it" /> &nbsp;
<input type="button" id="movie_no" value="No, haven't seen it" />
</div>
</div>

<div id="loading">
  <h1>Loading Movie Quotes...</h1>
</div>

<div id="instructions">
  <div style="text-align: left">
  <h1>Warm-up Question</h1>
  <br />
  Here are some examples of movie quotes. <b>Please read them carefully now.</b><br />
  </div>
  <div id="instructions_quotes">
  </div>
  <div style="text-align: left">
  How many of these quotes seem familiar to you? (Enter a number from 0 to 4, inclusive.)
  <input type="text" id="recb" name="recb" size="1" maxlength="1" placeholder="?" /> <br /><br />
  </div>
  
  <input type="button" id="inst_questions" value="Continue" />
  
</div>

<div id="question_instructions">
  <div style="text-align: left">
  <h1>Instructions</h1>
  <br />
  Next, you'll be asked to compare 15 pairs of quotes from movies you haven't seen, and determine which is more memorable. The first three questions are warm-up questions, and do not count in our experiments.
  
  <br /><br />At times, it might seem like neither quote is memorable, or that both seem equally memorable. However, please keep in mind that these quotes have already been annotated by humans, and one is indeed more memorable than the other. Do your best to 'recover' those existing labels! 
  
  <br /><br />After answering each question you will get instant feedback on whether your answer was correct (indicated with green) or incorrect (indicated with red).
  
  <br /><br />This is not an easy task, and it might take a couple of minutes to answer each question.
  
  <br /><br />A memorable quote could have one or more of the following characteristics:
  <ul>
    <li>The quote is likely to be remembered by people who saw the movie.</li>
    <li>The quote might be used by people who saw the movie.</li>
    <li>The quote could be used out-of-context, perhaps as a reference to the movie it came from.</li>
    <li>The quote could be catchy.</li>
  </ul>
  
  <br /><br />You should use your intuition in deciding what makes a quote sound more memorable, and the first three warm-up questions are there to help you "calibrate" it. But remember, <b>your task is to recover as many labels as you can</b>.
  
  <br /><br />Do not look <b>anything</b> up on the web while completing this task.
  
  <br /><br />Some of these quotes might contain offensive content. We are sorry about that.<br /><br />
  </div>
  
  <input type="button" id="start_questions" value="Start" />
</div>

<div id="final_instructions">
  <h1>Finally,</h1>
  <br />
  Do you recall any number of the quotes below from the warm-up question (from the yellow page)? <br />
  <div id="final_instructions_quotes">
    <div id="final_instructions_quotes_2"></div>
    <div class="qoptions last">
    <div class="qoption"><div class="right"><label><input type="radio" name="rec1c" value="1" /> Yes &nbsp;</label> &nbsp; <label><input type="radio" name="rec1c" value="0" /> No &nbsp;</label></div> I remember the <b>1st</b> quote.</div>
    <div class="qoption"><div class="right"><label><input type="radio" name="rec2c" value="1" /> Yes &nbsp;</label> &nbsp; <label><input type="radio" name="rec2c" value="0" /> No &nbsp;</label></div> I remember the <b>2nd</b> quote.</div>
    <div class="qoption"><div class="right"><label><input type="radio" name="rec3c" value="1" /> Yes &nbsp;</label> &nbsp; <label><input type="radio" name="rec3c" value="0" /> No &nbsp;</label></div> I remember the <b>3rd</b> quote.</div>
    <div class="qoption"><div class="right"><label><input type="radio" name="rec4c" value="1" /> Yes &nbsp;</label> &nbsp; <label><input type="radio" name="rec4c" value="0" /> No &nbsp;</label></div> I remember the <b>4th</b> quote.</div>
    </div>
  </div>
  
  <input type="button" id="next_comments" value="Almost Done!" />
  
</div>

<div id="comments">
  <br /><br />
  Now that you've completed these ten questions, what do you think is the best way to describe a memorable quote?
  <textarea name="memorable_box"></textarea>
  
  <br /><br />
  
  If you found any questions that were confusing, please note it down here.<br />
  
  <textarea name="comments_box"></textarea>
  
  <br />
  
  <input type="submit" id="submit" value="Submit" />
</div>

<div id="post_submit">
  <h1>Thanks for participating!</h1>
  <br />
  <h2>You got <span id="num_correct"></span> correct!</h2>
  (The very last question wasn't counted.)
  <br /><br />
  <!--
  <a href="https://twitter.com/share" class="twitter-share-button" data-url="http://memo.clr3.com/?gid=1" data-text="How good are you at identifying memorable quotes?" data-lang="en" data-size="large">Tweet</a>
  <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script>
  -->
  
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