import React from 'react';
import './DropdownItem.css';

function DropdownItem({mod, setSelectedMods}) {
  
  const addSelectedMods = () => {
    setSelectedMods(selectedMods => [...selectedMods, mod]);
  }

  return (
    <div className='dropdown-item-container' onClick={addSelectedMods}>
      <p className='text'>{`${mod["moduleCode"]} ${mod["title"]}`}</p>
    </div>
  )
}

export default DropdownItem;