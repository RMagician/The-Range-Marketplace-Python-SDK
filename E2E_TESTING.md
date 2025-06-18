# End-to-End Testing Guide

This guide explains how to run the end-to-end (e2e) tests for The Range Marketplace Python SDK functionality including order events and product feed operations.

## Overview

The e2e tests validate the complete integration with the live UAT (User Acceptance Testing) API environment. These tests perform actual API calls to verify that the SDK works correctly with the real service.

## Prerequisites

1. **Valid UAT Credentials**: You need access to test credentials for the UAT environment
2. **Network Access**: The test environment must have access to `uatsupplier.rstore.com`
3. **Environment Variables**: Test credentials must be provided via environment variables

## Setup

### 1. Set Environment Variables

Before running the e2e tests, you must set the following environment variables with your UAT credentials:

```bash
export THERANGE_USERNAME=your_uat_username
export THERANGE_PASSWORD=your_uat_password
```

### 2. Install Dependencies

Make sure all dependencies are installed:

```bash
pip install -e .
pip install pytest
```

## Running E2E Tests

### Run All E2E Tests

```bash
# Run order event e2e tests
python -m pytest tests/test_order_event_e2e.py -v

# Run product feed e2e tests
python -m pytest tests/test_product_feed_e2e.py -v

# Run all e2e tests
python -m pytest tests/test_*_e2e.py -v
```

### Run Specific E2E Tests

#### Order Event Tests

```bash
# Test authentication only
python -m pytest tests/test_order_event_e2e.py::TestOrderEventClientE2E::test_authentication_e2e -v

# Test dispatch order functionality
python -m pytest tests/test_order_event_e2e.py::TestOrderEventClientE2E::test_dispatch_order_e2e -v

# Test cancel order functionality
python -m pytest tests/test_order_event_e2e.py::TestOrderEventClientE2E::test_cancel_order_e2e -v

# Test complete order lifecycle
python -m pytest tests/test_order_event_e2e.py::TestOrderEventE2EIntegration::test_full_order_lifecycle_e2e -v
```

#### Product Feed Tests

```bash
# Test product feed with ProductFeedRequest
python -m pytest tests/test_product_feed_e2e.py::TestProductFeedClientE2E::test_send_product_feed_e2e -v

# Test product feed with dictionary data
python -m pytest tests/test_product_feed_e2e.py::TestProductFeedClientE2E::test_send_product_feed_dict_e2e -v

# Test legacy submit products method
python -m pytest tests/test_product_feed_e2e.py::TestProductFeedClientE2E::test_submit_products_e2e -v

# Test price amendments
python -m pytest tests/test_product_feed_e2e.py::TestProductFeedClientE2E::test_send_price_amendment_e2e -v

# Test complete product lifecycle
python -m pytest tests/test_product_feed_e2e.py::TestProductFeedE2EIntegration::test_full_product_lifecycle_e2e -v
```

### Run with Verbose Output

To see detailed output and API responses:

```bash
# Order event tests with verbose output
python -m pytest tests/test_order_event_e2e.py -v -s

# Product feed tests with verbose output
python -m pytest tests/test_product_feed_e2e.py -v -s

# All e2e tests with verbose output
python -m pytest tests/test_*_e2e.py -v -s
```

## Test Coverage

The e2e tests cover the following scenarios:

### Core Functionality Tests
- **Network Connectivity**: Verifies connection to the UAT API
- **Authentication**: Tests successful authentication with valid credentials
- **Dispatch Order**: Tests order dispatch with complete payload including optional delivery dates
- **Cancel Order**: Tests order cancellation with various cancellation codes
- **Send Event**: Tests custom event sending functionality
- **Product Feed**: Tests product creation using ProductFeedRequest objects
- **Product Feed Dict**: Tests product creation using dictionary data with validation
- **Submit Products**: Tests legacy product submission method
- **Price Amendments**: Tests price-only updates for existing products

### Error Handling Tests
- **Authentication Errors**: Tests handling of invalid credentials
- **Unauthenticated Calls**: Verifies that API calls fail without authentication

