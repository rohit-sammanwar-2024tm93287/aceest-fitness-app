name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest -v test_app.py

    - name: Upload test results (if tests fail)
      uses: actions/upload-artifact@v4
      if: failure()
      with:
        name: test-results
        path: |
          pytest.log
          test-results/
        retention-days: 7

  build:
    runs-on: ubuntu-latest
    needs: test

    steps:
    - uses: actions/checkout@v4

    - name: Build Docker image
      run: docker build -t fitness-tracker .

    - name: Save Docker image
      run: docker save fitness-tracker | gzip > fitness-tracker.tar.gz

    - name: Upload Docker image
      uses: actions/upload-artifact@v4
      with:
        name: docker-image
        path: fitness-tracker.tar.gz
        retention-days: 1