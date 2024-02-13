from ledger.model import InsufficientFundsException, User
from ledger.ledger_api import LedgerAPI

import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock

@pytest_asyncio.fixture
async def mock_sql_client():         
  return AsyncMock()

@pytest_asyncio.fixture
async def mock_request():
  return AsyncMock()

@pytest.mark.asyncio
async def test_GetUserDetails_Ok(mock_sql_client):
  mock_sql_client.FetchUser = AsyncMock(return_value=User(1, 100))
  response = await LedgerAPI(100, mock_sql_client).GetUserDetails(1)  
  assert response == {'balance': 100, 'userId': 1}

@pytest.mark.parametrize("invalid_id", [     
  "abc",  # Not numeric.
  "1.1",  # Not an int.
  "0",  # Not positive.
  "1,1",  # Mess.  
  None  # Empty
])
@pytest.mark.asyncio
async def test_GetUserDetails_InvalidUserId(mock_sql_client, invalid_id):
  response = await LedgerAPI(100, mock_sql_client).GetUserDetails(invalid_id)  
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_GetUserDetails_SqlClientReturnsNone(mock_sql_client):
  mock_sql_client.FetchUser = AsyncMock(return_value=None)
  response = await LedgerAPI(100, mock_sql_client).GetUserDetails(1)  
  assert response.status == "400 BAD REQUEST"

@pytest.mark.asyncio
async def test_GetUser_SqlClientRaisesAnException(mock_sql_client):
  mock_sql_client.FetchUser = AsyncMock(side_effect=Exception)
  response = await LedgerAPI(100, mock_sql_client).GetUserDetails(1)  
  assert response.status == "500 INTERNAL SERVER ERROR"

@pytest.mark.asyncio
async def test_CreateUser_Ok(mock_sql_client):  
  mock_sql_client.InsertUser = AsyncMock(return_value=1)
  user_id, status = await LedgerAPI(100, mock_sql_client).CreateUser()
  assert user_id == '1'
  assert status == 201  

@pytest.mark.asyncio
async def test_GetUser_SqlClientRaisesAnException(mock_sql_client):
  mock_sql_client.InsertUser = AsyncMock(side_effect=Exception)
  response = await LedgerAPI(100, mock_sql_client).CreateUser()  
  assert response.status == "500 INTERNAL SERVER ERROR"

@pytest.mark.asyncio
async def test_Transfer_Ok(mock_sql_client, mock_request): 
  mock_sql_client.Transfer = AsyncMock(return_value=1)
  mock_request.get_data = AsyncMock(return_value=json.dumps(
      {"userIdFrom": "2", "userIdTo": "1", "amount": "25"}))
  response_json, status = await LedgerAPI(100, mock_sql_client).Transfer(
      mock_request)
  assert response_json == {'transferId': 1}
  assert status == 200

@pytest.mark.asyncio
async def test_Transfer_UserIdFromIsNotSet(mock_sql_client, mock_request): 
  mock_request.get_data = AsyncMock(return_value=json.dumps(
      {"userIdTo": "1", "amount": "25"}))
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'

@pytest.mark.parametrize("invalid_id", [    
  "abc",  # Not numeric.  
  "1.1",  # Not an int.
  "0",  # Not positive.
  "1,1",  # Mess.
  "",  # Empty.
])
@pytest.mark.asyncio
async def test_Transfer_InvalidUserIdFrom(
  mock_sql_client, mock_request, invalid_id):  
  mock_request.get_data = AsyncMock(return_value=json.dumps(
      {"userIdFrom": f"{invalid_id}", "userIdTo": "1", "amount": "25"}))
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'

@pytest.mark.asyncio
async def test_Transfer_UserIdToIsNotSet(mock_sql_client, mock_request): 
  mock_request.get_data = AsyncMock(return_value=json.dumps(
      {"userIdFrom": "1", "amount": "25"}))
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'

