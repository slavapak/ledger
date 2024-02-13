from ledger.model import InsufficientFundsException

import json
import logging
from quart.wrappers import Response


HTTP_STATUS_OK = 200
HTTP_STATUS_CREATED = 201
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_SERVER_ERROR = 500


def _ValidatePositiveInt(int_str):
  try:
    number = int(int_str)
    return number > 0, number 
  except:
    return False, None 

def _DisallowDuplicateKeys(pairs):
  result = {}
  for key, val in pairs:
    if key in result:
      raise ValueError("duplicate keys disallowed")
    result[key] = val
  return result


class LedgerAPI:

  def __init__(self, default_balance, sql_client):
    self._default_balance = default_balance
    self._sql_client = sql_client

  async def CreateUser(self):
    try:
      user_id = await self._sql_client.InsertUser(self._default_balance)
      return str(user_id), HTTP_STATUS_CREATED
    except Exception as e:
      logging.exception(e)
      return Response(status=HTTP_STATUS_SERVER_ERROR)

  async def GetUserDetails(self, user_id_str):    
    is_user_id_valid, user_id = _ValidatePositiveInt(user_id_str)
    if not is_user_id_valid:
      return Response(status=HTTP_STATUS_BAD_REQUEST)

    try:
      user = await self._sql_client.FetchUser(user_id)
      if not user:
        return Response(status=HTTP_STATUS_BAD_REQUEST)

      return {
          "userId": user.user_id,
          "balance": user.balance
      }
    except Exception as e:
      logging.exception(e)
      return Response(status=HTTP_STATUS_SERVER_ERROR)

  async def Transfer(self, request):    
    data = await request.get_data()    
    json_data = None
    try:      
      json_data = json.loads(data, object_pairs_hook=_DisallowDuplicateKeys)
      print("data:", data, json_data)
    except ValueError:
      return Response(status=HTTP_STATUS_BAD_REQUEST)
    
    is_ok_user_id_from, user_id_from = _ValidatePositiveInt(
        json_data.get('userIdFrom', ''))
    if not is_ok_user_id_from:
      return Response(status=HTTP_STATUS_BAD_REQUEST)

    is_ok_user_id_to, user_id_to = _ValidatePositiveInt(
        json_data.get('userIdTo', ''))
    if not is_ok_user_id_to:
      return Response(status=HTTP_STATUS_BAD_REQUEST)

    is_ok_amount, amount = _ValidatePositiveInt(json_data.get('amount', ''))
    if not is_ok_amount:
      return Response(status=HTTP_STATUS_BAD_REQUEST)

    if user_id_from == user_id_to:
      return Response(status=HTTP_STATUS_BAD_REQUEST)
    
    try:
      transfer_id = await self._sql_client.Transfer(
          user_id_from, user_id_to, amount)      
      return {"transferId": transfer_id}, HTTP_STATUS_OK
    except ValueError:
      return Response(status=HTTP_STATUS_BAD_REQUEST)
    except InsufficientFundsException:
      return "Insufficient funds.", HTTP_STATUS_BAD_REQUEST
    except Exception as e:
      logging.exception(e)      
      return Response(status=HTTP_STATUS_SERVER_ERROR)
