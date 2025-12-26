import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    BarChart, Bar,
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts';
import { LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import MapComponent from './Map';

const Analytics = () => {
    const [data, setData] = useState(null);
    const [venues, setVenues] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    // ID mock
    const venueId = "00000000-0000-0000-0000-000000000001";

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    navigate('/login');
                    return;
                }
                const response = await axios.get(`http://localhost:8000/analytics/${venueId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                setData(response.data);

                // Fetch Venues for Map
                const venuesResp = await axios.get('http://localhost:8000/venues');
                setVenues(venuesResp.data);

            } catch (error) {
                console.error("Error fetching data", error);
                if (error.response && error.response.status === 401) {
                    navigate('/login');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5 seconds

        return () => clearInterval(interval);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    if (loading) return <div className="min-h-screen flex items-center justify-center">Loading Analytics...</div>;

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow">
                <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
                    <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={async () => {
                                if (confirm("Are you sure you want to reset the simulation? This will clear all data.")) {
                                    try {
                                        const token = localStorage.getItem('token');
                                        await axios.post('http://localhost:8000/admin/reset_simulation', {}, {
                                            headers: { 'Authorization': `Bearer ${token}` }
                                        });
                                        alert("Simulation Restarted!");
                                        window.location.reload();
                                    } catch (e) {
                                        alert("Error resetting simulation");
                                        console.error(e);
                                    }
                                }
                            }}
                            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
                        >
                            Restart Simulation
                        </button>
                        <button onClick={handleLogout} className="flex items-center text-gray-500 hover:text-gray-700">
                            <LogOut className="h-5 w-5 mr-2" />
                            Logout
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                {/* Venue Name Header */}
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">
                        {data.venue_name || 'Loading...'}
                    </h2>
                    <p className="text-gray-600">Analytics Dashboard</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                    {/* Line Chart */}
                    <div className="bg-white p-6 rounded-lg shadow col-span-1 md:col-span-2">
                        <h2 className="text-xl font-semibold mb-4 text-gray-800">Friday Night Traffic (7PM - 2AM)</h2>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={data.line_chart}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="time" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Line type="monotone" dataKey="transactions" stroke="#8884d8" activeDot={{ r: 8 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>



                    {/* Radar Chart - Performance vs City Average */}
                    <div className="bg-white p-6 rounded-lg shadow col-span-1 md:col-span-2">
                        <h2 className="text-xl font-semibold mb-4 text-gray-800">Performance vs City Average</h2>
                        <p className="text-sm text-gray-600 mb-4">
                            Comparing your bar's metrics to the city average (shown as 100%). Values above 100% indicate above-average performance.
                        </p>
                        <div className="h-80">
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data.radar_chart}>
                                    <PolarGrid />
                                    <PolarAngleAxis dataKey="metric" />
                                    <PolarRadiusAxis angle={90} domain={[0, 200]} />
                                    <Radar
                                        name={data.venue_name}
                                        dataKey="MyBar"
                                        stroke="#8884d8"
                                        fill="#8884d8"
                                        fillOpacity={0.6}
                                    />
                                    <Radar
                                        name="City Average"
                                        dataKey="CityAvg"
                                        stroke="#82ca9d"
                                        fill="#82ca9d"
                                        fillOpacity={0.3}
                                    />
                                    <Legend />
                                    <Tooltip />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Map Component */}
                    <div className="bg-white p-6 rounded-lg shadow col-span-1 md:col-span-2">
                        <h2 className="text-xl font-semibold mb-4 text-gray-800">Live Campus Map</h2>
                        <div className="h-96 w-full">
                            <MapComponent venues={venues} scores={{}} />
                        </div>
                    </div>

                </div>
            </main>
        </div>
    );
};

export default Analytics;
