import { useState } from 'react'
import { Routes, Route, Link, useNavigate } from 'react-router-dom'
import NavBar from '../src/components/NavBar.jsx'
import About from './pages/About.jsx'
import Home from './pages/Home.jsx'
import Compendium from './pages/Compendium.jsx'
import './App.css'



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
          <h3 className='nav-bar-item' onClick={() => handleNavClick("/Compendium")}>Compendium</h3>
          <h3 className='nav-bar-item'>Map</h3>
          <h3 className='nav-bar-item'>Badges</h3>
          <h3 className='nav-bar-item'>Your Avidex</h3>
        </nav>
      </div>

      {
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path="/About" element = {<About/>} />
          <Route path = '/Compendium' element={<Compendium />}/>
        </Routes>
      }
    </>
  )
}

export default App