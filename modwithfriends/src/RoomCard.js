import React from 'react';
import { useState, useEffect } from 'react';
import './RoomCard.css';

function RoomCard({roomID, moduleCode, userList, user, setRooms, body}) {

  const toggleRoom = () => {
    console.log(JSON.stringify({
        "student_id" : user,
        "group_id" : roomID,
      }));
    fetch(`https://modswithfriends.onrender.com/student_${userList.includes(user) ? "leave" : "join"}_group`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "student_id" : user,
        "group_id" : roomID,
      })
    });

    if (userList.length === 1 && userList.includes(user)) {
      fetch("https://modswithfriends.onrender.com/delete_group", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "group_id" : roomID,
        })
      })
      setRooms(prevRooms => {
        const roomsForMod = { ...prevRooms[moduleCode] };
        delete roomsForMod[roomID];

        return {
          ...prevRooms,
          [moduleCode]: roomsForMod
        };
      })
    } else if (userList.length > 1 && userList.includes(user)) {
       setRooms(prevRooms => {
        const roomsForMod = { ...prevRooms[moduleCode] };
        const usersForRoom = roomsForMod[roomID] ? [...roomsForMod[roomID]] : [];
        const index = usersForRoom.indexOf(user);
        usersForRoom.splice(index, 1);
        roomsForMod[roomID] = usersForRoom;

        return {
          ...prevRooms,
          [moduleCode]: roomsForMod
        };
      });
    }else {
      setRooms(prevRooms => {
        const roomsForMod = { ...prevRooms[moduleCode] };
        const usersForRoom = roomsForMod[roomID] ? [...roomsForMod[roomID]] : [];
        usersForRoom.push(user);
        roomsForMod[roomID] = usersForRoom;

        return {
          ...prevRooms,
          [moduleCode]: roomsForMod
        };
      });
    }
  }

  const addDuplicate = async () => {
    const request = await fetch("https://modswithfriends.onrender.com/add_group", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "session_id" : body,
        "module_id" : moduleCode,
      })
    })
    const data = await request.json();
    const groupID = data["group_id"];
    setRooms(prevRooms => ({
      ...prevRooms,
      [moduleCode]: {
        ...prevRooms[moduleCode],
        [groupID]: [user]
      }
    }));
  }

  return (
    <div className='room-wrapper'>
      <div className='room-card-row'>
        <div className='room-grid'>
          <p className='room-name'>{moduleCode}</p>
          {userList.length === 0 ? <p className='empty-room'>The room is currently empty</p> : 
          <div className="users-container">
            {userList.map(user => {
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
        <button className='room-action' onClick={() => toggleRoom()}>{userList.includes(user) ? "Leave" : "Join" }</button>
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
        {/*<div className='add-duplicate-container' onClick={() => addDuplicate()}>
          <p className='plus-sign'>+</p>
        </div>*/}
      </div>
    </div>
  )
}

export default RoomCard;