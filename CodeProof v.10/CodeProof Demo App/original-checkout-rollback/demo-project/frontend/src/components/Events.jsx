import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8001';

function Events({ user }) {
    const [events, setEvents] = useState([]);

    useEffect(() => {
        fetchEvents();
    }, []);

    const fetchEvents = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/events`);
            setEvents(response.data.events);
        } catch (err) {
            console.error('Failed to fetch events:', err);
        }
    };

    return (
        <div>
            <h2>Events</h2>
            <ul>
                {events.map(event => (
                    <li key={event.id}>
                        <strong>{event.title}</strong> - {event.date}
                        <p>{event.description}</p>
                        <p>Capacity: {event.capacity}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Events;
