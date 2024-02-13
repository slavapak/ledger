from dataclasses import dataclass

@dataclass
class User:
  user_id : int
  balance: int

class InsufficientFundsException(Exception):
    pass
