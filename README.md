## Description
End to end feature I developed for a start-up which automates the task of importing new listings from other real estate platform. The feature reduces the time needed to manually insert household specification and encourages real estate agencies to transition to the new platform.

### Architecture
![](https://raw.githubusercontent.com/bogdancucu/imobiliare-scraper-v2/main/png/project-diagram.png)

### The logic
1. URLs of listings to be scraped are fed to the app through a queue messaging system (SQS);
2. every 10 minutes, a crontab triggers sqs_main_queue.py script; 
3. the script checks if there are messages on the queue, then proceeds to retrieve them;
4. retrieved urls are passed onto the crawler, which scrapes the desired data and dumps it into an S3 bucket;
5. if any error occurs during the process, the message is sent to a dead letter queue, for later retrieval;
6. another crontab triggers, every 6 hours, sqs_dead_letter_queue.py, which checks if there are any messages on the dead letter queue, then proceeds to notify AWS user about this, through an SNS Topic *(feature yet to be implemented)*;

### Tools
- Python (Scrapy framework)
- AWS (S3, SQS, boto3)
- Docker
- Linux crontab

### Further improvements
*(depending on clients requirements)*
- automating the insertion of output data from the S3 bucket to the database;
- implementing the SNS Topic;
- scraping additional data;
- data cleaning and normalization; 