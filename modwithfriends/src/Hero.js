import React from 'react';
import './Hero.css';
import hero from'./assets/Hero.png';
import arrow from './assets/arrow.png';


function Body({setCreateSession}) {

  const createSession = () => {
    setCreateSession(true);
  }

  return (
    <div className='body'>
      <div className='hero-content'>
        <p className='p1'>
          ModWithFriends
        </p>
        <p className='p2'>
          Create sessions with friends to input your preferences and modules to take
          together and all your possible timetables will be generated for you.
        </p>
        <button className='hero-button' onClick={createSession}>
          <div className='button-content'>
            <p>
              New Session
            </p>
            <img src={arrow} className='arrow'></img>
          </div>
        </button>
      </div>
      <div className='img-container'>
        <img src={hero} className='hero-img'></img>
      </div>
    </div>
  )
}

export default Body;