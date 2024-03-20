import requests
import concurrent.futures
import time
import sys

# Redirect standard output to a file
original_stdout = sys.stdout
with open('test_load_details.txt', 'w') as f:
    sys.stdout = f

    # The URL of the endpoint you want to test
    url = 'https://bmjg67cbef.execute-api.eu-central-1.amazonaws.com/prod/docs/'

    # Function to make a single HTTP request
    def make_request():
        try:
            start_time = time.time()
            response = requests.get(url)  # You can change this to requests.post() if needed
            end_time = time.time()

            return {
                'status_code': response.status_code,
                'response_time': end_time - start_time
            }
        except Exception as e:
            return {
                'error': str(e)
            }

    # Number of requests you want to make (if negative, resort to time_limit)
    num_requests = 12000

    # Time limit for the load test (2 minutes)
    time_limit = 120

    # List to store response times and status codes
    responses = []

    # Record the start time of the load test
    start_time = time.time()

    # Use ThreadPoolExecutor to manage concurrent requests
    if num_requests > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            future_to_request = {executor.submit(make_request): i for i in range(num_requests)}
            for future in concurrent.futures.as_completed(future_to_request):
                response = future.result()
                responses.append(response)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            # Run the loop for time_limit
            while time.time() - start_time < time_limit:
                # Submit a new request
                future = executor.submit(make_request)
                # Get the result of the request and add it to the list of responses
                try:
                    response = future.result(timeout=1)  # Set a timeout for each request if needed
                    responses.append(response)
                except concurrent.futures.TimeoutError:
                    responses.append({'error': 'Request timed out'})

    # Record the end time of the load test
    end_time = time.time()

    # Calculate and print the total execution time of the load test
    total_time = end_time - start_time
    print(f"Total execution time: {total_time} seconds")

    # Print the total number of requests
    print(f"Total requests: {len(responses)} requests")

    # Print the total number of successful requests
    success_responses = sum(1 for d in responses if d.get('status_code') == 200)
    print(f"Total successful requests: {success_responses} requests")

    # Calculate and print the average response time
    average_response_time = sum(d['response_time'] for d in responses if 'response_time' in d) / len(responses)
    print(f"Average response time: {average_response_time} seconds")

    # Calculate and print success rate
    success_rate = 100.0 * (1.0 * success_responses / len(responses))
    print(f"Success rate: {success_rate}%")

    # Optionally, log the detailed responses or any errors encountered
    for response in responses:
        if 'error' in response:
            print(f"Error: {response['error']}")
        else:
            print(f"Status Code: {response['status_code']}, Response Time: {response['response_time']} seconds")

    # Reset standard output to original
    sys.stdout = original_stdout
