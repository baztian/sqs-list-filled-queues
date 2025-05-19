#!/usr/bin/env python3
import boto3
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import select
import sys
import termios
import tty
import argparse

# Initialize boto3 client
sqs = boto3.client('sqs')

def check_queue(queue_url):
    # Get the approximate number of messages in the queue
    try:
        response = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['ApproximateNumberOfMessages']
        )
    except sqs.exceptions.QueueDoesNotExist:
        # Ignore the queue if it does not exist
        return
    message_count = int(response['Attributes']['ApproximateNumberOfMessages'])

    if message_count:
        return (message_count, queue_url)

# ANSI escape codes for styles
BOLD = "\033[1m"
GREEN = "\033[92m"
RESET = "\033[0m"

def display_results(results):
    session = boto3.session.Session()
    current_region = session.region_name
    console_link = f"https://console.aws.amazon.com/sqs/v2/home?region={current_region}"
    displayable_results = [
        (queue_url.split('/')[-1], message_count, f"{console_link}#/queues/{urllib.parse.quote(queue_url, safe='')}")
        for message_count, queue_url in results
    ]
    sorted_display_results = sorted(displayable_results, key=lambda x: (-x[1], x[0]))
    clear_line()
    if results:
        max_base_name_length = max(len(result[0]) for result in sorted_display_results)
        max_message_count_length = len(str(max(result[1] for result in sorted_display_results)))
        for base_name, message_count, console_link in sorted_display_results:
            display_name = base_name.ljust(max_base_name_length)
            display_count = str(message_count).rjust(max_message_count_length)
            print(f"{BOLD}{display_name}{RESET}: {GREEN}{display_count} msgs{RESET}\n    {console_link}")
    else:
        print(f"{BOLD}No messages found in any queue.{RESET}")

def clear_line():
    print("\r" + " " * 60, end='\r')

def get_queue_infos(queue_urls, workers):
    total_queues = len(queue_urls)
    results = []
    # Use ThreadPoolExecutor to check queues in parallel
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(check_queue, url) for url in queue_urls]
        processed_queues = 0
        for future in as_completed(futures):
            processed_queues += 1
            print(f"\rProcessed {BOLD}{processed_queues}{RESET} out of {BOLD}{total_queues}{RESET} queues...", end='', flush=True)
            result = future.result()
            if result:  # Ensure the queue had more than 1 message
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

def main():
    parser = argparse.ArgumentParser(description="List SQS queues that have at least one message and update periodically.")
    parser.add_argument('-w', '--watch', nargs="?", const=60, type=int, metavar='n',
                        help="Update every [n] seconds. Default is 60 seconds if no value is provided.")
    parser.add_argument('-t', '--workers', type=int, default=4, help="Number of thread workers for fetching queue info. Default is 4.")
    args = parser.parse_args()

    try:
        print("Reading list of queues...", end='', flush=True)
        # List all queues
        response = sqs.list_queues()
        queue_urls = response.get('QueueUrls', [])
        if args.watch is None:
            results = get_queue_infos(queue_urls, args.workers)
            display_results(results)
            return
        while True:
            results = get_queue_infos(queue_urls, args.workers)
            os.system('clear' if os.name == 'posix' else 'cls')  # Clear the console
            display_results(results)
            if countdown(args.watch):
                continue
    except KeyboardInterrupt:
        clear_line()
        quit()

if __name__ == "__main__":
    main()