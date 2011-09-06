Find the difference in # of results between quotes with/without movie title
---------------------------------------------------------------------------
SELECT q1.movie, q1.actor, q1.quote, (q1.result - q2.result) as meow from quotes q1, quotes q2 WHERE q1.query_type = 'plain' and q2.query_type = 'with_movie' and q1.quote = q2.quote and q1.actor = q2.actor