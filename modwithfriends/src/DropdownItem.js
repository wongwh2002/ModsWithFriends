import React from 'react';
import './DropdownItem.css';

function DropdownItem({mod}) {
  return (
    <div className='dropdown-item-container'>
      <p>{`${mod["moduleCode"]} ${mod["title"]}`}</p>
    </div>
  )
}

export default DropdownItem;