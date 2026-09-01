import { useState } from "react";

const BirdCard = ({commonName, species, description, photos}) => {
    // Tracks which photo in the array is currently shown. Starts at 0
    // so the first photo is what displays by default, per the request.
    const [photoIndex, setPhotoIndex] = useState(0);

    const hasPhotos = photos && photos.length > 0;
    // More than one photo is what makes the arrows meaningful -- with
    // zero or one photo there's nothing to scroll between, so the
    // buttons are hidden rather than shown disabled/non-functional
    const hasMultiplePhotos = photos && photos.length > 1;

    // % (modulo) wraps the index around instead of stopping at the ends --
    // clicking "next" on the last photo loops back to the first, and
    // "prev" on the first loops to the last. Adding photos.length before
    // the modulo on goToPrevious keeps the result positive (JS's % can
    // return negative numbers for negative inputs, e.g. -1 % 5 === -1,
    // not 4).
    function goToPrevious() {
        setPhotoIndex((current) => (current - 1 + photos.length) % photos.length);
    }

    function goToNext() {
        setPhotoIndex((current) => (current + 1) % photos.length);
    }

    return (
        <>
        <div className="bird-card">
            <h2 className="bird-name">{commonName}</h2>
            <h3 className="bird-species"><em>{species}</em></h3>

            {/* Renders nothing (collapses to zero height) if photos is
                empty, rather than showing a broken image -- happens for
                any bird whose Wikimedia Commons search in image_pull.py
                came back empty */}
            {hasPhotos && (
                <div className="bird-photo-carousel">
                    {hasMultiplePhotos && (
                        <button
                            type="button"
                            className="bird-photo-nav bird-photo-nav-left"
                            onClick={goToPrevious}
                            aria-label={`Previous photo of ${commonName}`}
                        >
                            &#8249;
                        </button>
                    )}

                    <img
                        src={photos[photoIndex]}
                        alt={`Photo ${photoIndex + 1} of a ${commonName}`}
                        className="bird-image"
                    />

                    {hasMultiplePhotos && (
                        <button
                            type="button"
                            className="bird-photo-nav bird-photo-nav-right"
                            onClick={goToNext}
                            aria-label={`Next photo of ${commonName}`}
                        >
                            &#8250;
                        </button>
                    )}
                </div>
            )}

            <hr className='bird-hr'/>
            <p className='bird-description'>{description}</p>
        </div>
        </>
    )
}

export default BirdCard;