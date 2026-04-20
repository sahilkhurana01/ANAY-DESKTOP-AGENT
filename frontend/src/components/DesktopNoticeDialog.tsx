import { useEffect, useState } from 'react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Monitor, Globe, Brain, Mic, FolderOpen, Settings, Bot, Sparkles } from 'lucide-react';

export const DesktopNoticeDialog = () => {
    const [open, setOpen] = useState(false);

    useEffect(() => {
        // Show the dialog every time the app loads
        setOpen(true);
    }, []);

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogContent className="sm:max-w-[600px] bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border-2 border-cyan-500/30 text-white">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2 text-2xl font-bold text-cyan-400">
                        <Monitor className="w-6 h-6" />
                        🖥️ Desktop Capability Notice
                    </DialogTitle>
                    <DialogDescription className="text-gray-300 space-y-4 pt-4">
                        <div className="flex items-start gap-3 p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                            <Globe className="w-5 h-5 text-blue-400 mt-1 flex-shrink-0" />
                            <div>
                                <p className="font-semibold text-blue-300 mb-1">
                                    You're currently using the web demo of ANAY 🌐🤖
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start gap-3 p-3 bg-purple-500/10 rounded-lg border border-purple-500/20">
                            <Brain className="w-5 h-5 text-purple-400 mt-1 flex-shrink-0" />
                            <div>
                                <p className="text-gray-200">
                                    This version highlights ANAY's AI reasoning, intent understanding, and task planning 🧠✨
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start gap-3 p-3 bg-red-500/10 rounded-lg border border-red-500/20">
                            <Settings className="w-5 h-5 text-red-400 mt-1 flex-shrink-0" />
                            <div>
                                <p className="text-gray-200 mb-2">
                                    Due to browser security limits, features like:
                                </p>
                                <ul className="space-y-1 text-sm text-gray-300 ml-4">
                                    <li className="flex items-center gap-2">
                                        <Mic className="w-4 h-4 text-red-300" />
                                        Voice interaction 🎙️
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <FolderOpen className="w-4 h-4 text-red-300" />
                                        File access 📁
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Settings className="w-4 h-4 text-red-300" />
                                        System control ⚙️
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Bot className="w-4 h-4 text-red-300" />
                                        Automation 🤖
                                    </li>
                                </ul>
                                <p className="text-gray-200 mt-2">are not available here.</p>
                            </div>
                        </div>

                        <div className="flex items-start gap-3 p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                            <Monitor className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                            <div>
                                <p className="text-gray-200">
                                    The <span className="font-bold text-green-300">ANAY Desktop App 🖥️🚀</span> is in development and will unlock full local capabilities with user permission.
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start gap-3 p-3 bg-cyan-500/10 rounded-lg border border-cyan-500/20">
                            <Sparkles className="w-5 h-5 text-cyan-400 mt-1 flex-shrink-0" />
                            <div>
                                <p className="text-gray-200">
                                    This web experience is a <span className="font-bold text-cyan-300">preview-only demo</span> of ANAY's intelligence 👀⚡
                                </p>
                            </div>
                        </div>

                        <div className="text-center pt-2">
                            <button
                                onClick={() => setOpen(false)}
                                className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-semibold rounded-lg transition-all duration-200 shadow-lg hover:shadow-cyan-500/50"
                            >
                                Got it! Let's explore 🚀
                            </button>
                        </div>
                    </DialogDescription>
                </DialogHeader>
            </DialogContent>
        </Dialog>
    );
};
