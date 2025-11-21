{
  "services": [
    {
      "name": "httpbin",
      "base_url": "https://httpbin.org",
      "timeout_seconds": 5.0,
      "endpoints": [
        {
          "name": "status-200",
          "path": "/status/200",
          "method": "GET",
          "expected_status": 200,
          "max_response_ms": 1000
        },
        {
          "name": "delay-1s",
          "path": "/delay/1",
          "method": "GET",
          "expected_status": 200,
          "max_response_ms": 2000
        }
      ]
    }
  ]
}
