import React, { useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
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

export default function MobileMap({ venues, scores, getMarkerColor }) {
    // Center on London, ON default
    const position = [42.9849, -81.2453];

    return (
        <View style={styles.container}>
            <MapContainer center={position} zoom={13} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                {venues.map(venue => (
                    <Marker key={venue.id} position={[venue.latitude, venue.longitude]}>
                        <Popup>
                            <strong>{venue.name}</strong><br />
                            Score: {scores[venue.id] || 0}%<br />
                            Capacity: {venue.capacity}
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        height: '100%',
        width: '100%',
    },
});
