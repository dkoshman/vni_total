# VNI Total

A Python data processing application that extracts business metrics from MySQL and loads them into PostgreSQL.

## Overview

This application processes bike-sharing business data including:
- Ride statistics and revenue
- User registration metrics  
- Payment processing data (PayTabs, Stripe)
- Subscription revenue
- Bike availability metrics

## Features

- **Data Extraction**: Complex SQL queries to aggregate business metrics from MySQL
- **Data Loading**: Automated loading of processed data into PostgreSQL
- **Error Handling**: Comprehensive error handling and logging
- **Environment Configuration**: Secure credential management via environment variables
- **Comprehensive Testing**: 98% test coverage with unit and integration tests

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# MySQL credentials
export user_mysql="your_mysql_user"
export password_mysql="your_mysql_password"
export host_mysql="your_mysql_host"
export port_mysql="3306"
export db_mysql="your_mysql_database"

# PostgreSQL credentials
export user_postgres="your_postgres_user"
export password_postgres="your_postgres_password"
export host_postgres="your_postgres_host"
export port_postgres="5432"
export db_postgres="your_postgres_database"
```

## Usage

Run the data processing pipeline:
```bash
python entrypoint.py
```

## Testing

The project includes comprehensive tests with 98% code coverage.

### Run All Tests
```bash
# Using pytest directly
pytest tests/ -v --cov=entrypoint --cov-report=term-missing

# Using the test runner script
python run_tests.py
```

### Run Integration Tests Only
```bash
python run_tests.py --integration-only
```

### Test Structure
- `tests/test_entrypoint.py` - Unit tests for all functions
- `tests/test_integration.py` - Integration tests for the complete workflow
- `tests/test_main_execution.py` - Tests for script execution structure

### Test Coverage
The test suite covers:
- ✅ Environment variable validation
- ✅ Database connection string creation
- ✅ SQL query generation
- ✅ Data extraction from MySQL
- ✅ Data loading to PostgreSQL
- ✅ Error handling and edge cases
- ✅ Integration workflow testing

## Architecture

### Functions

- `get_mysql_credentials()` - Retrieves MySQL credentials from environment
- `get_postgres_credentials()` - Retrieves PostgreSQL credentials from environment
- `create_mysql_engine()` - Creates MySQL connection string
- `create_postgres_engine()` - Creates PostgreSQL SQLAlchemy engine
- `get_vni_query()` - Returns the complex business metrics SQL query
- `extract_data_from_mysql()` - Executes query and returns DataFrame
- `load_data_to_postgres()` - Loads DataFrame to PostgreSQL table
- `main()` - Orchestrates the complete data processing workflow

### Data Flow

1. **Credential Validation** - Verify all required environment variables
2. **Engine Creation** - Set up database connections
3. **Data Extraction** - Execute complex SQL query on MySQL
4. **Data Loading** - Insert processed data into PostgreSQL
5. **Success Reporting** - Log number of processed rows

## Dependencies

- `pandas` - Data manipulation and analysis
- `pymysql` - MySQL database connector
- `sqlalchemy` - SQL toolkit and ORM
- `psycopg2-binary` - PostgreSQL adapter
- `pytest` - Testing framework
- `pytest-mock` - Mocking for tests
- `pytest-cov` - Coverage reporting

## Development

### Adding Tests

When adding new functionality:

1. Add unit tests in `tests/test_entrypoint.py`
2. Add integration tests in `tests/test_integration.py` if needed
3. Ensure test coverage remains above 95%
4. Run tests before committing: `python run_tests.py`

### Code Quality

- Functions are well-documented with docstrings
- Error handling is comprehensive
- Environment variables are validated
- Database operations are properly abstracted
- Code follows Python best practices