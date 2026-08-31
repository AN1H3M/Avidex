import { useState, useEffect } from 'react'
import BirdCard from '../components/BirdCard';


export default function Compendium() {
     // Holds the array of bird objects once fetched
    const [birds, setBirds] = useState([])

    // Runs once when the component mounts, fetches the bird list from Flask
    // Fetches all birds from the Flask API and returns them as an array of objects.
    useEffect(() => {
        async function loadBirds() {
            const response = await fetch("http://localhost:8001/api/birds");
            const data = await response.json();
            setBirds(data)
        }

        loadBirds()
    }, [])


    return (
        <>
        <div>
            <p onLoad={() => getBirds}></p>
        </div>
        <div className='search-bar-div'>
            <h3 className='search-bar-title'> Search for a Bird </h3>
            <hr className='search-bar-hb'/>
            <input type='text' className='search-bar'/>
        </div>
        <div className='card-box'>
            {/* .map() renders one BirdCard per fetched bird instead of
                six hardcoded, empty ones. key={bird.birdID} is required
                by React to track each item in the list -- birdID works
                well since it's the table's primary key and unique */}
            {birds.map((bird) => (
                <BirdCard 
                    key={bird.birdID}
                    commonName={bird.commonName}
                    species={bird.species}
                    description={bird.description}
                />
            ))}
        </div>
        </>
    );
}