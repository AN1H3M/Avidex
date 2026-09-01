import { useState, useEffect } from 'react'
import BirdCard from '../components/BirdCard';
import { searchBirds } from '../typesense';

const PAGE_SIZE = 24;

export default function Compendium() {
    // Holds the array of bird objects currently shown, whichever source
    // they came from (paginated browse, or a Typesense search)
    const [birds, setBirds] = useState([])
    const [offset, setOffset] = useState(0)
    const [hasMore, setHasMore] = useState(false)
    const [searchQuery, setSearchQuery] = useState("")

    // Fetches one page of birds from Flask and appends it to what's
    // already shown (rather than replacing), so "Load more" grows the
    // list instead of resetting it
    async function loadMoreBirds() {
        const response = await fetch(`http://localhost:8001/api/birds?limit=${PAGE_SIZE}&offset=${offset}`);
        const data = await response.json();

        setBirds((current) => [...current, ...data.birds]);
        setOffset((current) => current + data.birds.length);
        setHasMore(data.hasMore);
    }

    // Runs once on mount to load the first page -- only when there's no
    // active search, since a search replaces this view entirely
    useEffect(() => {
        if (searchQuery.trim() === "") {
            loadMoreBirds();
        }
    }, [])

    // Debounced search: waits 300ms after the user stops typing before
    // actually querying Typesense, so a fast typist doesn't fire a
    // request on every single keystroke. The cleanup function (the
    // "return () => ...") cancels the pending timeout if searchQuery
    // changes again before it fires.
    useEffect(() => {
        if (searchQuery.trim() === "") {
            return;
        }

        const timeoutId = setTimeout(async () => {
            const results = await searchBirds(searchQuery);
            setBirds(results);
            setHasMore(false); // search results aren't paginated
        }, 300);

        return () => clearTimeout(timeoutId);
    }, [searchQuery])

    // Clearing the search box goes back to the paginated browse view,
    // starting fresh from the first page
    function handleSearchChange(event) {
        const value = event.target.value;
        setSearchQuery(value);

        if (value.trim() === "") {
            setBirds([]);
            setOffset(0);
            loadMoreBirds();
        }
    }

    return (
        <>
        <div className='search-bar-div'>
            <h3 className='search-bar-title'> Search for a Bird </h3>
            <hr className='search-bar-hb'/>
            <input
                type='text'
                className='search-bar'
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder='Try "cardinal"'
            />
        </div>
        <div className='card-box'>
            {birds.map((bird) => (
                <BirdCard 
                    key={bird.birdID}
                    commonName={bird.commonName}
                    species={bird.species}
                    description={bird.description}
                    photos={bird.photos}
                />
            ))}
        </div>

        {/* Only offer "Load more" during the default browse -- searches
            return their own complete result set from Typesense */}
        {searchQuery.trim() === "" && hasMore && (
            <button className='load-more-button' onClick={loadMoreBirds}>
                Load More
            </button>
        )}
        </>
    );
}