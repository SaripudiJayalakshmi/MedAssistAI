// Footer.jsx
// Simple footer with branding and social links.

import { FiGithub, FiLinkedin, FiMail } from "react-icons/fi";

function Footer() {
  return (
    <footer id="contact" className="bg-[#0F172A] border-t border-white/10 py-10">
      <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <span className="text-slate-400 text-sm">
          © {new Date().getFullYear()} MedAssist AI. Built as a student capstone project.
        </span>
        <div className="flex items-center gap-5">
          <a href="#" className="text-slate-400 hover:text-white transition" title="GitHub">
            <FiGithub size={20} />
          </a>
          <a href="#" className="text-slate-400 hover:text-white transition" title="LinkedIn">
            <FiLinkedin size={20} />
          </a>
          <a href="#" className="text-slate-400 hover:text-white transition" title="Email">
            <FiMail size={20} />
          </a>
        </div>
      </div>
    </footer>
  );
}

export default Footer;