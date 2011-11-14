Find the difference in # of results between quotes with/without movie title
---------------------------------------------------------------------------
SELECT q1.movie, q1.actor, q1.quote, (q1.result - q2.result) as meow from quotes q1, quotes q2 WHERE q1.query_type = 'plain' and q2.query_type = 'with_movie' and q1.quote = q2.quote and q1.actor = q2.actor

SELECT q1.movie, q1.actor, q1.quote, q1.result, q2.result as result_with_movie, (q1.result - q2.result) as diff from quotes q1, quotes q2 WHERE q1.query_type = 'plain' and q2.query_type = 'with_movie' and q1.quote = q2.quote and q1.actor = q2.actor AND q1.result > 100 AND diff > 0 AND q1.result / q2.result < 10 AND diff < 1000000

SELECT q1.movie, q1.actor, q1.quote, q1.result, q2.result as result_with_movie, (q1.result / q2.result) as ratio from quotes q1, quotes q2 WHERE q1.query_type = 'plain' and q2.query_type = 'with_movie' and q1.quote = q2.quote and q1.actor = q2.actor AND q1.result > 100 AND (q1.result - q2.result) > 0 AND q1.result / q2.result < 3 AND (q1.result - q2.result) < 1000000 AND length(q1.quote) > 10

SELECT q1.movie, q1.actor, q1.quote, q1.result, q2.result, (q2.result/cast(q1.result as float)) as ratio from quotes q1, quotes q2 WHERE q1.query_type = 'plain' and q2.query_type = 'movie_title' and q1.quote = q2.quote and q1.actor = q2.actor



SELECT q1.quote, q1.result, q2.result FROM quotes AS q1, quotes AS q2  WHERE q1.movie = q2.movie AND q1.quote = q2.quote AND q1.query_type=\'plain\' AND q2.query_type=\'movie_title\' AND q1.quote_type=\'full\' AND q2.quote_type=\'full\' ORDER BY q1.id ASC

SELECT quote, min(result) FROM quotes WHERE quote_type='full' GROUP BY quote, movie ORDER BY id asc




SELECT q.movie_name, q.actor, q.is_memorable, q.result, q2.result as result2, q.quote FROM quotes q, quotes q2 WHERE q.query_type='movie_title' AND q2.query_type='plain' AND q.quote_type='full' AND q2.quote_type='full' ORDER BY q.id ASC LIMIT 10

SELECT * FROM quotes WHERE movie_name='a few good men' AND query_type='movie_title' AND is_memorable=1 ORDER BY result_fixed DESC