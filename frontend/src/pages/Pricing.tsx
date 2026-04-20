import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Check, Sparkles, Zap, Crown, X } from 'lucide-react';

const Pricing = () => {
    const pricingTiers = [
        {
            name: 'Free Demo',
            price: '$0',
            period: 'forever',
            description: 'Experience ANAY\'s intelligence',
            icon: Sparkles,
            color: 'from-blue-500 to-cyan-500',
            borderColor: 'border-blue-500/30',
            glowColor: 'hover:shadow-blue-500/50',
            features: [
                'AI reasoning & planning',
                'Text-based interaction',
                'Web demo access',
            ],
            unavailable: [
                'Voice interaction 🎙️',
                'File system access 📁',
                'System control ⚙️',
                'Task automation 🤖',
            ],
            buttonText: 'Current Plan',
            popular: false,
        },
        {
            name: 'Desktop Pro',
            price: '$19',
            period: 'per month',
            description: 'Full local capabilities',
            icon: Zap,
            color: 'from-purple-500 to-pink-500',
            borderColor: 'border-purple-500/50',
            glowColor: 'hover:shadow-purple-500/50',
            features: [
                'Everything in Free Demo',
                'Voice interaction 🎙️',
                'File system access 📁',
                'System control ⚙️',
                'Task automation 🤖',
            ],
            unavailable: [],
            buttonText: 'Coming Soon',
            popular: true,
        },
        {
            name: 'Enterprise',
            price: 'Custom',
            period: 'contact us',
            description: 'Tailored for organizations',
            icon: Crown,
            color: 'from-amber-500 to-orange-500',
            borderColor: 'border-amber-500/30',
            glowColor: 'hover:shadow-amber-500/50',
            features: [
                'Everything in Desktop Pro',
                'Custom integrations',
                'Team collaboration',
                'Priority support',
                'Advanced analytics',
            ],
            unavailable: [],
            buttonText: 'Contact Sales',
            popular: false,
        },
    ];

    return (
        <div className="flex-1 overflow-y-auto custom-scrollbar">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <Link to="/" className="text-xs font-orbitron text-muted-foreground hover:text-primary inline-block mb-6">
                    ← Back to ANAY
                </Link>
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-10"
                >
                    <h1 className="text-4xl md:text-5xl font-orbitron font-bold text-cyan-400 mb-4">
                        Choose Your Plan
                    </h1>
                    <p className="text-gray-400 text-lg">
                        Start free or unlock full capabilities with the desktop app
                    </p>
                </motion.div>

                {/* Pricing Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
                    {pricingTiers.map((tier, index) => {
                        const Icon = tier.icon;
                        return (
                            <motion.div
                                key={tier.name}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                                whileHover={{
                                    scale: 1.05,
                                    y: -8,
                                    transition: { duration: 0.3 }
                                }}
                                className={`relative bg-gradient-to-br from-gray-900/50 to-gray-800/50 backdrop-blur-sm rounded-2xl border-2 ${tier.borderColor} p-7 cursor-pointer transition-all duration-300 hover:border-opacity-100 hover:shadow-2xl ${tier.glowColor} ${tier.popular ? 'ring-2 ring-purple-500/50' : ''
                                    }`}
                            >
                                {tier.popular && (
                                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                                        <span className="bg-gradient-to-r from-purple-500 to-pink-500 text-white text-sm font-bold px-5 py-1.5 rounded-full shadow-lg">
                                            MOST POPULAR
                                        </span>
                                    </div>
                                )}

                                {/* Icon */}
                                <motion.div
                                    className={`inline-flex p-4 rounded-xl bg-gradient-to-r ${tier.color} mb-5`}
                                    whileHover={{ rotate: 360, transition: { duration: 0.6 } }}
                                >
                                    <Icon className="w-7 h-7 text-white" />
                                </motion.div>

                                {/* Plan Name */}
                                <h3 className="text-3xl font-orbitron font-bold text-white mb-3">
                                    {tier.name}
                                </h3>

                                {/* Price */}
                                <div className="mb-4">
                                    <span className="text-5xl font-bold text-cyan-400">{tier.price}</span>
                                    {tier.period && (
                                        <span className="text-gray-400 text-base ml-2">/ {tier.period}</span>
                                    )}
                                </div>

                                {/* Description */}
                                <p className="text-gray-400 text-base mb-6">{tier.description}</p>

                                {/* Features */}
                                <div className="space-y-3 mb-4">
                                    {tier.features.map((feature, idx) => (
                                        <motion.div
                                            key={idx}
                                            className="flex items-start gap-3"
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: index * 0.1 + idx * 0.05 }}
                                        >
                                            <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                                            <span className="text-gray-300 text-base leading-relaxed">{feature}</span>
                                        </motion.div>
                                    ))}
                                </div>

                                {/* Unavailable Features */}
                                {tier.unavailable && tier.unavailable.length > 0 && (
                                    <div className="space-y-3 mb-6 pt-4 border-t border-gray-700/50">
                                        <p className="text-sm font-orbitron text-red-400/80 uppercase tracking-wider mb-3">
                                            Not Available in Web
                                        </p>
                                        {tier.unavailable.map((feature, idx) => (
                                            <motion.div
                                                key={idx}
                                                className="flex items-start gap-3"
                                                initial={{ opacity: 0, x: -10 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: index * 0.1 + (tier.features.length + idx) * 0.05 }}
                                            >
                                                <X className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                                                <span className="text-gray-400 text-base leading-relaxed line-through opacity-60">{feature}</span>
                                            </motion.div>
                                        ))}
                                    </div>
                                )}

                                {/* CTA Button */}
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className={`w-full py-4 rounded-lg font-orbitron font-bold text-base transition-all ${tier.popular
                                            ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/50 hover:shadow-purple-500/80'
                                            : 'bg-gray-700/50 text-gray-300 hover:bg-gray-700 hover:shadow-lg'
                                        }`}
                                    disabled={tier.buttonText === 'Current Plan'}
                                >
                                    {tier.buttonText}
                                </motion.button>
                            </motion.div>
                        );
                    })}
                </div>

                {/* Footer Note */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="text-center text-gray-500 text-base mb-8"
                >
                    <p>
                        💡 Desktop App in development - Join our waitlist!
                    </p>
                </motion.div>
            </div>
        </div>
    );
};

export default Pricing;
