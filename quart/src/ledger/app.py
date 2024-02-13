import asyncio
import logging
from ledger.sql_client import PostgreSQLClient
from ledger.ledger_api import LedgerAPI
import os
from quart import Quart, request
from quart_cors import cors
from markupsafe import escape

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
     "[%(asctime)s] - %(filename)s - %(funcName)s - %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


sql_client = PostgreSQLClient(os.environ["DATASOURCE"])
ledger_api = LedgerAPI(int(os.environ["DEFAULT_BALANCE"]), sql_client)
app = Quart(__name__)
app = cors(app, allow_origin="*")


@app.before_serving
async def SetUp():  
  await sql_client.CreateConnectionPool()
  with open(app.root_path + "/" + os.environ["SCHEMA_PATH"]) as file:
    await sql_client.ApplyMigrations(file.read())

@app.after_serving
async def Shutdown():  
  await sql_client.CloseConnectionPool()


@app.post("/users")
async def CreateUser():
  return await ledger_api.CreateUser()

@app.get("/users/<user_id_str>")
async def GetUserDetails(user_id_str):
  return await ledger_api.GetUserDetails(user_id_str)

@app.post("/transactions")
async def Transfer():
  return await ledger_api.Transfer(request)