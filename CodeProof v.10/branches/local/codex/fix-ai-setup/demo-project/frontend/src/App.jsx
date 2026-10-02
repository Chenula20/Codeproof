import React, { useState } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Events from './components/Events';
import Booking from './components/Booking';

function App() {
    const [user, setUser] = useState(null);
    const [view, setView] = useState('login');

    if (!user) {
        if (view === 'register') {
            return <Register onRegister={setUser} onSwitch={() => setView('login')} />;
        }
        return <Login onLogin={setUser} onSwitch={() => setView('register')} />;
    }

    return (
        <div>
            <nav>
                <span>Welcome, {user.username}</span>
                <button onClick={() => setUser(null)}>Logout</button>
            </nav>
            <Events user={user} />
            <Booking user={user} />
        </div>
    );
}

export default App;
