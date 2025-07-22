#!/usr/bin/env python3
import boto3
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import re
import select
import sys
import termios
import tty
import argparse

# Initialize boto3 client
sqs = boto3.client('sqs')

def check_queue(queue_url, include_in_flight=False):
    # Get the approximate number of messages in the queue
    try:
        attribute_names = ['ApproximateNumberOfMessages']
        if include_in_flight:
            attribute_names.append('ApproximateNumberOfMessagesNotVisible')

        response = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=attribute_names
        )
    except sqs.exceptions.QueueDoesNotExist:
        # Ignore the queue if it does not exist
        return

    message_count = int(response['Attributes']['ApproximateNumberOfMessages'])
    in_flight_count = 0
    if include_in_flight:
        in_flight_count = int(response['Attributes'].get('ApproximateNumberOfMessagesNotVisible', 0))

    total_count = message_count + in_flight_count

    if total_count:
        return (message_count, in_flight_count, queue_url)

# ANSI escape codes for styles
BOLD = "\033[1m"
GREEN = "\033[92m"
RESET = "\033[0m"

def display_results(results, include_in_flight=False):
    session = boto3.session.Session()
    current_region = session.region_name
    console_link = f"https://console.aws.amazon.com/sqs/v2/home?region={current_region}"

    displayable_results = []
    for result in results:
        message_count, in_flight_count, queue_url = result
        base_name = queue_url.split('/')[-1]
        link = f"{console_link}#/queues/{urllib.parse.quote(queue_url, safe='')}"
        total_count = message_count + in_flight_count
        displayable_results.append((base_name, message_count, in_flight_count, total_count, link))

    sorted_display_results = sorted(displayable_results, key=lambda x: (-x[3], x[0]))  # Sort by total count desc, then name
    clear_line()
    if results:
        max_base_name_length = max(len(result[0]) for result in sorted_display_results)
        max_message_count_length = len(str(max(result[1] for result in sorted_display_results)))
        max_in_flight_length = len(str(max(result[2] for result in sorted_display_results))) if include_in_flight else 0
        max_total_length = len(str(max(result[3] for result in sorted_display_results)))

        for base_name, message_count, in_flight_count, total_count, console_link in sorted_display_results:
            display_name = base_name.ljust(max_base_name_length)
            display_count = str(message_count).rjust(max_message_count_length)

            if include_in_flight:
                display_in_flight = str(in_flight_count).rjust(max_in_flight_length)
                display_total = str(total_count).rjust(max_total_length)
                print(f"{BOLD}{display_name}{RESET}: {GREEN}{display_count} msgs{RESET}, {GREEN}{display_in_flight} in-flight{RESET}, {GREEN}{display_total} total{RESET}\n    {console_link}")
            else:
                print(f"{BOLD}{display_name}{RESET}: {GREEN}{display_count} msgs{RESET}\n    {console_link}")
    else:
        print(f"{BOLD}No messages found in any queue.{RESET}")

def clear_line():
    print("\r" + " " * 60, end='\r')

def get_queue_infos(queue_urls, workers, include_in_flight=False):
    total_queues = len(queue_urls)
    results = []
    # Use ThreadPoolExecutor to check queues in parallel
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(check_queue, url, include_in_flight) for url in queue_urls]
        processed_queues = 0
        for future in as_completed(futures):
            processed_queues += 1
            print(f"\rProcessed {BOLD}{processed_queues}{RESET} out of {BOLD}{total_queues}{RESET} queues...", end='', flush=True)
            result = future.result()
            if result:  # Ensure the queue had more than 0 messages (including in-flight)
                results.append(result)
    return results

def countdown(duration):
    original_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    duration_len = len(str(duration))
    try:
        for i in range(duration, 0, -1):
            print(f"\rRefresh in {str(i).rjust(duration_len)} seconds (press 'R' to force refresh)", end='', flush=True)
            # time.sleep(1)
            rlist, _, _ = select.select([sys.stdin], [], [], 1)
            if rlist:
                key = sys.stdin.read(1).lower()
                clear_line()
                if key == 'r':
                    return True
                elif key == 'q':
                    quit()
            else:
                # No input, continue countdown
                continue
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)
    return False

def quit():
    print(f"{BOLD}{GREEN}Program terminated by user.{RESET}")
    sys.exit(0)

def filter_queues_by_pattern(queue_urls, pattern):
    """Filter queue URLs by regex pattern applied to queue names."""
    if not pattern:
        return queue_urls

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        print(f"Error: Invalid regex pattern '{pattern}': {e}")
        sys.exit(1)

    filtered_urls = []
    for url in queue_urls:
        queue_name = url.split('/')[-1]  # Extract queue name from URL
        if regex.search(queue_name):
            filtered_urls.append(url)

    return filtered_urls

def main():
    parser = argparse.ArgumentParser(description="List SQS queues that have at least one message and update periodically.")
    parser.add_argument('-w', '--watch', nargs="?", const=60, type=int, metavar='n',
                        help="Update every [n] seconds. Default is 60 seconds if no value is provided.")
    parser.add_argument('-t', '--workers', type=int, default=4, help="Number of thread workers for fetching queue info. Default is 4.")
    parser.add_argument('-f', '--include-in-flight', action='store_true',
                        help="Include messages in flight (being processed) in the count.")
    parser.add_argument('-p', '--pattern', type=str, metavar='REGEX',
                        help="Filter queues by name using a regex pattern (searches queue name, not full URL).")
    args = parser.parse_args()

    try:
        print("Reading list of queues...", end='', flush=True)
        # List all queues
        response = sqs.list_queues()
        queue_urls = response.get('QueueUrls', [])

        # Filter queues by pattern if provided
        if args.pattern:
            original_count = len(queue_urls)
            queue_urls = filter_queues_by_pattern(queue_urls, args.pattern)
            filtered_count = len(queue_urls)
            clear_line()
            print(f"Filtered {original_count} queues to {filtered_count} matching pattern '{args.pattern}'")

        if args.watch is None:
            results = get_queue_infos(queue_urls, args.workers, args.include_in_flight)
            display_results(results, args.include_in_flight)
            # Exit with error code 1 if any messages were found
            if results:
                sys.exit(1)
            return
        while True:
            results = get_queue_infos(queue_urls, args.workers, args.include_in_flight)
            os.system('clear' if os.name == 'posix' else 'cls')  # Clear the console
            display_results(results, args.include_in_flight)
            if countdown(args.watch):
                continue
    except KeyboardInterrupt:
        clear_line()
        quit()

if __name__ == "__main__":
    main()