import bluejay from '../assets/blue-jay.jpg';

const BirdCard = ({commonName, species, description}) => {
    return (
        <>
        <div className="bird-card">
            <h2 className="bird-name">{commonName}</h2>
            <h3 className="bird-species"><em>{species}</em></h3>
            <img src={bluejay} alt={`An image of a ${commonName}`} className="bird-image"/>
            <hr className='bird-hr'/>
            <p className='bird-description'>{description}</p>
        </div>
        </>
    )
}

export default BirdCard;