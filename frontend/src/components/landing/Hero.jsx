import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { FiActivity, FiHeart, FiCpu } from "react-icons/fi";

function Hero() {
  return (
    <section id="home" className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-[#0F172A] via-[#1E3A8A] to-[#0F172A] pt-20">
      <motion.div className="absolute top-1/4 left-[10%] text-[#38BDF8]/20 text-6xl" animate={{ y: [0, -20, 0] }} transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}>
        <FiHeart />
      </motion.div>

      <motion.div className="absolute top-1/3 right-[12%] text-[#06B6D4]/20 text-7xl" animate={{ y: [0, 20, 0] }} transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}>
        <FiActivity />
      </motion.div>

      <motion.div className="absolute bottom-1/4 left-[20%] text-[#2563EB]/20 text-5xl" animate={{ y: [0, -15, 0] }} transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}>
        <FiCpu />
      </motion.div>

      <div className="relative z-10 max-w-4xl mx-auto text-center px-6">
        <motion.h1 initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }} className="text-5xl md:text-7xl font-extrabold text-white mb-6">
          MedAssist{" "}
          <span className="bg-gradient-to-r from-[#38BDF8] to-[#06B6D4] bg-clip-text text-transparent">AI</span>
        </motion.h1>

        <motion.p initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.15 }} className="text-lg md:text-xl text-slate-300 mb-10 max-w-2xl mx-auto">
          Evidence-Based Medical Question Answering using Llama 3 and Retrieval-Augmented Generation
        </motion.p>

        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.3 }} className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/register" className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-[#2563EB] to-[#06B6D4] text-white font-semibold hover:opacity-90 transition shadow-lg shadow-blue-500/25">
            Get Started
          </Link>
          <a href="#features" className="px-8 py-3.5 rounded-xl border border-white/20 text-white font-semibold hover:bg-white/5 transition">
            Learn More
          </a>
        </motion.div>
      </div>
    </section>
  );
}

export default Hero;
