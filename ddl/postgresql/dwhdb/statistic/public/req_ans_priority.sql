create view req_ans_priority
            (id, answer_time, username, request, ans_docs, ans_percents, max_percent, min_percent, average_percent,
             subscription) as
SELECT articles_requests_statistic.id,
       articles_requests_statistic.answer_time,
       articles_requests_statistic.username,
       articles_requests_statistic.request,
       articles_requests_statistic.ans_docs,
       articles_requests_statistic.ans_percents,
       articles_requests_statistic.max_percent,
       articles_requests_statistic.min_percent,
       articles_requests_statistic.average_percent,
       u.subscription
FROM articles_requests_statistic
         JOIN users u ON u.username = articles_requests_statistic.username;

