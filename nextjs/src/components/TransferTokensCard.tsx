import React, {useState} from 'react';

interface Transfer {
  userIdFrom: number | string
  userIdTo: number | string
  amount: number | string
}

interface TransferTokensCardProps {
  apiUrl : string | undefined;
}

export const TransferTokensCard: React.FC<TransferTokensCardProps> =
    ({ apiUrl }) => {
  const [transfer, setTransfer] = useState<Transfer>(
      {userIdFrom: "", userIdTo: "", amount: ""});
  const [responseMessage, setResponseMessage] = useState<string>("")  

  const transferTokens = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const response = await fetch(`${apiUrl}/transactions`, {
          method: "POST", body: JSON.stringify(transfer)});      
      if (response.status == 200) {
        const json = await response.json();
        const message = `Transferred ${transfer.amount} tokens from
            ${transfer.userIdFrom} to ${transfer.userIdTo} successfully.
            Transfer ID: ${json["transferId"]}`;        
        setResponseMessage(message);        
      } else if (response.status == 400) {
        const data = await response.text();
        setResponseMessage("");        
        alert("Transfer failed: " + (data || "Bad request"));        
      }
    } catch (error) {
      console.log("Transfer tokens error:", error);            
      setResponseMessage("");
      alert(`
          Failed to transfer tokens.
          Are you connected to the correct API url?
          Is backend running?
          You are now using ${apiUrl}`);
    }
  };

  return (
      <form onSubmit={transferTokens} className="mb-6 p-4 bg-slate-200 rounded shadow">
        <label htmlFor="userIdFrom" className="p-2 text-sm">From User with ID: </label>
        <input id="userIdFrom" placeholder="As a starter try value 1"
          value={transfer.userIdFrom}
          onChange={(e) => setTransfer({...transfer, userIdFrom: e.target.value})}
          className="mb-2 p-2 w-full border text-gray-800 border-gray-300 rounded" />
        <br />
        <label htmlFor="userIdTo" className="p-2 text-sm">To User with ID: </label>
        <input id="userIdTo" placeholder="As a starter try value 2"
          value={transfer.userIdTo}
          onChange={(e) => setTransfer({...transfer, userIdTo: e.target.value})}
          className="mb-2 p-2 w-full border text-gray-800 border-gray-300 rounded" />
        <br />
        <label htmlFor="amount" className="p-2 text-sm">Amount: </label>
        <input id="amount" placeholder="As a starter try value 20"
          value={transfer.amount}
          onChange={(e) => setTransfer({...transfer, amount: e.target.value})}
          className="mb-6 p-2 w-full border text-gray-800 border-gray-300 rounded" />
        <button type="submit" className="w-full p-2 text-white bg-blue-500 rounded hover:bg-blue-600">
           Transfer Tokens 
        </button>
        <div className="text-gray-600 mt-4">
          {responseMessage}
        </div>
      </form>
  );
};