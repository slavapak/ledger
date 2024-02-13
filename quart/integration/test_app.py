from ledger.app import app

import asyncpg
import os
import pytest
import pytest_asyncio

async def ExecuteSqlQuery(query):
  connection = await asyncpg.connect(os.environ["DATASOURCE"])  
  rows = await connection.fetch(query)  
  await connection.close()
  return rows

async def CleanSqlTables():
  # Warning: Keep in sync with database schema
  await ExecuteSqlQuery("TRUNCATE users, transfers RESTART IDENTITY")

@pytest_asyncio.fixture
async def http_client():         
  async with app.test_app() as test_app:        
    await CleanSqlTables()    
    yield test_app.test_client()

@pytest.mark.asyncio
async def test_GetUserDetails_Ok(http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")  
  response = await http_client.get(f"/users/1")
  assert response.status == "200 OK"
  json = await response.get_json()
  assert json == {'balance': 100, 'userId': 1}

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_id, expected_status", [    
  ("abc", "400 BAD REQUEST"),  # Not numeric.  
  ("1.1", "400 BAD REQUEST"),  # Not an int.
  ("0", "400 BAD REQUEST"),  # Not positive.
  (";DROP TABLE users;", "400 BAD REQUEST"),  # Mess.
  ("", "404 NOT FOUND"),  # Empty.
])
async def test_GetUserDetails_InvalidUserId(
    http_client, invalid_id, expected_status):   
  response = await http_client.get(f"/users/{invalid_id}")
  assert response.status == expected_status

