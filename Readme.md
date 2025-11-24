# El País Scraper Test Suite

This repository contains automated tests for a web scraper designed to extract data from the El País newspaper. The tests are built using the Pytest framework and can be executed both locally and on the BrowserStack cloud platform.

## Drive Link

As part of the project submission, the following resources are available at the link below:

*   **Screenshots and Test Reports**

**https://drive.google.com/drive/folders/19iPmEaQ8pzw7PwhHVPLI02ylQJ2SXDc7**

## Prerequisites

Before running the tests, ensure you have the following installed:

*   **Python 3.x:** Download and install it from the official [Python website](https://www.python.org/).
*   **pip:** Python's package installer, which typically comes with Python 3.x.

You will also need a BrowserStack account to run the tests in `browserstack` mode.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install dependencies:**

    Install all the required Python packages using the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure BrowserStack Credentials:**

    To run tests on BrowserStack, you need to set up your credentials. This can be done in two ways:

    *   **Environment Variables (Recommended):** Set the following environment variables:
        *   `BROWSERSTACK_USERNAME`: Your BrowserStack username.
        *   `BROWSERSTACK_ACCESS_KEY`: Your BrowserStack access key.

    *   **Configuration File:** Create a `browserstack.yml` file in the root of the project with the following content:

        ```yaml
        userName: YOUR_USERNAME
        accessKey: YOUR_ACCESS_KEY
        ```

        Replace `YOUR_USERNAME` and `YOUR_ACCESS_KEY` with your actual BrowserStack credentials.

## Running the Tests

This test suite can be run in different modes using the command line. The tests are designed to check the functionality of the El País web scraper.

### Running Tests on BrowserStack

To execute the tests on the BrowserStack cloud infrastructure, use the following command:

```bash
pytest test_el_pais_scraper.py --mode browserstack -s -n 5
```

**Command Breakdown:**

*   `pytest`: This command initiates the test execution, which then communicates with the BrowserStack cloud.
*   `test_el_pais_scraper.py`: This is the Python file containing the tests for the El País scraper.
*   `--mode browserstack`: This is a custom flag that configures the tests to run on the BrowserStack platform. It ensures that the tests utilize the remote browsers and devices available on BrowserStack.
*   `-s`: This standard pytest flag disables output capturing, allowing any `print` statements within the tests to be displayed in the console. This is useful for debugging purposes.
*   `-n 5`: This flag, provided by the `pytest-xdist` plugin, enables parallel test execution with 5 workers. This can significantly reduce the overall test execution time.

### Running Tests Locally

To run the tests on your local machine, use the following command:

```bash
pytest test_el_pais_scraper.py --mode local -s -n 5
```

**Command Breakdown:**

*   `pytest`: This command directly invokes the Pytest test runner.
*   `test_el_pais_scraper.py`: Specifies the test file to be executed.
*   `--mode local`: This custom flag configures the tests to run in a local environment, using the browsers installed on your machine.
*   `-s`: Disables output capturing to show `print` statements.
*   `-n 5`: Runs the tests in parallel with 5 processes to speed up execution.

---

**Note:** The `--mode` flag is a custom argument defined within this project's test configuration (likely in a `conftest.py` file) to switch between different test environments. The specific behavior of this flag is determined by the test framework's implementation.
