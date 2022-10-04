import React, { useState, useEffect} from 'react';

function LogIn() {

  const [data, setData] = useState([{}]);

  useEffect(() => {
    fetch("/login").then(
      res => res.json()
    ).then(
      data => {
        setData(data)
      }
    )
  }, [])

  return (
    <div className="login">
        <div> 
            
        </div>
    </div>
    
  );
}

export default LogIn;
