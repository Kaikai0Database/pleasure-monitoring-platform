import React, { createContext, useContext, useState, useEffect, useRef } from 'react';

interface MusicContextType {
    isPlaying: boolean;
    volume: number;
    isMuted: boolean;
    play: () => void;
    pause: () => void;
    toggle: () => void;
    setVolume: (volume: number) => void;
    toggleMute: () => void;
}

const MusicContext = createContext<MusicContextType | undefined>(undefined);

export const useMusicPlayer = () => {
    const context = useContext(MusicContext);
    if (!context) {
        throw new Error('useMusicPlayer must be used within BackgroundMusic');
    }
    return context;
};

export const BackgroundMusic: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [volume, setVolumeState] = useState(0.5);
    const [isMuted, setIsMuted] = useState(false);

    useEffect(() => {
        // Create audio element
        const audio = new Audio('/bgm.mp3');
        audio.loop = true;
        audio.volume = volume;
        audioRef.current = audio;

        // Load saved preferences
        const savedVolume = localStorage.getItem('bgm_volume');
        const savedMuted = localStorage.getItem('bgm_muted');
        const savedPlaying = localStorage.getItem('bgm_playing');

        if (savedVolume) {
            const vol = parseFloat(savedVolume);
            setVolumeState(vol);
            audio.volume = vol;
        }

        if (savedMuted === 'true') {
            setIsMuted(true);
            audio.muted = true;
        }

        // Auto-play if it was playing before (but respect browser autoplay policy)
        if (savedPlaying === 'true') {
            audio.play().catch(() => {
                // Autoplay was prevented, user needs to interact first
                console.log('Autoplay prevented - waiting for user interaction');
            });
        }

        return () => {
            audio.pause();
            audio.src = '';
        };
    }, []);

    const play = () => {
        if (audioRef.current) {
            audioRef.current.play().then(() => {
                setIsPlaying(true);
                localStorage.setItem('bgm_playing', 'true');
            });
        }
    };

    const pause = () => {
        if (audioRef.current) {
            audioRef.current.pause();
            setIsPlaying(false);
            localStorage.setItem('bgm_playing', 'false');
        }
    };

    const toggle = () => {
        if (isPlaying) {
            pause();
        } else {
            play();
        }
    };

    const setVolume = (newVolume: number) => {
        const vol = Math.max(0, Math.min(1, newVolume));
        setVolumeState(vol);
        if (audioRef.current) {
            audioRef.current.volume = vol;
        }
        localStorage.setItem('bgm_volume', vol.toString());
    };

    const toggleMute = () => {
        const newMuted = !isMuted;
        setIsMuted(newMuted);
        if (audioRef.current) {
            audioRef.current.muted = newMuted;
        }
        localStorage.setItem('bgm_muted', newMuted.toString());
    };

    const value: MusicContextType = {
        isPlaying,
        volume,
        isMuted,
        play,
        pause,
        toggle,
        setVolume,
        toggleMute,
    };

    return (
        <MusicContext.Provider value={value}>
            {children}
        </MusicContext.Provider>
    );
};