@pytest.mark.asyncio
async def test_GetUserDetails_UserIdDoesNotExist(http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")
  response = await http_client.get("/users/2")
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_GetUserDetails_MethodNotAllowed(http_client): 
  response = await http_client.patch("/users/1")
  assert response.status == "405 METHOD NOT ALLOWED"
  
  response = await http_client.post("/users/1")
  assert response.status == "405 METHOD NOT ALLOWED"

  response = await http_client.put("/users/1")
  assert response.status == "405 METHOD NOT ALLOWED"
  
  response = await http_client.trace("/users/1")
  assert response.status == "405 METHOD NOT ALLOWED"

@pytest.mark.asyncio
async def test_CreateUser_Ok(http_client):  
  response = await http_client.post("/users")    
  assert response.status == "201 CREATED"  
  assert await response.get_data(True) == '1'

@pytest.mark.asyncio
async def test_CreateUser_MethodNotAllowed(http_client):  
  response = await http_client.get("/users")    
  assert response.status == "405 METHOD NOT ALLOWED"

  response = await http_client.head("/users")    
  assert response.status == "405 METHOD NOT ALLOWED"

  response = await http_client.patch("/users")    
  assert response.status == "405 METHOD NOT ALLOWED"
  
  response = await http_client.put("/users")    
  assert response.status == "405 METHOD NOT ALLOWED"

  response = await http_client.trace("/users")    
  assert response.status == "405 METHOD NOT ALLOWED"

@pytest.mark.asyncio
async def test_Transfer_Ok(http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (2, 200)")
  
  response = await http_client.post(
      "/transactions",
      json={"userIdFrom": "2", "userIdTo": "1", "amount": "25"})  
  
  assert response.status == "200 OK"
  response_json = await response.get_json()
  assert response_json == {'transferId': 1}  

@pytest.mark.asyncio
async def test_Transfer_ChangesSenderBalance(http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (2, 200)")
  
  response = await http_client.post(
      "/transactions",
      json={"userIdFrom": "2", "userIdTo": "1", "amount": "25"})  
    
  sender = await ExecuteSqlQuery("SELECT balance FROM users WHERE user_id = 2")
  assert sender[0]["balance"] == 175

@pytest.mark.asyncio
async def test_Transfer_ChangesReceiverBalance(http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (2, 200)")
  
  response = await http_client.post(
      "/transactions",
      json={"userIdFrom": "2", "userIdTo": "1", "amount": "25"})  
  
  receiver = await ExecuteSqlQuery(
      "SELECT balance FROM users WHERE user_id = 1")
  assert receiver[0]["balance"] == 125  

@pytest.mark.asyncio
async def test_Transfer_MakesARecordOfTransfer(http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (2, 200)")
  
  response = await http_client.post(
      "/transactions",
      json={"userIdFrom": "2", "userIdTo": "1", "amount": "25"})  
    
  transfer = await ExecuteSqlQuery('''
      SELECT user_id_from, user_id_to, amount
      FROM transfers WHERE transfer_id = 1''')
  assert transfer[0]["user_id_from"] == 2
  assert transfer[0]["user_id_to"] == 1
  assert transfer[0]["amount"] == 25

@pytest.mark.asyncio
async def test_Transfer_MethodNotAllowed(http_client):  
  request_json = { "userIdFrom": "2", "userIdTo": "1", "amount": "25" }

  response = await http_client.get("/transactions", json=request_json)
  assert response.status == "405 METHOD NOT ALLOWED"

  response = await http_client.head("/transactions", json=request_json)
  assert response.status == "405 METHOD NOT ALLOWED"

  response = await http_client.patch("/transactions", json=request_json)
  assert response.status == "405 METHOD NOT ALLOWED"
  
  response = await http_client.put("/transactions", json=request_json)
  assert response.status == "405 METHOD NOT ALLOWED"

  response = await http_client.trace("/transactions", json=request_json)
  assert response.status == "405 METHOD NOT ALLOWED"

@pytest.mark.asyncio
async def test_Transfer_UserIdFromIsNotSet(http_client): 
  response = await http_client.post(
      "/transactions", json={"userIdTo": "1", "amount": "25"})  
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_id", [    
  "abc",  # Not numeric.  
  "1.1",  # Not an int.
  "0",  # Not positive.
  ";DROP TABLE users;",  # Mess.
  "",  # Empty.
])
async def test_Transfer_InvalidUserIdFrom(http_client, invalid_id):
  response = await http_client.post(
      "/transactions",
      json={"userIdFrom": invalid_id, "userIdTo": "1", "amount": "25"})  
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_Transfer_UserIdFromDoesNotExist(http_client):   
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (2, 200)")
  response = await http_client.post(
      "/transactions",
      json={"userIdFrom": "3", "userIdTo": "1", "amount": "25"})  
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_Transfer_UserIdToIsNotSet(http_client): 
  response = await http_client.post(
      "/transactions", json={"userIdFrom": "1", "amount": "25"})  
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_id", [  
  "abc",  # Not numeric.  
  "1.1",  # Not an int.
  "0",  # Not positive.
  ";DROP TABLE users;",  # Mess.
  "",  # Empty.
])
async def test_Transfer_InvalidUserIdTo(http_client, invalid_id):   
  response = await http_client.post(
      "/transactions",
      json={"userIdFrom": "2", "userIdTo": invalid_id, "amount": "25"})  
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_Transfer_UserIdToDoesNotExist(http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (2, 200)")
  response = await http_client.post(
      "/transactions",
      json={"userIdFrom": "2", "userIdTo": "3", "amount": "25"})  
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_Transfer_UserIdFromEqualsUserIdTo(http_client): 
  response = await http_client.post(
      "/transactions",
      json={"userIdFrom": "1", "userIdTo": "1", "amount": "25"})  
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_Transfer_AmountNotSet(http_client): 
  response = await http_client.post(
      "/transactions", json={"userIdFrom": "2", "userIdTo": "1"})
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_amount", [  
  "abc",  # Not numeric.  
  "1.1",  # Not an int.
  "0",  # Not positive.
  ";DROP TABLE users;",  # Mess.
  "",  # Empty.
])
async def test_Transfer_InvalidAmount(http_client, invalid_amount):   
  response = await http_client.post(
      "/transactions",
      json={"userIdFrom": "2", "userIdTo": "2", "amount": invalid_amount})  
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_Transfer_AmountLargerThanFromUserBalance(http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 10)")
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (2, 20)")
  
  response = await http_client.post(
      "/transactions",
      json={"userIdFrom": "2", "userIdTo": "1", "amount": "25"})
  
  assert response.status == "400 BAD REQUEST"
  response_json = await response.get_data(True)
  assert response_json == "Insufficient funds."

