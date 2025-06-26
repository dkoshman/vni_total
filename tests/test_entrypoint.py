import pytest
import os
import pandas as pd
from unittest.mock import patch, MagicMock, call
from sqlalchemy import create_engine

# Import the functions we want to test
from entrypoint import (
    get_mysql_credentials,
    get_postgres_credentials,
    create_mysql_engine,
    create_postgres_engine,
    get_vni_query,
    extract_data_from_mysql,
    load_data_to_postgres,
    main
)


class TestCredentialFunctions:
    """Test credential retrieval functions."""
    
    def test_get_mysql_credentials_success(self):
        """Test successful MySQL credential retrieval."""
        env_vars = {
            "user_mysql": "test_user",
            "password_mysql": "test_pass",
            "host_mysql": "localhost",
            "port_mysql": "3306",
            "db_mysql": "test_db"
        }
        
        with patch.dict(os.environ, env_vars):
            credentials = get_mysql_credentials()
            
        assert credentials == env_vars
    
    def test_get_mysql_credentials_missing_var(self):
        """Test MySQL credential retrieval with missing environment variable."""
        env_vars = {
            "user_mysql": "test_user",
            "password_mysql": "test_pass",
            "host_mysql": "localhost",
            "port_mysql": "3306"
            # Missing db_mysql
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="Environment variable db_mysql is not set"):
                get_mysql_credentials()
    
    def test_get_postgres_credentials_success(self):
        """Test successful PostgreSQL credential retrieval."""
        env_vars = {
            "user_postgres": "test_user",
            "password_postgres": "test_pass",
            "host_postgres": "localhost",
            "port_postgres": "5432",
            "db_postgres": "test_db"
        }
        
        with patch.dict(os.environ, env_vars):
            credentials = get_postgres_credentials()
            
        assert credentials == env_vars
    
    def test_get_postgres_credentials_missing_var(self):
        """Test PostgreSQL credential retrieval with missing environment variable."""
        env_vars = {
            "user_postgres": "test_user",
            "password_postgres": "test_pass",
            "host_postgres": "localhost"
            # Missing port_postgres and db_postgres
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="Environment variable port_postgres is not set"):
                get_postgres_credentials()


class TestEngineCreation:
    """Test database engine creation functions."""
    
    def test_create_mysql_engine(self):
        """Test MySQL engine string creation."""
        credentials = {
            "user_mysql": "test_user",
            "password_mysql": "test_pass",
            "host_mysql": "localhost",
            "port_mysql": "3306",
            "db_mysql": "test_db"
        }
        
        engine_string = create_mysql_engine(credentials)
        expected = "mysql+pymysql://test_user:test_pass@localhost:3306/test_db"
        
        assert engine_string == expected
    
    def test_create_mysql_engine_special_chars(self):
        """Test MySQL engine string creation with special characters in password."""
        credentials = {
            "user_mysql": "test_user",
            "password_mysql": "test@pass#123",
            "host_mysql": "localhost",
            "port_mysql": "3306",
            "db_mysql": "test_db"
        }
        
        engine_string = create_mysql_engine(credentials)
        expected = "mysql+pymysql://test_user:test@pass#123@localhost:3306/test_db"
        
        assert engine_string == expected
    
    @patch('entrypoint.create_engine')
    def test_create_postgres_engine(self, mock_create_engine):
        """Test PostgreSQL engine creation."""
        credentials = {
            "user_postgres": "test_user",
            "password_postgres": "test_pass",
            "host_postgres": "localhost",
            "port_postgres": "5432",
            "db_postgres": "test_db"
        }
        
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        result = create_postgres_engine(credentials)
        
        expected_connection_string = "postgresql+psycopg2://test_user:test_pass@localhost:5432/test_db"
        mock_create_engine.assert_called_once_with(expected_connection_string)
        assert result == mock_engine


class TestQueryFunction:
    """Test SQL query function."""
    
    def test_get_vni_query_returns_string(self):
        """Test that get_vni_query returns a non-empty string."""
        query = get_vni_query()
        
        assert isinstance(query, str)
        assert len(query) > 0
        assert "WITH three_left_cols AS" in query
        assert "SELECT" in query
        assert "FROM" in query
    
    def test_get_vni_query_contains_expected_tables(self):
        """Test that the query contains expected table references."""
        query = get_vni_query()
        
        expected_tables = [
            "t_bike_use",
            "t_bike",
            "t_trade",
            "t_user",
            "t_payment_details",
            "t_subscription_mapping",
            "t_subscription"
        ]
        
        for table in expected_tables:
            assert table in query