### Integration Tests
- **Full Order Lifecycle**: Tests dispatch followed by cancellation of the same order
- **Full Product Lifecycle**: Tests product creation followed by price amendment

## Test Behavior

### When Credentials Are Not Provided
If the `THERANGE_USERNAME` and `THERANGE_PASSWORD` environment variables are not set, all e2e tests will be **skipped** with an informative message.

### When Network Issues Occur
If the test environment cannot reach the UAT API (network connectivity issues), the tests will be **skipped** rather than failing, with appropriate messages.

### Test Data
- All tests use uniquely generated test data to avoid conflicts
- Order numbers include timestamps (e.g., `E2E_TEST_20231201143045`)
- Product codes are prefixed with `E2E_` for easy identification
- Tests are designed to be safe to run multiple times

## Example Usage

```bash
# Set your credentials
export THERANGE_USERNAME=test_supplier_001
export THERANGE_PASSWORD=test_password_123

# Run all order event e2e tests
python -m pytest tests/test_order_event_e2e.py -v

# Run all product feed e2e tests
python -m pytest tests/test_product_feed_e2e.py -v

# Run all e2e tests
python -m pytest tests/test_*_e2e.py -v

# Expected output (order events):
# tests/test_order_event_e2e.py::TestOrderEventClientE2E::test_network_connectivity_e2e PASSED
# tests/test_order_event_e2e.py::TestOrderEventClientE2E::test_authentication_e2e PASSED
# tests/test_order_event_e2e.py::TestOrderEventClientE2E::test_dispatch_order_e2e PASSED
# ... etc

# Expected output (product feed):
# tests/test_product_feed_e2e.py::TestProductFeedClientE2E::test_network_connectivity_e2e PASSED
# tests/test_product_feed_e2e.py::TestProductFeedClientE2E::test_authentication_e2e PASSED
# tests/test_product_feed_e2e.py::TestProductFeedClientE2E::test_send_product_feed_e2e PASSED
# ... etc
```

## Troubleshooting

### Tests Are Being Skipped
- **Cause**: Environment variables not set
- **Solution**: Set `THERANGE_USERNAME` and `THERANGE_PASSWORD` environment variables

### Network Connectivity Errors
- **Cause**: Cannot reach `uatsupplier.rstore.com`
- **Solution**: Check network connectivity, firewall settings, or run from an environment with internet access

### Authentication Failures
- **Cause**: Invalid credentials or expired test account
- **Solution**: Verify credentials are correct and account is active in the UAT environment

### API Response Errors
- **Cause**: UAT API changes or service issues
- **Solution**: Check with The Range team about UAT environment status

## Integration with CI/CD

To integrate these tests into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run E2E Tests
  env:
    THERANGE_USERNAME: ${{ secrets.THERANGE_UAT_USERNAME }}
    THERANGE_PASSWORD: ${{ secrets.THERANGE_UAT_PASSWORD }}
  run: |
    python -m pytest tests/test_order_event_e2e.py -v
    python -m pytest tests/test_product_feed_e2e.py -v
```

## Security Notes

- **Never commit credentials** to version control
- Use environment variables or secure secret management
- UAT credentials should be separate from production credentials
- Rotate test credentials regularly
- Ensure test data doesn't contain sensitive information

## Extending E2E Tests

To add new e2e tests:

1. Follow the existing pattern in `test_order_event_e2e.py`
2. Use the `@pytest.mark.skipif` decorator with credential checks
3. Add network error handling with try/catch blocks
4. Generate unique test data using timestamps
5. Log API responses for debugging
6. Add comprehensive docstrings

Example:

```python
@pytest.mark.skipif(
    not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
    reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
)
def test_new_functionality_e2e(self):
    """Test new functionality with live API call."""
    try:
        self.auth.authenticate()
        # Your test logic here
        response = self.client.new_method(test_data)
        assert response is not None
        print(f"Response: {response}")
    except requests.exceptions.ConnectionError:
        pytest.skip("Network connectivity issue - cannot reach UAT API")
    except requests.exceptions.Timeout:
        pytest.skip("Network timeout - UAT API is not responding")
```