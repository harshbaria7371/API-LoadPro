"""
API Load Pro - Universal Python REST API Data Creator
A command-line utility for automating test data creation via REST APIs.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List
import requests
from Libraries.config_manager import ConfigManager
from Libraries.authenticator import Authenticator

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    Returns:
    Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="API-Load Pro - Universal Python REST API Data Creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        python main.py --data-file sample_data.json
        python main.py -d test_data.json --verbose
        """
    )

    parser.add_argument(
        '-d', '--data-file',
        required=True,
        help='The path to the JSON file containing the test data & API requests'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output for detailed requests information'
    )

    parser.add_argument(
        '--config',
        default='config.ini',
        help='The path to the configuration file(defaults to config.ini)'
    )

    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save the test data & API requests'
    )

    parser.add_argument(
        '--result-dir',
        default='results',
        help='The directory to save the test data & API requests(defaults to results)'
    )

    return parser.parse_args()

def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Load JSON data from file.
    Args:
        file_path: Path to the JSON file
    Returns:
        List of request specifications
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON file must contain an array of request objects")
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file '{file_path}' not found")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in data file: {e}")

def make_request(
    method: str,
    url: str,
    headers: Dict[str, str],
    data: Any = None,
    json_data: Any = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Make an HTTP request.
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Full URL to request
        headers: Request headers
        data: Form data (for POST/PUT)
        json_data: JSON data (for POST/PUT)
        verbose: Enable verbose output
    Returns:
        Dictionary containing response information
    """
    method = method.upper()
    
    if verbose:
        print(f"\n{'='*50}")
        print(f"Making {method} request to: {url}")
        if headers:
            print(f"Headers: {json.dumps(headers, indent=2)}")
        if json_data:
            print(f"JSON Body: {json.dumps(json_data, indent=2)}")
        if data:
            print(f"Form Data: {data}")
    
    try:
        # Prepare request kwargs
        request_kwargs = {'headers': headers}
        
        if json_data:
            request_kwargs['json'] = json_data
        elif data:
            request_kwargs['data'] = data
        
        # Make the request based on method
        if method == 'GET':
            response = requests.get(url, **request_kwargs)
        elif method == 'POST':
            response = requests.post(url, **request_kwargs)
        elif method == 'PUT':
            response = requests.put(url, **request_kwargs)
        elif method == 'DELETE':
            response = requests.delete(url, **request_kwargs)
        elif method == 'PATCH':
            response = requests.patch(url, **request_kwargs)
        elif method == 'HEAD':
            response = requests.head(url, **request_kwargs)
        elif method == 'OPTIONS':
            response = requests.options(url, **request_kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Prepare response data
        result = {
            'method': method,
            'url': url,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'timestamp': datetime.now().isoformat()
        }
        
        # Try to parse response as JSON, otherwise use text
        try:
            result['response_body'] = response.json()
            result['response_type'] = 'json'
        except (json.JSONDecodeError, ValueError):
            result['response_body'] = response.text
            result['response_type'] = 'text'
        
        if verbose:
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
            if result['response_type'] == 'json':
                print(f"Response Body: {json.dumps(result['response_body'], indent=2)}")
            else:
                print(f"Response Body: {result['response_body'][:500]}...")  # Truncate long text
        
        return result
        
    except requests.exceptions.RequestException as e:
        error_result = {
            'method': method,
            'url': url,
            'status_code': None,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        if verbose:
            print(f"Request Error: {e}")
        return error_result

def save_results(results: List[Dict[str, Any]], result_dir: str, data_file: str) -> None:
    """
    Save request results to a JSON file.
    Args:
        results: List of request results
        result_dir: Directory to save results
        data_file: Original data file name (for naming output file)
    """
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    # Generate output filename based on input file and timestamp
    base_name = os.path.splitext(os.path.basename(data_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(result_dir, f"{base_name}_results_{timestamp}.json")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"Warning: Error saving results: {e}")

def main():
    """ Main entry point for the API Load Pro Utility """
    print("_"*50)
    print("API Load Pro - Universal Python REST API Data Creator")
    print("_"*50)

    args = parse_arguments()

    try:
        # Load configuration
        config_manager = ConfigManager(args.config)
        config = config_manager.load_config()
        print(f"Configuration loaded from {args.config}")

        # Load JSON data
        print(f"\nLoading data from {args.data_file}...")
        requests_data = load_json_data(args.data_file)
        print(f"Loaded {len(requests_data)} request(s)")

        # Check if authentication is required
        require_auth = config_manager.requires_auth()
        access_token = None
        
        if require_auth:
            # Initialize authenticator
            authenticator = Authenticator(config_manager)
            
            # Get access token (will authenticate if needed)
            print("\nAuthenticating...")
            access_token = authenticator.get_access_token()
            
            if not access_token:
                print("Error: Failed to obtain access token")
                if not authenticator.authenticate():
                    print("Error: Authentication failed")
                    sys.exit(1)
                access_token = authenticator.get_access_token()
            
            if access_token:
                print("Authentication successful")
            else:
                print("Error: Could not obtain access token")
                sys.exit(1)
        else:
            print("\nAuthentication skipped (require_auth = false in config)")

        # Prepare headers
        base_url = config_manager.get_base_url()
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Add authorization header only if authentication is required and token is available
        if require_auth and access_token:
            headers['Authorization'] = f'Bearer {access_token}'

        # Process each request
        print(f"\nProcessing {len(requests_data)} request(s)...")
        results = []
        
        for idx, request_spec in enumerate(requests_data, 1):
            path = request_spec.get('path', '')
            method = request_spec.get('method', 'GET')
            body = request_spec.get('body', None)
            headers_override = request_spec.get('headers', {})
            
            # Merge custom headers with default headers
            request_headers = {**headers, **headers_override}
            
            # Build full URL
            if path.startswith('http'):
                full_url = path
            else:
                # Ensure base_url doesn't end with / and path starts with /
                base = base_url.rstrip('/')
                path = '/' + path.lstrip('/')
                full_url = base + path
            
            print(f"\n[{idx}/{len(requests_data)}] {method} {path}")
            
            # Prepare request data
            json_data = None
            form_data = None
            
            if body:
                if isinstance(body, dict):
                    json_data = body
                elif isinstance(body, str):
                    try:
                        json_data = json.loads(body)
                    except json.JSONDecodeError:
                        form_data = body
            
            # Make the request
            result = make_request(
                method=method,
                url=full_url,
                headers=request_headers,
                data=form_data,
                json_data=json_data,
                verbose=args.verbose
            )
            
            # Add request specification to result
            result['request_spec'] = request_spec
            
            results.append(result)
            
            # Print summary
            if result.get('status_code'):
                print(f"  Status: {result['status_code']}")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")

        # Save results if requested
        if not args.no_save:
            save_results(results, args.result_dir, args.data_file)
        else:
            print("\nResults not saved (--no-save flag set)")

        # Print summary
        print(f"\n{'='*50}")
        print("Summary:")
        successful = sum(1 for r in results if r.get('status_code') and 200 <= r['status_code'] < 300)
        failed = len(results) - successful
        print(f"  Total requests: {len(results)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"{'='*50}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
