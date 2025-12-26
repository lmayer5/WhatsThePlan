import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

let DefaultIcon = L.icon({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const MapComponent = ({ venues = [], scores = {} }) => {
    // Default center (London, ON)
    const position = [42.9849, -81.2453];

    return (
        <div className="h-full w-full rounded-lg overflow-hidden shadow-lg z-0">
            <MapContainer center={position} zoom={13} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                {venues.map(venue => {
                    if (venue.latitude == null || venue.longitude == null) return null;
                    return (
                        <Marker key={venue.id} position={[venue.latitude, venue.longitude]}>
                            <Popup>
                                <div className="text-center">
                                    <h3 className="font-bold">{venue.name}</h3>
                                    <div className="mt-1">
                                        <span className={`px-2 py-1 rounded text-white text-xs ${(scores[venue.id] || 0) > 70 ? 'bg-red-500' :
                                            (scores[venue.id] || 0) > 30 ? 'bg-orange-500' : 'bg-green-500'
                                            }`}>
                                            Hotness: {scores[venue.id] || 0}%
                                        </span>
                                    </div>
                                </div>
                            </Popup>
                        </Marker>
                    );
                })}
            </MapContainer>
        </div>
    );
};

export default MapComponent;
