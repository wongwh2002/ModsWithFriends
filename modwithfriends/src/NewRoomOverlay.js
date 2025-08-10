import React, { useEffect, useState } from 'react';
import './Overlay.css';
import x from './assets/x.png';
import Days from './Days';

function NewRoomOverlay({setCreateRoom, selectedMods, setRooms, username, body}) {

  const [modList, setModList] = useState([]);
  const [hasSelected, setHasSelected] = useState(false);
  const [loading, setLoading] = useState(false);

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

  const createRoom = async () => {
    setLoading(true);
    if (hasSelected == false) {
      return
    }
    const mods = modList.filter(mod => 
      mod["selected"] == true).map(selected => selected["day"])
    
    const add_module = async (moduleCode) => {
      const groupData = await fetch("https://modswithfriends.onrender.com/add_group", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "session_id" : body,
          "module_id" : moduleCode,
        })
      })
      const groupID = await groupData.json();
      console.log(groupID);
      await fetch ("https://modswithfriends.onrender.com/student_join_group", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "group_id" : groupID["group_id"],
          "student_id" : username,
        })
      })
    }
    
    for (let mod of mods) {
      await add_module(mod);
    }

    const getRoomData = async () => {
      await fetch("https://modswithfriends.onrender.com/get_session_groups", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "session_id" : body,
        })
      }).then(request => request.json())
      .then(data => {
        let mods = selectedMods.map(mod => mod.moduleCode);
        Object.keys(data["groups"]).forEach(key => {
          if (!mods.includes(key)) {
            delete data["groups"][key];
          }
        });
        setRooms(data["groups"])
      });
    }
    await getRoomData();
    setCreateRoom(false);
    setLoading(false);
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
          <button className={hasSelected ? 'create-room' : 'greyed-out create-room'} disabled={loading} onClick = {() => createRoom()}>{loading ? "Creating..." : "Create Room"}</button>
        </div>
      </div>
    </div>
  )
}

export default NewRoomOverlay;