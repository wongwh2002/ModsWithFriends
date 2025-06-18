import React from 'react';
import './RoomCard.css';

function RoomCard({roomInfo}) {
  return (
    <div className='room-card-container'>
      <p className='mod-title'>{roomInfo["modules"].toString()}</p>
      <div className='participants-wrapper'>
        <div className='participants-container'>
          <p>{roomInfo["users"].toString()}</p>
        </div>
        <button className='room-action'>Join</button>
      </div>
    </div>
  )
}

export default RoomCard;