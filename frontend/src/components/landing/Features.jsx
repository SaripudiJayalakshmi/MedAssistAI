// Features.jsx
// Grid of feature cards explaining what the platform does.

import { motion } from "framer-motion";
import { FiCpu, FiSearch, FiFileText, FiShield, FiLink, FiLock } from "react-icons/fi";

const features = [
  { icon: FiCpu, title: "Powered by Llama 3", desc: "State-of-the-art language model for accurate, natural medical answers." },
  { icon: FiSearch, title: "Retrieval-Augmented Generation", desc: "Every answer is grounded in real retrieved document context, not guesswork." },
  { icon: FiFileText, title: "Medical PDFs", desc: "Upload trusted medical documents to build your own knowledge base." },
  { icon: FiShield, title: "Trusted Answers", desc: "Strict guardrails prevent the AI from answering outside your documents." },
  { icon: FiLink, title: "Source Citation", desc: "Every answer links back to the exact document it came from." },
  { icon: FiLock, title: "Secure Login", desc: "JWT-based authentication keeps your data and history private." },
];

function Features() {
  return (
    <section id="features" className="bg-[#F8FAFC] py-24">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-slate-800 mb-3">
            Built for Trust & Accuracy
          </h2>
          <p className="text-slate-500 max-w-xl mx-auto">
            Every feature is designed around one principle: never make up medical information.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: (i % 3) * 0.1 }}
                className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#2563EB] to-[#06B6D4] flex items-center justify-center mb-4">
                  <Icon className="text-white" size={22} />
                </div>
                <h3 className="text-lg font-semibold text-slate-800 mb-2">{feature.title}</h3>
                <p className="text-slate-500 text-sm">{feature.desc}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default Features;