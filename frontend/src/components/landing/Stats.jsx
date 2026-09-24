// Stats.jsx
// Three key numbers, animated into view as the user scrolls to them.

import { motion } from "framer-motion";

const stats = [
  { value: "10,000+", label: "Medical Documents" },
  { value: "95%", label: "Accurate Retrieval" },
  { value: "2 Seconds", label: "Average Response" },
];

function Stats() {
  return (
    <section className="bg-[#0F172A] py-16 border-t border-white/10">
      <div className="max-w-5xl mx-auto px-6 grid grid-cols-1 sm:grid-cols-3 gap-8">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }} // only animate the first time it scrolls into view
            transition={{ duration: 0.5, delay: i * 0.1 }}
            className="text-center"
          >
            <p className="text-4xl md:text-5xl font-extrabold bg-gradient-to-r from-[#38BDF8] to-[#06B6D4] bg-clip-text text-transparent mb-2">
              {stat.value}
            </p>
            <p className="text-slate-400">{stat.label}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

export default Stats;