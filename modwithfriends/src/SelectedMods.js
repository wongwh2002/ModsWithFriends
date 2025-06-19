import React from 'react';
import './SelectedMods.css';
import bin from './assets/bin.png';

function SelectedMods({selectedMod, setSelectedMods}) {

  const removeMod = () => {
    setSelectedMods(selectedMods => selectedMods.filter(mod => mod != selectedMod));
  }

  return (
    <div className='selected-mods-container'>
      <p className='mod-name'>{selectedMod["moduleCode"]}</p>
      <p className='mod-description'>{selectedMod["title"]}</p>
      <div className='bin-container' onClick={removeMod}>
        <img className='bin' src={bin} />
      </div>
    </div>
  )
}

export default SelectedMods;