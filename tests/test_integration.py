import pytest
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from entrypoint import main


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.mark.integration
    def test_full_workflow_with_mocked_databases(self):
        """Test the complete workflow with mocked database connections."""
        # Set up environment variables
        env_vars = {
            "user_mysql": "test_user",
            "password_mysql": "test_pass",
            "host_mysql": "localhost",
            "port_mysql": "3306",
            "db_mysql": "test_db",
            "user_postgres": "pg_user",
            "password_postgres": "pg_pass",
            "host_postgres": "localhost",
            "port_postgres": "5432",
            "db_postgres": "pg_db"
        }
        
        # Mock data that would be returned from MySQL
        mock_data = pd.DataFrame({
            'timestamp': ['2024-01-01 12:00:00'],
            'day_': ['2024-01-01'],
            'rides': [100],
            'avg_rides_per_bike': [5.0],
            'revenue_per_sim': [50.0],
            'avg_ride_price': [2.5],
            'bonus_revenue': [10.0],
            'revenue': [240.0],
            'revenue_without_bonus': [230.0],
            'revenue_from_subscription': [20.0],
            'revenue_without_bonus_plus_revenue_from_subscription': [250.0],
            'vni': [1000.0],
            'vni_without_bonus': [990.0],
            'revenue_paytabs': [150.0],
            'total_paytabs': [1500.0],
            'revenue_stripe': [90.0],
            'total_stripe': [900.0],
            'total_paytabs_plus_total_stripe': [2400.0],
            'kvt': [20],
            'user_per_day': [15],
            'user_total': [1500],
            'total_time_min': [300.0],
            'avg_time_of_ride': [3.0],
            'count_rides_of_new_user_who_reg_today': [5],
            'total_count_rides_of_new_user_who_reg_today': [8],
            'pervasion': [33.33],
            'count_rides_per_count_new_users': [1.6]
        })
        
        with patch.dict(os.environ, env_vars):
            with patch('entrypoint.pd.read_sql') as mock_read_sql:
                with patch('entrypoint.create_engine') as mock_create_engine:
                    # Setup mocks
                    mock_read_sql.return_value = mock_data
                    mock_postgres_engine = MagicMock()
                    mock_create_engine.return_value = mock_postgres_engine
                    
                    # Mock the to_sql method on the DataFrame
                    with patch.object(mock_data, 'to_sql') as mock_to_sql:
                        # Execute main function
                        main()
                        
                        # Verify that data was read from MySQL
                        mock_read_sql.assert_called_once()
                        
                        # Verify that PostgreSQL engine was created
                        mock_create_engine.assert_called_once()
                        
                        # Verify that data was written to PostgreSQL
                        mock_to_sql.assert_called_once_with(
                            'vni_total', 
                            mock_postgres_engine, 
                            if_exists='append', 
                            index=False
                        )
    
    @pytest.mark.integration
    def test_error_handling_in_full_workflow(self):
        """Test error handling in the complete workflow."""
        # Set up environment variables
        env_vars = {
            "user_mysql": "test_user",
            "password_mysql": "test_pass",
            "host_mysql": "localhost",
            "port_mysql": "3306",
            "db_mysql": "test_db",
            "user_postgres": "pg_user",
            "password_postgres": "pg_pass",
            "host_postgres": "localhost",
            "port_postgres": "5432",
            "db_postgres": "pg_db"
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('entrypoint.pd.read_sql') as mock_read_sql:
                # Simulate a database connection error
                mock_read_sql.side_effect = Exception("Connection timeout")
                
                # The main function should raise the exception
                with pytest.raises(Exception, match="Connection timeout"):
                    main()
    
    def test_missing_environment_variables_integration(self):
        """Test integration with missing environment variables."""
        # Clear all environment variables
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Environment variable .* is not set"):
                main()
    
    @pytest.mark.integration
    def test_data_validation(self):
        """Test that the extracted data has the expected structure."""
        from entrypoint import get_vni_query
        
        query = get_vni_query()
        
        # Check that the query contains all expected columns
        expected_columns = [
            'timestamp', 'day_', 'rides', 'avg_rides_per_bike', 'revenue_per_sim',
            'avg_ride_price', 'bonus_revenue', 'revenue', 'revenue_without_bonus',
            'revenue_from_subscription', 'revenue_without_bonus_plus_revenue_from_subscription',
            'vni', 'vni_without_bonus', 'revenue_paytabs', 'total_paytabs',
            'revenue_stripe', 'total_stripe', 'total_paytabs_plus_total_stripe',
            'kvt', 'user_per_day', 'user_total', 'total_time_min', 'avg_time_of_ride',
            'count_rides_of_new_user_who_reg_today', 'total_count_rides_of_new_user_who_reg_today',
            'pervasion', 'count_rides_per_count_new_users'
        ]
        
        for column in expected_columns:
            assert f"'{column}'" in query or f'AS {column}' in query or f'AS \'{column}\'' in query


if __name__ == "__main__":
    pytest.main([__file__])