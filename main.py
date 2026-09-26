"""
Entry point for the Nagpur UHI Analysis Platform.
"""

import sys
import uvicorn

def main():
    print("Starting Nagpur Urban Heat Island Platform API on http://127.0.0.1:8000 ...")
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