class TestDataOperations:
    """Test data extraction and loading functions."""
    
    @patch('entrypoint.pd.read_sql')
    def test_extract_data_from_mysql_success(self, mock_read_sql):
        """Test successful data extraction from MySQL."""
        mock_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        mock_read_sql.return_value = mock_df
        
        engine_string = "mysql+pymysql://user:pass@host:port/db"
        query = "SELECT * FROM test_table"
        
        result = extract_data_from_mysql(engine_string, query)
        
        mock_read_sql.assert_called_once_with(query, engine_string)
        pd.testing.assert_frame_equal(result, mock_df)
    
    @patch('entrypoint.pd.read_sql')
    def test_extract_data_from_mysql_exception(self, mock_read_sql):
        """Test data extraction from MySQL with exception."""
        mock_read_sql.side_effect = Exception("Database connection failed")
        
        engine_string = "mysql+pymysql://user:pass@host:port/db"
        query = "SELECT * FROM test_table"
        
        with pytest.raises(Exception, match="Database connection failed"):
            extract_data_from_mysql(engine_string, query)
    
    def test_load_data_to_postgres_success(self):
        """Test successful data loading to PostgreSQL."""
        mock_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        mock_engine = MagicMock()
        
        # Mock the to_sql method
        mock_df.to_sql = MagicMock()
        
        load_data_to_postgres(mock_df, mock_engine)
        
        mock_df.to_sql.assert_called_once_with('vni_total', mock_engine, if_exists='append', index=False)
    
    def test_load_data_to_postgres_custom_table(self):
        """Test data loading to PostgreSQL with custom table name."""
        mock_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        mock_engine = MagicMock()
        
        # Mock the to_sql method
        mock_df.to_sql = MagicMock()
        
        load_data_to_postgres(mock_df, mock_engine, 'custom_table')
        
        mock_df.to_sql.assert_called_once_with('custom_table', mock_engine, if_exists='append', index=False)


class TestMainFunction:
    """Test the main function integration."""
    
    @patch('entrypoint.load_data_to_postgres')
    @patch('entrypoint.extract_data_from_mysql')
    @patch('entrypoint.get_vni_query')
    @patch('entrypoint.create_postgres_engine')
    @patch('entrypoint.create_mysql_engine')
    @patch('entrypoint.get_postgres_credentials')
    @patch('entrypoint.get_mysql_credentials')
    def test_main_success(self, mock_mysql_creds, mock_postgres_creds, mock_mysql_engine,
                         mock_postgres_engine, mock_get_query, mock_extract_data, mock_load_data):
        """Test successful main function execution."""
        # Setup mocks
        mock_mysql_creds.return_value = {"user_mysql": "test"}
        mock_postgres_creds.return_value = {"user_postgres": "test"}
        mock_mysql_engine.return_value = "mysql://connection"
        mock_postgres_engine.return_value = MagicMock()
        mock_get_query.return_value = "SELECT * FROM test"
        mock_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_extract_data.return_value = mock_df
        
        # Execute main function
        main()
        
        # Verify all functions were called
        mock_mysql_creds.assert_called_once()
        mock_postgres_creds.assert_called_once()
        mock_mysql_engine.assert_called_once()
        mock_postgres_engine.assert_called_once()
        mock_get_query.assert_called_once()
        mock_extract_data.assert_called_once()
        mock_load_data.assert_called_once()
    
    @patch('entrypoint.get_mysql_credentials')
    def test_main_mysql_credentials_failure(self, mock_mysql_creds):
        """Test main function with MySQL credentials failure."""
        mock_mysql_creds.side_effect = ValueError("Missing environment variable")
        
        with pytest.raises(ValueError, match="Missing environment variable"):
            main()
    
    @patch('entrypoint.extract_data_from_mysql')
    @patch('entrypoint.get_vni_query')
    @patch('entrypoint.create_postgres_engine')
    @patch('entrypoint.create_mysql_engine')
    @patch('entrypoint.get_postgres_credentials')
    @patch('entrypoint.get_mysql_credentials')
    def test_main_data_extraction_failure(self, mock_mysql_creds, mock_postgres_creds,
                                        mock_mysql_engine, mock_postgres_engine,
                                        mock_get_query, mock_extract_data):
        """Test main function with data extraction failure."""
        # Setup mocks
        mock_mysql_creds.return_value = {"user_mysql": "test"}
        mock_postgres_creds.return_value = {"user_postgres": "test"}
        mock_mysql_engine.return_value = "mysql://connection"
        mock_postgres_engine.return_value = MagicMock()
        mock_get_query.return_value = "SELECT * FROM test"
        mock_extract_data.side_effect = Exception("Database query failed")
        
        with pytest.raises(Exception, match="Database query failed"):
            main()


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_dataframe_loading(self):
        """Test loading an empty DataFrame."""
        empty_df = pd.DataFrame()
        mock_engine = MagicMock()
        empty_df.to_sql = MagicMock()
        
        load_data_to_postgres(empty_df, mock_engine)
        
        empty_df.to_sql.assert_called_once_with('vni_total', mock_engine, if_exists='append', index=False)
    
    def test_credentials_with_empty_values(self):
        """Test credential functions with empty string values."""
        env_vars = {
            "user_mysql": "",
            "password_mysql": "test_pass",
            "host_mysql": "localhost",
            "port_mysql": "3306",
            "db_mysql": "test_db"
        }
        
        with patch.dict(os.environ, env_vars):
            credentials = get_mysql_credentials()
            assert credentials["user_mysql"] == ""
    
    @patch('entrypoint.pd.read_sql')
    def test_extract_data_with_large_dataset(self, mock_read_sql):
        """Test data extraction with a large dataset."""
        # Create a large mock DataFrame
        large_df = pd.DataFrame({
            'col1': range(10000),
            'col2': ['data'] * 10000
        })
        mock_read_sql.return_value = large_df
        
        result = extract_data_from_mysql("connection_string", "query")
        
        assert len(result) == 10000
        assert result.equals(large_df)


if __name__ == "__main__":
    pytest.main([__file__])