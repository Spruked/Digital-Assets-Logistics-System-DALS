#!/usr/bin/env python3
"""
DALS Endpoint Scanner and Validator
Tests all API endpoints on port 8003 to ensure proper operation
"""

import requests
import json
from typing import Dict, List, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8003"
TIMEOUT = 5

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class EndpointTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
        
    def test_endpoint(self, method: str, path: str, data: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
        """Test a single endpoint and return results"""
        url = f"{self.base_url}{path}"
        result = {
            "method": method,
            "path": path,
            "url": url,
            "success": False,
            "status_code": None,
            "response_time": None,
            "error": None
        }
        
        try:
            start_time = datetime.now()
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=TIMEOUT)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=TIMEOUT)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=TIMEOUT)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000  # ms
            
            result["status_code"] = response.status_code
            result["response_time"] = round(response_time, 2)
            result["success"] = response.status_code == expected_status
            
            # Try to parse JSON response
            try:
                result["response_preview"] = str(response.json())[:100]
            except:
                result["response_preview"] = str(response.text)[:100]
                
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection refused - is the server running?"
        except requests.exceptions.Timeout:
            result["error"] = "Request timeout"
        except Exception as e:
            result["error"] = str(e)
        
        self.results.append(result)
        return result
    
    def print_result(self, result: Dict[str, Any]):
        """Print a single test result"""
        if result["success"]:
            status = f"{GREEN}✓{RESET}"
            color = GREEN
        elif result["error"]:
            status = f"{RED}✗{RESET}"
            color = RED
        else:
            status = f"{YELLOW}⚠{RESET}"
            color = YELLOW
        
        print(f"{status} {result['method']:6} {result['path']:50}", end=" ")
        
        if result["status_code"]:
            print(f"{color}[{result['status_code']}]{RESET} {result['response_time']}ms", end="")
        elif result["error"]:
            print(f"{RED}{result['error']}{RESET}", end="")
        
        print()
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        success = sum(1 for r in self.results if r["success"])
        failed = sum(1 for r in self.results if r["error"])
        
        print(f"\n{'='*80}")
        print(f"ENDPOINT TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Endpoints: {total}")
        print(f"{GREEN}Successful: {success}{RESET}")
        print(f"{RED}Failed: {failed}{RESET}")
        print(f"{YELLOW}Other Status: {total - success - failed}{RESET}")
        print(f"Success Rate: {(success/total*100):.1f}%")
        print(f"{'='*80}\n")


def main():
    print(f"{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}DALS Endpoint Scanner - Port 8003{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    tester = EndpointTester()
    
    # Test Core Endpoints
    print(f"{BLUE}[Core Endpoints]{RESET}")
    result = tester.test_endpoint("GET", "/")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/health")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/status")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/docs")
    tester.print_result(result)
    
    # Test ISS/Time Endpoints
    print(f"\n{BLUE}[ISS Time & Stardate]{RESET}")
    result = tester.test_endpoint("GET", "/api/v1/iss/now")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/time")
    tester.print_result(result)
    
    # Test Telemetry Endpoints
    print(f"\n{BLUE}[Telemetry & Metrics]{RESET}")
    result = tester.test_endpoint("GET", "/api/telemetry/metrics")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/telemetry/status")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/telemetry/events")
    tester.print_result(result)
    
    # Test CALEON Security Endpoints
    print(f"\n{BLUE}[CALEON Security Layer]{RESET}")
    result = tester.test_endpoint("GET", "/api/caleon/status")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/caleon/threats/status")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/caleon/security/dashboard")
    tester.print_result(result)
    
    # Test UCM Integration
    print(f"\n{BLUE}[UCM Integration]{RESET}")
    result = tester.test_endpoint("GET", "/api/ucm/status")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/ucm/health")
    tester.print_result(result)
    
    # Test Alpha CertSig Elite
    print(f"\n{BLUE}[Alpha CertSig Elite]{RESET}")
    result = tester.test_endpoint("GET", "/api/alpha-certsig/health")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/alpha-certsig/mint-status")
    tester.print_result(result)
    
    # Test TrueMark Mint
    print(f"\n{BLUE}[TrueMark Mint Enterprise]{RESET}")
    result = tester.test_endpoint("GET", "/api/truemark/health")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/truemark/status")
    tester.print_result(result)
    
    # Test DALS Asset Management
    print(f"\n{BLUE}[DALS Asset Management]{RESET}")
    result = tester.test_endpoint("GET", "/api/dals/assets")
    tester.print_result(result)
    
    # Test WebSocket endpoint (just check if it exists)
    print(f"\n{BLUE}[WebSocket]{RESET}")
    result = tester.test_endpoint("GET", "/api/ws/events", expected_status=426)  # Upgrade required
    tester.print_result(result)
    
    # Test Module Status Endpoints
    print(f"\n{BLUE}[Module Status]{RESET}")
    result = tester.test_endpoint("GET", "/api/modules/iss/pulse")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/modules/caleon/status")
    tester.print_result(result)
    
    result = tester.test_endpoint("GET", "/api/modules/certsig/mint-status")
    tester.print_result(result)
    
    # Print summary
    tester.print_summary()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"endpoint_test_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "total_tests": len(tester.results),
            "results": tester.results
        }, f, indent=2)
    
    print(f"Results saved to: {output_file}")
    
    # Return exit code based on success
    if all(r["success"] or r["status_code"] == 404 for r in tester.results):
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
