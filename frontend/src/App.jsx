import { useState } from 'react'
import { Routes, Route, Link, useNavigate } from 'react-router-dom'
import About from './pages/About.jsx'
import './App.css'

function signInButton() {
  const [signedIn, setSignedIn] = useState(false)



  return 
}

function App() {
  const [signedIn, setSignedIn] = useState(false)
  
  const navigate = useNavigate()

  function handleNavClick(path) {
    console.log(`${path} was clicked on`)
    navigate(path);
  }

  return (
    <>
      <div className='top-bar'>
        <h1 className='title' onClick={() => handleNavClick("/")}>Avidex</h1>
        <nav className='nav-bar'>
          <h3 className='nav-bar-item' onClick={() => handleNavClick("/About")}>About</h3>
          <h3 className='nav-bar-item'>Avian Compendium</h3>
          <h3 className='nav-bar-item'>Map</h3>
          <h3 className='nav-bar-item'>Badges</h3>
          <h3 className='nav-bar-item'>Your Avidex</h3>
          <button className='nav-bar-button'>Sign In</button>
        </nav>
      </div>

      {
        <Routes>
          <Route path='/' element={
            <div className='opening-title-div'>
              <h1 className='opening-title'>Welcome to Avidex!</h1>
              <hr/>
              <p className='opening-intro'>
                Avidex is a project where you can upload images of birds you've seen, identify them, and earn rewards for doing so!
                <br/>
                <br/>
                This is a project being developed by one person, so it may go slow, but I'll be sure to leave updates. As well as a link to the <a href='https://github.com/AN1H3M/Avidex'>Github page</a> so you can track my progress
              </p>
            </div>
          } />
          <Route path="/About" element = {<About/>} />
        </Routes>
      }
    </>
  )
}

export default App
