from ledger.model import InsufficientFundsException, User

import asyncpg


class PostgreSQLClient:

  def __init__(self, datasource_name):
    self._datasource_name = datasource_name
    self._connection_pool = None

  async def ApplyMigrations(self, migration_script):
    async with self._connection_pool.acquire() as connection:
      await connection.execute(migration_script)

  async def CreateConnectionPool(self):
    self._connection_pool = await asyncpg.create_pool(dsn=self._datasource_name)
  
  async def CloseConnectionPool(self):
    await self._connection_pool.close()

  async def InsertUser(self, balance):
    async with self._connection_pool.acquire() as connection:
      return await connection.fetchval(
          "INSERT INTO users (balance) VALUES ($1) RETURNING user_id",
          balance)

  async def FetchUser(self, user_id):
    async with self._connection_pool.acquire() as connection:
      row = await connection.fetchrow(
          "SELECT user_id, balance FROM users WHERE user_id = $1", user_id)
      return User(row["user_id"], row["balance"]) if row else None

  async def Transfer(self, user_id_from, user_id_to, amount):
    async with self._connection_pool.acquire() as connection:
      async with connection.transaction(isolation='repeatable_read'):
        rows = await connection.fetch('''
            SELECT user_id, balance FROM users
            WHERE user_id in ($1, $2) FOR UPDATE NOWAIT''',
            user_id_from, user_id_to)
        user_from, user_to = None, None
        for row in rows:
          if row["user_id"] == user_id_from:
            user_from = User(row["user_id"], row["balance"])
          else:
            user_to = User(row["user_id"], row["balance"])
        if not user_from or not user_to:
          raise ValueError("Invalid arguments.")
        if user_from.balance < amount:
          raise InsufficientFundsException() 

        user_from.balance -= amount
        user_to.balance += amount
        # Execute ordered by user_id to avoid DB deadlock.
        user1, user2 = user_from, user_to
        if user_from.user_id > user_to.user_id:
            user1, user2 = user_to, user_from
        await connection.execute(
            "UPDATE users SET balance = $1 WHERE user_id = $2",
            user1.balance, user1.user_id)
        await connection.execute(
            "UPDATE users SET balance = $1 WHERE user_id = $2",
            user2.balance, user2.user_id)
        return await connection.fetchval('''
            INSERT INTO transfers (user_id_from, user_id_to, amount)
            VALUES ($1, $2, $3) RETURNING transfer_id''',
            user_id_from, user_id_to, amount)
        
