import React from 'react';
import './SelectedMods.css';

function SelectedMods({selectedMod, setSelectedMods}) {

  const removeMod = () => {
    setSelectedMods(selectedMods => selectedMods.filter(mod => mod != selectedMod));
  }

  return (
    <div className='selected-mods-container'>
      <p>{selectedMod["moduleCode"]}</p>
      <div className='sm-overlay' onClick={removeMod}>
        <p className='close'>x</p>
      </div>
    </div>
  )
}

export default SelectedMods;