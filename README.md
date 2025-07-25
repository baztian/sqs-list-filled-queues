# SQS List Filled Queues

A Python script that lists Amazon SQS queues containing messages and updates the display periodically. This tool leverages the `boto3` library to interact with AWS SQS, making it easy to monitor your message queues.

## Features

- Lists all SQS queues with at least one message.
- Displays the number of messages in each queue.
- Optionally includes messages in flight (being processed) in the count.
- Filters queues by name using regex patterns.
- Provides direct links to the AWS SQS console for each queue.
- Supports periodic updates to refresh the displayed information.
- Configurable number of worker threads for fetching queue information.
- Exits with error code 1 when messages are found (useful for monitoring/alerting).

## Prerequisites

- Python 3.x
- AWS credentials configured (via environment variables, AWS config file, or IAM roles).

## Usage

You can run the script directly from the command line. Here are some usage examples:

- To list queues and display results once:

   sqs-list-filled-queues

- To include messages in flight (being processed):

   sqs-list-filled-queues --include-in-flight

- To watch the queues and refresh every 60 seconds:

   sqs-list-filled-queues --watch

- To specify a custom refresh interval (e.g., 30 seconds):

   sqs-list-filled-queues --watch 30

- To adjust the number of worker threads (e.g., 8):

   sqs-list-filled-queues --workers 8

- To filter queues by name pattern (case-insensitive regex):

   sqs-list-filled-queues --pattern "prod"
   sqs-list-filled-queues --pattern "^test-"
   sqs-list-filled-queues --pattern "queue$"

- To combine options (watch with in-flight messages and pattern filtering):

   sqs-list-filled-queues --watch 30 --include-in-flight --pattern "production"

### Exit Codes

- **0**: No messages found in any queue
- **1**: At least one message found in one or more queues (useful for monitoring/alerting)

### Controls During Watching

- Press `R` to force a refresh.
- Press `Q` to quit the program.

### Pattern Filtering

The `--pattern` option allows you to filter queues by name using regular expressions. The pattern is applied to the queue name only (not the full URL) and is case-insensitive.

Examples:

- `--pattern "test"` - matches queues containing "test" anywhere in the name
- `--pattern "^prod-"` - matches queues starting with "prod-"
- `--pattern "queue$"` - matches queues ending with "queue"
- `--pattern "(dev|test|staging)"` - matches queues containing "dev", "test", or "staging"

## Example Output

### Without in-flight messages

    Reading list of queues...Processed 5 out of 10 queues...
    QueueName1: 12 msgs
        https://console.aws.amazon.com/sqs/v2/home?region=us-west-2#/queues/QueueName1
    QueueName2: 5 msgs
        https://console.aws.amazon.com/sqs/v2/home?region=us-west-2#/queues/QueueName2

### With in-flight messages (--include-in-flight)

    Reading list of queues...Processed 5 out of 10 queues...
    QueueName1: 12 msgs, 3 in-flight, 15 total
        https://console.aws.amazon.com/sqs/v2/home?region=us-west-2#/queues/QueueName1
    QueueName2:  5 msgs, 0 in-flight,  5 total
        https://console.aws.amazon.com/sqs/v2/home?region=us-west-2#/queues/QueueName2

### With pattern filtering (--pattern "prod")

    Reading list of queues...Filtered 10 queues to 3 matching pattern 'prod'
    Processed 3 out of 3 queues...
    production-queue: 25 msgs
        https://console.aws.amazon.com/sqs/v2/home?region=us-west-2#/queues/production-queue
    user-actions-prod:  8 msgs
        https://console.aws.amazon.com/sqs/v2/home?region=us-west-2#/queues/user-actions-prod

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
