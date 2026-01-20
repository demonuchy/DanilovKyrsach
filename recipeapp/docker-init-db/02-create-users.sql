DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'ivan') THEN
        CREATE USER ivan WITH PASSWORD 'root';
        RAISE NOTICE 'User ivan created';
    ELSE
        RAISE NOTICE 'User ivan already exists';
    END IF;
END $$;

GRANT ALL PRIVILEGES ON DATABASE recipesdb TO ivan;