# 🧪 Europa Tech Tracker - Test Suite

Comprehensive testing for all phases of the Europa Tech Tracker project.

## 🎯 Test Overview

This test suite validates functionality across all development phases:

- **Phase 1 (MVP)**: RSS scraping, basic article processing
- **Phase 2 (Enhanced)**: Caching, deduplication, multi-source processing  
- **Phase 3 (Automation)**: Logging, GitHub Actions workflows
- **Future Phases**: Google Docs integration, web scraping, YouTube

## 📋 Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and test configuration
├── test_cache.py              # Phase 1-2: Cache Manager tests
├── test_deduplicator.py       # Phase 2: Article deduplication tests
├── test_config_loader.py      # Phase 1-3: Configuration loading tests
├── test_logger.py             # Phase 3: Logging system tests
├── test_integration_rss.py    # Phase 1-2: RSS processing integration tests
├── test_workflow_validation.py # Phase 3: GitHub Actions workflow tests
└── README.md                  # This file
```

## 🚀 Quick Start

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Using the test runner
python run_tests.py

# Using pytest directly
pytest tests/ -v
```

### Run Specific Test Suites

```bash
# Unit tests only (fastest)
python run_tests.py --suite unit

# Integration tests
python run_tests.py --suite integration

# Workflow validation tests
python run_tests.py --suite workflow

# With coverage report
python run_tests.py --coverage
```

## 🧪 Test Categories

### Unit Tests (`@pytest.mark.unit`)

Test individual components in isolation:

- **Cache Manager**: Article caching, retrieval, cleanup
- **Deduplicator**: Similarity detection, duplicate prevention
- **Config Loader**: YAML loading, validation, settings
- **Logger**: GitHub Actions integration, session tracking

Usage:
```bash
pytest -m unit
```

### Integration Tests (`@pytest.mark.integration`)

Test component interactions and data flow:

- **RSS Processing Pipeline**: End-to-end article collection and processing
- **Multi-source Collection**: Handling multiple RSS feeds
- **Error Recovery**: Graceful handling of source failures
- **Cache Integration**: Article persistence across runs

Usage:
```bash
pytest -m integration
```

### Workflow Tests (`@pytest.mark.workflow`)

Validate GitHub Actions automation:

- **YAML Syntax**: Workflow configuration validation
- **Schedule Validation**: Cron expression verification
- **Environment Setup**: Python and dependency installation
- **Permissions**: GitHub repository access rights

Usage:
```bash
pytest -m workflow
```

### Slow Tests (`@pytest.mark.slow`)

Tests that take longer to execute:

- Network operations
- Large dataset processing
- Comprehensive integration scenarios

Skip with:
```bash
pytest -m "not slow"
```

## 📊 Coverage Reports

Generate detailed coverage analysis:

```bash
# HTML report (recommended)
python run_tests.py --coverage

# Terminal report only
pytest --cov=src --cov-report=term

# XML report (for CI)
pytest --cov=src --cov-report=xml
```

Coverage reports are saved to `htmlcov/index.html`.

## 🔧 Test Configuration

### Pytest Settings (`pytest.ini`)

- **Test Discovery**: Automatic test file detection
- **Coverage**: Source code coverage tracking
- **Markers**: Test categorization and filtering
- **Output**: Verbose reporting and coverage exclusions

### Shared Fixtures (`conftest.py`)

Available test fixtures:

- `sample_rss_feed`: Mock RSS feed content
- `sample_config`: Test configuration data
- `sample_articles`: Sample article objects
- `processed_articles`: Articles with metadata
- `temp_directories`: Temporary file structure
- `mock_cache_file`: Pre-populated cache
- `mock_requests`: HTTP request mocking

### Custom Assertions

Validation helpers:

- `assert_valid_article_structure()`: Check article fields
- `assert_valid_processed_article()`: Validate processed metadata
- `assert_valid_cache_entry()`: Verify cache format

## 🐛 Debugging Tests

### Run Single Test

```bash
pytest tests/test_cache.py::TestCacheManager::test_add_article_to_cache -v
```

### Debug Mode

```bash
pytest --pdb  # Drop into debugger on failure
pytest -s     # Don't capture output (print statements work)
```

### Test Selection

```bash
# Run tests matching pattern
pytest -k "cache or dedup"

# Run specific test class  
pytest tests/test_cache.py::TestCacheManager
```

## 🚀 Continuous Integration

### GitHub Actions Integration

The test suite runs automatically on:

- **Push to main/develop**: Full test suite
- **Pull requests**: Complete validation
- **Manual trigger**: Configurable test selection

Workflow: [`.github/workflows/test_suite.yml`](../.github/workflows/test_suite.yml)

### Test Matrix

Tests run against multiple Python versions:
- Python 3.11 (primary)
- Python 3.12 (future compatibility)

## 🔍 Test Data

### Sample RSS Feed

Mock RSS content with:
- European tech articles (high relevance)
- US tech articles (lower relevance)
- Mixed content for deduplication testing

### Configuration Testing

Mock configurations for:
- Active/inactive sources
- Keyword filtering scenarios
- Rate limiting settings
- Error conditions

### Cache Testing

Simulated cache scenarios:
- Empty cache initialization
- Populated cache with articles
- Cache corruption handling
- Cleanup and maintenance

## ⚡ Performance Testing

### Benchmarks

```bash
# Time test execution
pytest --durations=10  # Show 10 slowest tests

# Profile memory usage
pytest --memray  # Requires memray package
```

### Load Testing

Test with large datasets:

```bash
pytest -m "slow"  # Run performance tests
```

## 🎯 Writing New Tests

### Test File Organization

1. Create test files matching source structure:
   ```
   src/utils/new_module.py → tests/test_new_module.py
   ```

2. Use descriptive test class names:
   ```python
   class TestNewModuleFunctionality:
   ```

3. Include markers for categorization:
   ```python
   @pytest.mark.unit
   def test_specific_function():
   ```

### Test Naming Convention

- `test_function_name_behavior`
- `test_class_method_scenario`
- `test_integration_feature_outcome`

Example:
```python
def test_cache_manager_add_article_success()
def test_deduplicator_detect_duplicate_above_threshold()
def test_rss_collection_with_source_failure()
```

### Using Fixtures

```python
def test_with_fixtures(sample_config, temp_directories):
    # Use provided fixtures in tests
    config_loader = ConfigLoader(temp_directories['config'])
```

## 🔗 Related Documentation

- [Project README](../README.md)
- [Configuration Guide](../config/README.md)
- [Workflow Documentation](../.github/workflows/README.md)
- [Phase Documentation](../PROJECT_PLAN.md)

## 📚 Testing Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Guide](https://coverage.readthedocs.io/)
- [Responses Library](https://github.com/getsentry/responses) (HTTP mocking)
- [GitHub Actions Testing](https://docs.github.com/en/actions/automating-builds-and-tests)

---

*Ensure all phases work correctly with comprehensive testing* 🧪✅