# Assignment1-Devops-2024tm93287
Assignment 1 of DevOps

# Software requirements
Install Python SDK

# Steps to Run Application locally
- Follow the below commands step by step to run the application locally
  - **Step 1:** Create virtual environment: `python -m venv venv`
  - **Step 2:** Activate virtual environment: `venv\Scripts\activate`
  - **Step 2:** Install dependencies: `pip install -r requirements.txt`
  - **Step 3:** Start the Flask server: `python app.py`
- please refer to the postman collection file for testing

# Steps to execute the tests locally
- Ensure that you have Python and Flask installed in the environment
- use the command `python -v test_app.py`

# Brief Overview of GitHub Actions
- **Triggers**: Every git push to the repository.
- **Steps**:
  - **Test** - Runs pytest unit tests inside Docker container.
  - **Build** - Creates Docker image with Flask app and dependencies.
- **Purpose**: Ensures code quality by automatically testing every change before integration.
- **Success**: Green status in Actions tab means all tests pass and code is deployment-ready.
- Once the build is complete successfully we get the '**Artifact download URL:**' to download the Artifact. 
