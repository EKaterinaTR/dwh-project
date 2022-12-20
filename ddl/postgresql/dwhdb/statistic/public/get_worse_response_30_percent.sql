create view get_worse_response_30_percent(request, id, max_percent, min_percent, average_percent, subscription) as
SELECT percent_rank_priority.request,
       percent_rank_priority.id,
       percent_rank_priority.max_percent,
       percent_rank_priority.min_percent,
       percent_rank_priority.average_percent,
       percent_rank_priority.subscription
FROM (SELECT req_ans_priority.request,
             req_ans_priority.max_percent,
             req_ans_priority.min_percent,
             req_ans_priority.average_percent,
             req_ans_priority.subscription,
             req_ans_priority.id,
             percent_rank()
             OVER (ORDER BY req_ans_priority.max_percent, req_ans_priority.min_percent, req_ans_priority.average_percent, req_ans_priority.subscription) AS per_r
      FROM req_ans_priority) percent_rank_priority
WHERE foo.per_r < 0.3;

