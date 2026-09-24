import { useState } from "react";
import { Link } from "react-router-dom";
import { FiMenu, FiX } from "react-icons/fi";

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  const navLinks = [
    { label: "Home", href: "#home" },
    { label: "Features", href: "#features" },
    { label: "Technology", href: "#technology" },
    { label: "About", href: "#about" },
    { label: "Contact", href: "#contact" },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-lg bg-[#0F172A]/80 border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <span className="text-xl font-bold bg-gradient-to-r from-[#38BDF8] to-[#06B6D4] bg-clip-text text-transparent">MedAssist AI</span>

        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <a key={link.href} href={link.href} className="text-slate-300 hover:text-white transition text-sm font-medium">
              {link.label}
            </a>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-3">
          <Link to="/login" className="px-4 py-2 text-sm font-medium text-slate-200 hover:text-white transition">Login</Link>
          <Link to="/register" className="px-5 py-2 rounded-lg bg-gradient-to-r from-[#2563EB] to-[#06B6D4] text-white text-sm font-semibold hover:opacity-90 transition">Get Started</Link>
        </div>

        <button className="md:hidden text-white text-2xl" onClick={() => setMenuOpen(!menuOpen)}>
          {menuOpen ? <FiX /> : <FiMenu />}
        </button>
      </div>

      {menuOpen && (
        <div className="md:hidden bg-[#0F172A] border-t border-white/10 px-6 py-4 space-y-3">
          {navLinks.map((link) => (
            <a key={link.href} href={link.href} className="block text-slate-300 hover:text-white transition" onClick={() => setMenuOpen(false)}>
              {link.label}
            </a>
          ))}
          <div className="flex gap-3 pt-2">
            <Link to="/login" className="flex-1 text-center py-2 rounded-lg border border-white/20 text-white">Login</Link>
            <Link to="/register" className="flex-1 text-center py-2 rounded-lg bg-gradient-to-r from-[#2563EB] to-[#06B6D4] text-white">Get Started</Link>
          </div>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
