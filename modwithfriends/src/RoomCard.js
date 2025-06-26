import React from 'react';
import './RoomCard.css';

function RoomCard({roomInfo}) {
  return (
    <div className='room-wrapper'>
      <div className='room-card-row'>
        <div className='room-grid'>
          <p className='room-name'>{roomInfo["module"]}</p>
          <p className={roomInfo["users"].length === 0 ? 'empty-room' : ''}>{roomInfo["users"].length === 0 ? "The room is currently empty" : "Nigel"}</p>
        </div>
        <button className='room-action'>Join</button>
      {/*<div className='room-card-container'>
        <p className='mod-title'>{roomInfo["modules"].join(", ")}</p>
        <div className='participants-wrapper'>
          <div className='participants-container'>
            <p>{roomInfo["users"].join(", ")}</p>
          </div>
          <button className='room-action'>Join</button>
        </div>
      </div>*/}
      </div>
      <div className='dividor'></div>
    </div>
  )
}

export default RoomCard;