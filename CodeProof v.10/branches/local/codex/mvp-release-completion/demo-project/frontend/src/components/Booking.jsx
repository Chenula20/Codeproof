import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8001';

function Booking({ user }) {
    const [bookings, setBookings] = useState([]);
    const [eventId, setEventId] = useState('');
    const [seats, setSeats] = useState(1);

    useEffect(() => {
        fetchBookings();
    }, []);

    const fetchBookings = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/bookings/${user.id}`);
            setBookings(response.data.bookings);
        } catch (err) {
            console.error('Failed to fetch bookings:', err);
        }
    };

    const handleBook = async (e) => {
        e.preventDefault();
        try {
            await axios.post(`${API_URL}/api/bookings`, {
                event_id: parseInt(eventId),
                seats: parseInt(seats)
            });
            fetchBookings();
        } catch (err) {
            alert(err.response?.data?.detail || 'Booking failed');
        }
    };

    return (
        <div>
            <h2>My Bookings</h2>
            <form onSubmit={handleBook}>
                <input
                    type="number"
                    placeholder="Event ID"
                    value={eventId}
                    onChange={(e) => setEventId(e.target.value)}
                />
                <input
                    type="number"
                    placeholder="Seats"
                    value={seats}
                    onChange={(e) => setSeats(e.target.value)}
                    min="1"
                />
                <button type="submit">Book</button>
            </form>
            <ul>
                {bookings.map(booking => (
                    <li key={booking.id}>
                        Event #{booking.event_id} - {booking.seats} seat(s)
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Booking;
