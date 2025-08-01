import React from 'react';
import { useState, useEffect } from 'react';
import './RoomCard.css';

function RoomCard({roomInfo, setRoomInfo, user, idx}) {

  const toggleRoom = () => {
    setRoomInfo(prevRooms => {
      const room = prevRooms[idx];
      const isUserInRoom = room.users.includes(user);
      const isOnlyUser = room.users.length === 1;

      if (isUserInRoom && isOnlyUser && !room.isOriginal) {
        return [
          ...prevRooms.slice(0, idx),
          ...prevRooms.slice(idx + 1)
        ];
      }

      return [
        ...prevRooms.slice(0, idx),
        {
          ...room,
          users: isUserInRoom
            ? room.users.filter(u => u !== user)
            : [...room.users, user]
        },
        ...prevRooms.slice(idx + 1)
      ];
    });
  };

  const addDuplicate = () => {
    setRoomInfo(prev => {
      const newRoom = { ...prev[idx], users: [user], isOriginal: false };
      const updated = [...prev.slice(0, idx + 1), newRoom, ...prev.slice(idx + 1)];
      return updated;
    })
  }

  return (
    <div className='room-wrapper'>
      <div className='room-card-row'>
        <div className='room-grid'>
          <p className='room-name'>{roomInfo["module"]}</p>
          {roomInfo["users"].length === 0 ? <p className='empty-room'>The room is currently empty</p> : 
          <div className="users-container">
            {roomInfo["users"].map(user => {
              return (
                <div className='user-icon'>
                  <div className='user-fulltext'>
                    <p className='username'>{user}</p>
                  </div>
                  <p className='user-text'>{user.charAt(0)}</p>
                </div>
              )
            })}
          </div>}
        </div>
        <button className='room-action' onClick={() => toggleRoom()}>{roomInfo["users"].includes(user) ? "Leave" : "Join" }</button>
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
      <div className='dividor'>
        <div className='add-duplicate-container' onClick={() => addDuplicate()}>
          <p className='plus-sign'>+</p>
        </div>
      </div>
    </div>
  )
}

export default RoomCard;