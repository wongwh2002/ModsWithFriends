import React from 'react';
import './DropdownItem.css';

function DropdownItem({mod, selectedMods, setSelectedMods}) {
  
  const addSelectedMods = () => {
    if (selectedMods.includes(mod) == false) {
      setSelectedMods(selectedMods => [...selectedMods, mod]);
    }
  }

  return (
    <div className='dropdown-item-container' onClick={addSelectedMods}>
      <p className='text'>{`${mod["moduleCode"]} ${mod["title"]}`}</p>
    </div>
  )
}

export default DropdownItem;