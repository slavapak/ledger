import React, {useState} from 'react';

interface User {
  userId: number | string;
  balance: number | string;
}

interface GetUserDetailsCardProps {
  apiUrl : string | undefined;
}

export const GetUserDetailsCard: React.FC<GetUserDetailsCardProps> =
    ({ apiUrl }) => {
  const [userDetails, setUserDetails] = useState<User>(
      {userId: "", balance: ""});

  const fetchUserDetails = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const response = await fetch(`${apiUrl}/users/${userDetails.userId}`);
      if (response.status == 200) {
        const data = await response.json(); 
        setUserDetails(data);
      } else if (response.status == 400 || response.status == 404) {
        alert("Bad request. Probably User ID is invalid.");
      } else throw response;
    } catch (error) {
      const errorMessage = `
          Failed to fetch user details for user with ID ${userDetails.userId}.
          Are you connected to the correct API url?
          Is backend running?
          You are now using ${apiUrl}`;
      console.log(errorMessage + ":", error);
      alert(errorMessage);
    }
  };

  return (
      <form onSubmit={fetchUserDetails} className="mb-6 p-4 bg-slate-200 rounded shadow">
        <label htmlFor="userId" className="p-2 text-sm">User ID: </label>
        <input id="userId" placeholder="As a starter try value 1"
          value={userDetails.userId}
          onChange={(e) => setUserDetails({...userDetails, userId: e.target.value})}
          className="mb-2 p-2 w-full border text-gray-800 border-gray-300 rounded" />
        <br />
        <label htmlFor="balance" className="p-2 text-sm">Balance: </label>
        <input id="balance" placeholder="Balance" readOnly disabled
          value={userDetails.balance}
          className="mb-6 p-2 w-full border text-gray-800 border-gray-300 rounded" />
        <button type="submit" className="w-full p-2 text-white bg-blue-500 rounded hover:bg-blue-600">
          Get User Details
        </button>
      </form>
  );
};
