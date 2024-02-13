import React from 'react';
import {CreateUserCard} from 'src/components/CreateUserCard';
import {GetUserDetailsCard} from 'src/components/GetUserDetailsCard';
import {TransferTokensCard} from 'src/components/TransferTokensCard';

const Home: React.FC = () => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  const defaultBalance = process.env.NEXT_PUBLIC_DEFAULT_BALANCE; 

  return (
    <div className="max-w-sm mx-auto">
      <h1 className="text-3xl font-bold p-6 text-center">Tiny Token</h1>
      <CreateUserCard apiUrl={apiUrl} defaultBalance={defaultBalance} />
      <GetUserDetailsCard apiUrl={apiUrl} />
      <TransferTokensCard apiUrl={apiUrl} />
    </div>
  );
}

export default Home;
