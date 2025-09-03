name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests with pytest
      run: |
        pytest -v --tb=short test_app.py
    
    - name: Generate test coverage report
      run: |
        pip install coverage
        coverage run -m pytest test_app.py
        coverage xml
    
    - name: Upload coverage reports to Codecov
      if: matrix.python-version == '3.9'
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false

  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.9
    
    - name: Install linting dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 black isort
    
    - name: Run flake8
      run: flake8 app.py test_app.py --max-line-length=88 --extend-ignore=E203,W503
    
    - name: Run black (check only)
      run: black --check app.py test_app.py
    
    - name: Run isort (check only)
      run: isort --check-only app.py test_app.py

  docker:
    runs-on: ubuntu-latest
    needs: [test, lint]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Build Docker image
      run: |
        docker build -t fitness-tracker:${{ github.sha }} .
        docker build -t fitness-tracker:latest .
    
    - name: Test Docker image
      run: |
        docker run -d -p 5000:5000 --name test-container fitness-tracker:latest
        sleep 10
        curl -f http://localhost:5000/health || exit 1
        docker stop test-container
        docker rm test-container
    
    - name: Save Docker image as artifact
      run: |
        docker save fitness-tracker:latest | gzip > fitness-tracker-image.tar.gz
    
    - name: Upload Docker image artifact
      uses: actions/upload-artifact@v4  # Updated to v4
      with:
        name: docker-image
        path: fitness-tracker-image.tar.gz
        retention-days: 7
        compression-level: 0  # Already compressed

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.9
    
    - name: Install security tools
      run: |
        python -m pip install --upgrade pip
        pip install safety bandit
    
    - name: Run safety check
      run: safety check -r requirements.txt
    
    - name: Run bandit security linter
      run: bandit -r app.py -f json -o bandit-report.json || true
    
    - name: Upload security report
      uses: actions/upload-artifact@v4  # Updated to v4
      with:
        name: security-report
        path: bandit-report.json
        retention-days: 30