@pytest.mark.asyncio
async def test_Transfer_AmountSpecifiedMultipleTimes(http_client): 
  response = await http_client.post(
      "/transactions",
      data='''{"userIdFrom": "2", "userIdTo": "1", "amount": "25",
              "amount": "50"}''')
  assert response.status == "400 BAD REQUEST"  

@pytest.mark.asyncio
async def test_Transfer_UserIdFromSpecifiedMultipleTimes(http_client): 
  response = await http_client.post(
      "/transactions",
      data='''{"userIdFrom": "2", "userIdFrom": "2", "userIdTo": "1",
              "amount": "50"}''')
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_Transfer_UserIdToSpecifiedMultipleTimes(http_client): 
  response = await http_client.post(
      "/transactions",
      data='''{"userIdFrom": "2", "userIdTo": "3", "userIdTo": "1",
              "amount": "50"}''')
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_Transfer_BodyIsNotJson(http_client): 
  response = await http_client.post(
      "/transactions",
      data='"userIdFrom": "2", "userIdTo": "1", "amount": "50"')
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_Transfer_OnConcurrentTransaction_Bounces(http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (2, 200)")
  
  connection = await asyncpg.connect(os.environ["DATASOURCE"])
  async with connection.transaction():
    await connection.execute(
        "UPDATE users SET balance = 200 WHERE user_id = 1")    
    response = await http_client.post(
        "/transactions",
       json={"userIdFrom": "2", "userIdTo": "1", "amount": "25"})  
    
    assert response.status == "500 INTERNAL SERVER ERROR"

@pytest.mark.asyncio
async def test_Transfer_OnConcurrentTransaction_DoesNotChangeSenderBalance(
  http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (2, 200)")
  
  connection = await asyncpg.connect(os.environ["DATASOURCE"])
  async with connection.transaction():
    await connection.execute(
        "UPDATE users SET balance = 200 WHERE user_id = 1")    
    response = await http_client.post(
        "/transactions",
       json={"userIdFrom": "2", "userIdTo": "1", "amount": "25"})  
  
  sender = await ExecuteSqlQuery("SELECT balance FROM users WHERE user_id = 2")
  assert sender[0]["balance"] == 200

@pytest.mark.asyncio
async def test_Transfer_OnConcurrentTransaction_DoesNotChangeRecieverBalance(
  http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (2, 200)")
  
  connection = await asyncpg.connect(os.environ["DATASOURCE"])
  async with connection.transaction():
    await connection.execute(
        "UPDATE users SET balance = 200 WHERE user_id = 1")    
    response = await http_client.post(
        "/transactions",
       json={"userIdFrom": "2", "userIdTo": "1", "amount": "25"})  
  
  sender = await ExecuteSqlQuery("SELECT balance FROM users WHERE user_id = 2")
  assert sender[0]["balance"] == 200

@pytest.mark.asyncio
async def test_Transfer_OnConcurrentTransaction_DoesNotCreateRecordOfTransfer(
  http_client): 
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (1, 100)")
  await ExecuteSqlQuery("INSERT INTO users (user_id, balance) VALUES (2, 200)")
  
  connection = await asyncpg.connect(os.environ["DATASOURCE"])
  async with connection.transaction():
    await connection.execute(
        "UPDATE users SET balance = 200 WHERE user_id = 1")    
    response = await http_client.post(
        "/transactions",
       json={"userIdFrom": "2", "userIdTo": "1", "amount": "25"})  
    
  transfer = await ExecuteSqlQuery("SELECT user_id_from FROM transfers")
  assert not transfer