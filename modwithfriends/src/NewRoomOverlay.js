import React, { useEffect, useState } from 'react';
import './Overlay.css';
import x from './assets/x.png';
import Days from './Days';

function NewRoomOverlay({setCreateRoom, selectedMods}) {

  const [modList, setModList] = useState([]);

  useEffect(() => {
    const moduleCodes = selectedMods.map(mod => ({
      "day" : mod.moduleCode,
      "selected" : false
    }));
    setModList(moduleCodes);
  }, [])

  const closeOverlay = () => {
    setCreateRoom(false);
  }

  return (
    <div className='dim'>
      <div className='overlay'> 
        <div className='close'>
          <img src={x} className='x' onClick={closeOverlay}></img>
        </div>
        <div className='selection'>
          <p className='module'>Modules</p>
          <div className='module-list'>
            {modList.map(mod => {
              return <Days day={mod} setDays={setModList} />
            })}
          </div>
        </div>
        <div className='create-room-container'>
          <button className='create-room'>Create Room</button>
        </div>
      </div>
    </div>
  )
}

export default NewRoomOverlay;