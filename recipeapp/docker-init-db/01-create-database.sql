SELECT 'CREATE DATABASE recipesdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'recipesdb')