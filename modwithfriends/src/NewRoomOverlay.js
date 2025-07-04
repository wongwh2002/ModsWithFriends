import React, { useEffect, useState } from 'react';
import './Overlay.css';
import x from './assets/x.png';
import Days from './Days';

function NewRoomOverlay({setCreateRoom, selectedMods, setRooms, username}) {

  const [modList, setModList] = useState([]);
  const [hasSelected, setHasSelected] = useState(false);

  useEffect(() => {
    const moduleCodes = selectedMods.map(mod => ({
      "day" : mod.moduleCode,
      "selected" : false
    }));
    setModList(moduleCodes);
  }, [])

  useEffect(() => {
    let changed = false;
    for (let mod of modList) {
      if (mod["selected"] == true) {
        setHasSelected(true);
        changed = true;
      }
    }
    if (changed == false) {
      setHasSelected(false);
    }
  }, [modList])

  const closeOverlay = () => {
    setCreateRoom(false);
  }

  const createRoom = () => {
    if (hasSelected == false) {
      return
    }
    const mods = modList.filter(mod => 
      mod["selected"] == true).map(selected => selected["day"])
    const roomDetails = 
    {
      "modules": mods,
      "users": [username]
    }
    setRooms(rooms => [...rooms, roomDetails]);
    setCreateRoom(false);
  }

  return (
    <div className='dim'>
      <div className='overlay'> 
        <div className='close'>
          <img src={x} className='x' onClick={closeOverlay}></img>
        </div>
        <div className='selection'>
          <p className='modules'>Modules</p>
          {modList.length === 0 ? <p className='no-mods'>You have not selected any mods yet...</p> : <></>}
          <div className='module-list'>
            {modList.map(mod => {
              return <Days day={mod} setDays={setModList} />
            })}
          </div>
        </div>
        <div className='create-room-container'>
          <button className={hasSelected ? 'create-room' : 'greyed-out create-room'} onClick = {() => createRoom()}>Create Room</button>
        </div>
      </div>
    </div>
  )
}

export default NewRoomOverlay;