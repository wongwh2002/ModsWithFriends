import React from 'react';
import './Overlay.css';
import x from "./assets/x.png";

function ShareSessionOverlay({setShareSession}) {

  const closeOverlay = () => {
    setShareSession(false);
  }

  return (
    <div className='dim'>
      <div className='share-overlay overlay'> 
        <div className='close'>
          <img src={x} className='x' onClick={closeOverlay}></img>
        </div>
      </div>
    </div>
  )
}

export default ShareSessionOverlay;