Find the difference in # of results between quotes with/without movie title
---------------------------------------------------------------------------
SELECT q1.movie, q1.actor, q1.quote, (q1.result - q2.result) as meow from quotes q1, quotes q2 WHERE q1.query_type = 'plain' and q2.query_type = 'with_movie' and q1.quote = q2.quote and q1.actor = q2.actor

SELECT q1.movie, q1.actor, q1.quote, q1.result, q2.result as result_with_movie, (q1.result - q2.result) as diff from quotes q1, quotes q2 WHERE q1.query_type = 'plain' and q2.query_type = 'with_movie' and q1.quote = q2.quote and q1.actor = q2.actor AND q1.result > 100 AND diff > 0 AND q1.result / q2.result < 10 AND diff < 1000000

SELECT q1.movie, q1.actor, q1.quote, q1.result, q2.result as result_with_movie, (q1.result / q2.result) as ratio from quotes q1, quotes q2 WHERE q1.query_type = 'plain' and q2.query_type = 'with_movie' and q1.quote = q2.quote and q1.actor = q2.actor AND q1.result > 100 AND (q1.result - q2.result) > 0 AND q1.result / q2.result < 3 AND (q1.result - q2.result) < 1000000 AND length(q1.quote) > 10