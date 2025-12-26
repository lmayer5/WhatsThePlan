import React from 'react';
import { StyleSheet, View } from 'react-native';
import MapView, { Marker } from 'react-native-maps';

export default function MobileMap({ venues, scores, getMarkerColor }) {
    const initialRegion = {
        latitude: 42.9849,
        longitude: -81.2453,
        latitudeDelta: 0.05,
        longitudeDelta: 0.05,
    };

    return (
        <MapView style={styles.map} initialRegion={initialRegion}>
            {venues.map(venue => (
                <Marker
                    key={venue.id}
                    coordinate={{ latitude: venue.latitude, longitude: venue.longitude }}
                    title={venue.name}
                    description={`Score: ${scores[venue.id] || 0}%`}
                    pinColor={getMarkerColor(scores[venue.id] || 0)}
                />
            ))}
        </MapView>
    );
}

const styles = StyleSheet.create({
    map: {
        width: '100%',
        height: '100%',
    },
});
