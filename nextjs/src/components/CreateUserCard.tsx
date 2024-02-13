import React, {useState} from 'react';

interface CreateUserCardProps {
  apiUrl : string | undefined;
  defaultBalance : string | undefined;
}

export const CreateUserCard: React.FC<CreateUserCardProps> = (
    {apiUrl, defaultBalance}) => {
  const [responseMessage, setResponseMessage] = useState<string>("")
      
  const createUser = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const response = await fetch(`${apiUrl}/users`, { method: "POST"});
      if (response.status == 201) {
        const data = await response.json();                
        setResponseMessage(
            `User Created Successfully. New user's id is: ${data}`);
      } else throw response;
    } catch (error) {
      console.log("Error during user creation:", error);
      setResponseMessage("");        
      alert(`
          Failed to create a new user.
          Are you connected to the correct API url?
          Is backend running?
          You are now using ${apiUrl}`);
    }
  };

  return (
      <form onSubmit={createUser} className="mb-6 p-4 bg-slate-200 rounded shadow">
        <div className="text-sm text-gray-400 mb-2">
          Create a new user with the default balance of {defaultBalance}.
        </div>
        <button type="submit" className="w-full p-2 text-white bg-blue-500 rounded hover:bg-blue-600">
          Create a New User
        </button>        
        <div className="text-sm text-gray-600 mt-2">
          {responseMessage}
        </div>
      </form>
  );
};