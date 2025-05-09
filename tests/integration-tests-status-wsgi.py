import json
import os
import sys
from wsgiref.simple_server import make_server


def _load_test_data():
    """Loads the JSON test results from a file."""
    filepath = os.environ.get('TEST_RESULTS_JSON', 'test_results.json')
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f), '200 OK'
    except Exception as e:
        return {"error": str(e)}, '500 Internal Server Error'


def _generate_html(data):
    """Generates an HTML report from the test results JSON."""
    html = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Test Report</title>",
        "<style>body { font-family: Arial; } .error { color: red; } .success { color: green; }</style>",
        "</head><body>",
        "<h1>Test Results</h1><ul>"
    ]

    for test_name, result in data.items():
        elapsed = result.get("Elapsed Time", "N/A")
        errors = result.get("Errors", [])

        html.append(f"<li><strong>{test_name}</strong> - Elapsed Time: {elapsed:.2f} seconds")
        if errors:
            html.append("<ul class='error'>")
            for err in errors:
                html.append(f"<li><b>{err.get('collectionId')}</b>: "
                            f"{err.get('statusCode')}<br>"
                            f"<a href='{err.get('url')}' target='_blank'>{err.get('url')}</a></li>")
            html.append("</ul>")
        else:
            html.append("<span class='success'> ✅ No errors</span>")

        html.append("</li>")

    html.append("</ul></body></html>")
    return "\n".join(html).encode('utf-8')


def application(environ, start_response):
    data, status = _load_test_data()
    if status != '200 OK':
        html = f"<h1>Error loading test results:</h1><p>{data.get('error')}</p>".encode('utf-8')
    else:
        html = _generate_html(data)

    headers = [('Content-type', 'text/html'), ('Content-Length', str(len(html)))]
    start_response(status, headers)
    return [html]


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Serving test results on http://localhost:{port}")
    httpd = make_server('', port, application)
    httpd.serve_forever()
