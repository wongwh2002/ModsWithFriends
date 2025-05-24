import React from 'react';
import './HomePage.css';
import Header from './Header';
import Body from './Body'
import {useState} from 'react';

function HomePage() {

  const [body, setBody] = useState('home');

  return (
    <div className="background-color">
      <Header setBody={setBody}/>
      <Body body={body} />
    </div>
  )
}

export default HomePage;