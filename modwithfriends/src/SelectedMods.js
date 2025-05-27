import React from 'react';
import './SelectedMods.css';

function SelectedMods({selectedMod}) {
  return (
    <div className='selected-mods-container'>
      <p>{selectedMod["moduleCode"]}</p>
    </div>
  )
}

export default SelectedMods;