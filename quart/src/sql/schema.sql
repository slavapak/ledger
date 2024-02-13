-- using more verbose forms of DDL to allow support for more databases
CREATE TABLE IF NOT EXISTS users (
  user_id BIGSERIAL,
  balance BIGINT NOT NULL,
  PRIMARY KEY (user_id)
);

-- this table is simply to log transactions
CREATE TABLE IF NOT EXISTS transfers (
  transfer_id BIGSERIAL,
  transfer_timestamp TIMESTAMP DEFAULT current_timestamp,
  user_id_from BIGINT,
  user_id_to BIGINT,
  amount BIGINT NOT NULL
);

-- added two users with some arbit balance just for demo purposes
INSERT INTO users (balance)
SELECT 100 WHERE NOT EXISTS (SELECT user_id FROM users WHERE user_id = 1)
ON CONFLICT (user_id) DO NOTHING;
INSERT INTO users (balance)
SELECT 100 WHERE NOT EXISTS (SELECT user_id FROM users WHERE user_id = 2)
ON CONFLICT (user_id) DO NOTHING;
