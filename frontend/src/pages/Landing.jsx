// Landing.jsx
// Assembles all landing page sections in order.

import Navbar from "../components/landing/Navbar";
import Hero from "../components/landing/Hero";
import Stats from "../components/landing/Stats";
import Features from "../components/landing/Features";
import Footer from "../components/landing/Footer";

function Landing() {
  return (
    <div>
      <Navbar />
      <Hero />
      <Stats />
      <Features />
      <Footer />
    </div>
  );
}

export default Landing;