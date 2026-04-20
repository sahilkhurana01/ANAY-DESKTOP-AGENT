import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Power, PowerOff } from 'lucide-react';

interface SessionControlProps {
    onStart: () => void;
    onEnd: () => void;
}

const SessionControl = ({ onStart, onEnd }: SessionControlProps) => {
    const [isActive, setIsActive] = useState(false);
    const [showModal, setShowModal] = useState(true);

    useEffect(() => {
        // Show modal on first load
        setShowModal(!isActive);
    }, [isActive]);

    const handleStart = () => {
        setIsActive(true);
        setShowModal(false);
        onStart();
    };

    const handleEnd = () => {
        setIsActive(false);
        setShowModal(true);
        onEnd();
    };

    return (
        <>
            {/* Start/End Modal */}
            <AnimatePresence>
                {showModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
                    >
                        <motion.div
                            initial={{ scale: 0.8, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.8, opacity: 0 }}
                            className="relative p-8 rounded-2xl bg-gradient-to-br from-gray-900/90 to-black/90 border border-green-500/30 shadow-2xl"
                        >
                            {/* Glow effect */}
                            <div className="absolute inset-0 rounded-2xl bg-green-500/10 blur-xl" />

                            <div className="relative z-10 flex flex-col items-center gap-6">
                                <h2 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">
                                    ANAY - Your AI Assistant
                                </h2>

                                <p className="text-gray-400 text-center max-w-md">
                                    Click the button below to start your session with ANAY
                                </p>

                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={handleStart}
                                    className="relative group px-12 py-6 rounded-full bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold text-xl shadow-lg shadow-green-500/50 hover:shadow-green-500/70 transition-all duration-300"
                                >
                                    <div className="flex items-center gap-3">
                                        <Power className="w-8 h-8" />
                                        <span>START</span>
                                    </div>

                                    {/* Pulse animation */}
                                    <motion.div
                                        className="absolute inset-0 rounded-full bg-green-400/30"
                                        animate={{
                                            scale: [1, 1.2, 1],
                                            opacity: [0.5, 0, 0.5],
                                        }}
                                        transition={{
                                            duration: 2,
                                            repeat: Infinity,
                                            ease: "easeInOut"
                                        }}
                                    />
                                </motion.button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Floating End Button (shown when active) */}
            <AnimatePresence>
                {isActive && (
                    <motion.button
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0, opacity: 0 }}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={handleEnd}
                        className="fixed bottom-8 right-8 z-40 px-10 py-5 rounded-full bg-gradient-to-r from-red-500 to-rose-600 text-white font-bold text-lg shadow-lg shadow-red-500/50 hover:shadow-red-500/70 transition-all duration-300"
                    >
                        <div className="flex items-center gap-3">
                            <PowerOff className="w-6 h-6" />
                            <span>END</span>
                        </div>
                    </motion.button>
                )}
            </AnimatePresence>
        </>
    );
};

export default SessionControl;
