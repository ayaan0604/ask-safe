import { useState } from 'react'
import { login, signup, getMe, askQuestion } from './api'
import './App.css'
import Navbar from './componenets/navbar'
import LoginPage from './componenets/login-page'
import ChatPage from './componenets/chatpage'


export default function App() {

  const [user, setUser] = useState(null)

  function handleLogin(userData){
    setUser(userData)
  }
  

  return(
    <div className='app'>
        {/* <Navbar/> */}
        {user?(
            <ChatPage user={user}/>
          ):(
            
            <div className="login-container">
              <LoginPage onLogin={handleLogin}/>
            </div>
            
          )

        }
        
    </div>
  )
}