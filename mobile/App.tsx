import React, { useEffect, useState, useMemo } from 'react';
import { StyleSheet, Text, View, FlatList, Dimensions, Platform } from 'react-native';
import MobileMap from './MobileMap';
// Types
interface Venue {
    id: string;
    name: string;
    latitude: number;
    longitude: number;
    capacity: number;
}

const API_URL = Platform.OS === 'web' ? 'http://localhost:8000' : 'http://10.0.2.2:8000'; // Adjust for Android Emulator if needed
const WS_URL = Platform.OS === 'web' ? 'ws://localhost:8000/ws' : 'ws://10.0.2.2:8000/ws';

export default function App() {
    const [venues, setVenues] = useState<Venue[]>([]);
    const [scores, setScores] = useState<Record<string, number>>({});

    // Fetch Venues
    useEffect(() => {
        fetch(`${API_URL}/venues`)
            .then(res => res.json())
            .then(data => setVenues(data))
            .catch(err => console.error("Error fetching venues:", err));
    }, []);

    // Polling for Scores
    useEffect(() => {
        const fetchScores = () => {
            fetch(`${API_URL}/scores`)
                .then(res => res.json())
                .then(data => setScores(data))
                .catch(err => console.error("Error fetching scores:", err));
        };

        fetchScores();
        const interval = setInterval(fetchScores, 5000); // Poll every 5 seconds
        return () => clearInterval(interval);
    }, []);

    const getMarkerColor = (score: number) => {
        if (score >= 70) return 'red';
        if (score >= 30) return 'orange';
        return 'green';
    };

    const sortedVenues = useMemo(() => {
        return [...venues].sort((a, b) => {
            const scoreA = scores[a.id] || 0;
            const scoreB = scores[b.id] || 0;
            return scoreB - scoreA;
        });
    }, [venues, scores]);

    const initialRegion = {
        latitude: 42.9849,
        longitude: -81.2453,
        latitudeDelta: 0.05,
        longitudeDelta: 0.05,
    };

    return (
        <View style={styles.container}>
            {/* Map View */}
            <View style={styles.mapContainer}>
                {Platform.OS === 'web' && (
                    <Text style={styles.webWarning}>On Web, ensure you have a Google Maps API key or use a compatible config for react-native-maps. If map is blank, check console.</Text>
                )}
                <MobileMap
                    venues={venues}
                    scores={scores}
                    getMarkerColor={getMarkerColor}
                />
            </View>

            {/* Bottom Sheet List */}
            <View style={styles.listContainer}>
                <Text style={styles.listHeader}>Venues (Sorted by Hotness)</Text>
                <FlatList
                    data={sortedVenues}
                    keyExtractor={v => v.id}
                    renderItem={({ item }) => (
                        <View style={styles.listItem}>
                            <View>
                                <Text style={styles.venueName}>{item.name}</Text>
                                <Text style={styles.venueCap}>Cap: {item.capacity}</Text>
                            </View>
                            <View style={[styles.scoreBadge, { backgroundColor: getMarkerColor(scores[item.id] || 0) }]}>
                                <Text style={styles.scoreText}>{scores[item.id] || 0}%</Text>
                            </View>
                        </View>
                    )}
                />
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
    },
    mapContainer: {
        flex: 2,
        width: '100%',
    },
    map: {
        width: '100%',
        height: '100%',
    },
    webWarning: {
        position: 'absolute',
        top: 10,
        left: 10,
        zIndex: 100,
        backgroundColor: 'rgba(255,255,255,0.8)',
        padding: 5,
        fontSize: 10
    },
    listContainer: {
        flex: 1,
        backgroundColor: 'white',
        borderTopLeftRadius: 20,
        borderTopRightRadius: 20,
        padding: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 5,
    },
    listHeader: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 10,
    },
    listItem: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
    },
    venueName: {
        fontSize: 16,
        fontWeight: '600',
    },
    venueCap: {
        fontSize: 12,
        color: '#666',
    },
    scoreBadge: {
        paddingHorizontal: 10,
        paddingVertical: 5,
        borderRadius: 12,
    },
    scoreText: {
        color: 'white',
        fontWeight: 'bold',
    },
});
