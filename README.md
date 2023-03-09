## Description
Feature I build for a start-up which extracts household specification from imobiliare.ro real estate listings and dumps them in an S3 bucket.  
Listing URLs are provided through a queue messaging system (SQS). Using a crontab, the script checks if there is any new message in the queue every 10 minutes, then proceeds to process it.  
Deployed using Docker.