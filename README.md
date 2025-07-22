# SQS List Filled Queues

A Python script that lists Amazon SQS queues containing messages and updates the display periodically. This tool leverages the `boto3` library to interact with AWS SQS, making it easy to monitor your message queues.

## Features

- Lists all SQS queues with at least one message.
- Displays the number of messages in each queue.
- Optionally includes messages in flight (being processed) in the count.
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

- To combine options (watch with in-flight messages):

   sqs-list-filled-queues --watch 30 --include-in-flight

### Exit Codes

- **0**: No messages found in any queue
- **1**: At least one message found in one or more queues (useful for monitoring/alerting)

### Controls During Watching

- Press `R` to force a refresh.
- Press `Q` to quit the program.

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