@pytest.mark.parametrize("invalid_id", [    
  "abc",  # Not numeric.  
  "1.1",  # Not an int.
  "0",  # Not positive.
  "1,1",  # Mess.
  "",  # Empty.
])
@pytest.mark.asyncio
async def test_Transfer_InvalidUserIdTo(
  mock_sql_client, mock_request, invalid_id):  
  mock_request.get_data = AsyncMock(return_value=json.dumps(
      {"userIdTo": f"{invalid_id}", "userIdFrom": "1", "amount": "25"}))
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'

@pytest.mark.asyncio
async def test_Transfer_AmountNotSet(mock_sql_client, mock_request): 
  mock_request.get_data = AsyncMock(return_value=json.dumps(
      {"userIdFrom": "1", "userIdTo": "2"}))
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'


@pytest.mark.asyncio
async def test_Transfer_UserIdFromEqualsUserIdTo(mock_sql_client, mock_request): 
  mock_request.get_data = AsyncMock(return_value=json.dumps(
      {"userIdTo": f"1", "userIdFrom": "1", "amount": "25"}))
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'

@pytest.mark.parametrize("invalid_amount", [    
  "abc",  # Not numeric.  
  "1.1",  # Not an int.
  "0",  # Not positive.
  "1,1",  # Mess.
  "",  # Empty.
])
@pytest.mark.asyncio
async def test_Transfer_InvalidAmount(
  mock_sql_client, mock_request, invalid_amount):  
  mock_request.get_data = AsyncMock(return_value=json.dumps(
      {"userIdTo": "2", "userIdFrom": "1", "amount": f"{invalid_amount}"}))
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'

@pytest.mark.asyncio
async def test_Transfer_BodyIsNotJson(mock_sql_client, mock_request):  
  mock_request.get_data = AsyncMock(return_value=
      '"userIdTo": "1", "userIdFrom": "1", "amount": "25"')
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'

@pytest.mark.asyncio
async def test_Transfer_UserIdFromSpecifiedMultipleTimes(
    mock_sql_client, mock_request):  
  mock_request.get_data = AsyncMock(return_value=
      '{"userIdTo": "2", "userIdFrom": "3", "userIdFrom": "1", "amount": "25"}')
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'

@pytest.mark.asyncio
async def test_Transfer_UserIdToSpecifiedMultipleTimes(
    mock_sql_client, mock_request):  
  mock_request.get_data = AsyncMock(return_value=
      '{"userIdTo": "2", "userIdTo": "3", "userIdFrom": "1", "amount": "25"}')
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'

@pytest.mark.asyncio
async def test_Transfer_AmountSpecifiedMultipleTimes(
    mock_sql_client, mock_request):  
  mock_request.get_data = AsyncMock(return_value=
      '{"userIdTo": "2", "userIdFrom": "1", "amount": "25", "amount": "30"}')
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'

@pytest.mark.asyncio
async def test_Transfer_SqlClientRaisesValueError(
    mock_sql_client, mock_request): 
  mock_sql_client.Transfer = AsyncMock(side_effect=ValueError)
  mock_request.get_data = AsyncMock(return_value=json.dumps(
      {"userIdFrom": "2", "userIdTo": "1", "amount": "25"}))
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == '400 BAD REQUEST'

@pytest.mark.asyncio
async def test_Transfer_SqlClientRaisesInsufficientFundsException(
    mock_sql_client, mock_request): 
  mock_sql_client.Transfer = AsyncMock(side_effect=InsufficientFundsException)
  mock_request.get_data = AsyncMock(return_value=json.dumps(
      {"userIdFrom": "2", "userIdTo": "1", "amount": "25"}))
  error_message, response_status = await LedgerAPI(
      100, mock_sql_client).Transfer(mock_request)
  assert error_message == "Insufficient funds."
  assert response_status == 400

@pytest.mark.asyncio
async def test_Transfer_SqlClientRaisesException(mock_sql_client, mock_request): 
  mock_sql_client.Transfer = AsyncMock(side_effect=Exception)
  mock_request.get_data = AsyncMock(return_value=json.dumps(
      {"userIdFrom": "2", "userIdTo": "1", "amount": "25"}))
  response = await LedgerAPI(100, mock_sql_client).Transfer(mock_request)
  assert response.status == "500 INTERNAL SERVER ERROR"