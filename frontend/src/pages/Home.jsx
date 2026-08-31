import { useState } from 'react'

export default function Home() {
    return (
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
    );
}