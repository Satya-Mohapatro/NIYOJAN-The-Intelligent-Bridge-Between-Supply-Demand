import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { AreaChart, Area, ResponsiveContainer, YAxis, Tooltip } from 'recharts';

// --- Icons (Lucide Style) ---
const ZapIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
);

const TargetIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <circle cx="12" cy="12" r="10" />
    <circle cx="12" cy="12" r="6" />
    <circle cx="12" cy="12" r="2" />
  </svg>
);

const BarChartIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <line x1="12" y1="20" x2="12" y2="10" />
    <line x1="18" y1="20" x2="18" y2="4" />
    <line x1="6" y1="20" x2="6" y2="16" />
  </svg>
);

const FileTextIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
    <line x1="10" y1="9" x2="8" y2="9" />
  </svg>
);

const BotIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect x="3" y="11" width="18" height="10" rx="2" />
    <circle cx="12" cy="5" r="2" />
    <path d="M12 7v4" />
    <line x1="8" y1="16" x2="8" y2="16" />
    <line x1="16" y1="16" x2="16" y2="16" />
  </svg>
);

// --- Mock Data for Hero Chart ---
const heroData = Array.from({ length: 20 }, (_, i) => {
  const x = i;
  // Create a realistic looking curve: sigmoid + noise
  const trend = 50 + 40 * (1 / (1 + Math.exp(-(x - 10) / 2)));
  const noise = Math.sin(x * 0.8) * 10;
  return {
    name: `W${i + 1}`,
    historical: i < 14 ? trend + noise : null,
    forecast: i >= 13 ? trend + noise : null, // Overlap slightly
    upper: i >= 13 ? (trend + noise) * 1.2 : null,
    lower: i >= 13 ? (trend + noise) * 0.8 : null,
  };
});

const HeroGraphic = () => {
  return (
    <div className="relative w-full h-[320px] bg-[#0F1014] rounded-2xl border border-white/5 overflow-hidden shadow-2xl shadow-emerald-900/10">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 p-4 border-b border-white/5 flex justify-between items-center z-10 bg-[#0F1014]/80 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-mono uppercase tracking-widest text-emerald-400">Live Forecast</span>
        </div>
        <div className="text-xs text-gray-500 font-medium">Category: Dairy</div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={heroData} margin={{ top: 60, right: 0, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorHist" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorFore" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <Tooltip
            contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px', fontSize: '12px' }}
            itemStyle={{ color: '#e4e4e7' }}
            labelStyle={{ display: 'none' }}
          />
          {/* Uncertainty Band */}
          <Area
            type="monotone"
            dataKey="upper"
            stroke="none"
            fill="#3b82f6"
            fillOpacity={0.1}
            isAnimationActive={true}
            animationDuration={2000}
          />
          {/* Forecast Line */}
          <Area
            type="monotone"
            dataKey="forecast"
            stroke="#3b82f6"
            strokeWidth={2}
            strokeDasharray="4 4"
            fill="url(#colorFore)"
            isAnimationActive={true}
            animationDuration={2000}
            animationBegin={1000}
          />
          {/* Historical Line */}
          <Area
            type="monotone"
            dataKey="historical"
            stroke="#10b981"
            strokeWidth={2}
            fill="url(#colorHist)"
            isAnimationActive={true}
            animationDuration={1500}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Floating Badge */}
      <div className="absolute bottom-6 left-6 px-3 py-2 bg-emerald-500/10 border border-emerald-500/20 backdrop-blur-md rounded-lg flex items-center gap-2">
        <ZapIcon className="w-4 h-4 text-emerald-400" />
        <span className="text-xs font-bold text-emerald-400">Demand Rising +12%</span>
      </div>
    </div>
  );
};

export default function Landing() {
  return (
    <Layout>
      <div className="min-h-screen bg-[#0F1014] text-gray-300 font-sans selection:bg-emerald-500/30">

        {/* --- Hero Section --- */}
        <section className="relative pt-24 pb-32 px-6 lg:px-12 overflow-hidden">
          {/* Background Gradient */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-emerald-600/5 rounded-full blur-3xl -z-10 animate-pulse duration-[5000ms]"></div>

          <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
            {/* Content */}
            <div className="flex flex-col items-start text-left animate-fade-in-up">
              <h1 className="text-5xl lg:text-7xl font-bold text-white tracking-tight mb-6 leading-[1.1]">
                NIYOJAN
                <span className="block text-2xl lg:text-3xl font-light text-gray-400 mt-2 tracking-normal">
                  Kal se kal ka <span className="text-emerald-400 font-medium">Ayojan</span>
                </span>
              </h1>

              <p className="text-lg text-gray-400 mb-8 max-w-lg leading-relaxed">
                The intelligent demand forecasting platform for modern grocery retail.
                Minimize waste, optimize stock, and predict tomorrow, today.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
                <Link
                  to="/login"
                  className="inline-flex justify-center items-center px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl transition-all hover:scale-[1.02] shadow-lg shadow-emerald-900/20"
                >
                  Login to Dashboard
                </Link>
                <a
                  href="#features"
                  className="inline-flex justify-center items-center px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/5 text-white font-medium rounded-xl transition-all"
                >
                  See How It Works
                </a>
              </div>

              <div className="mt-12 flex items-center gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
                  Enterprise Ready
                </span>
                <span className="w-1 h-1 bg-gray-700 rounded-full"></span>
                <span>Secure & Private</span>
                <span className="w-1 h-1 bg-gray-700 rounded-full"></span>
                <span>Explainable AI</span>
              </div>
            </div>

            {/* Hero Graphic */}
            <div className="relative animate-fade-in-up delay-200">
              <HeroGraphic />
              {/* Decorative Elements */}
              <div className="absolute -z-10 -right-10 -bottom-10 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl"></div>
            </div>
          </div>
        </section>

        {/* --- Features Section --- */}
        <section id="features" className="py-24 bg-black/20 border-t border-white/5">
          <div className="max-w-7xl mx-auto px-6 lg:px-12">
            <div className="text-center mb-16 max-w-2xl mx-auto">
              <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">Why <span className="text-emerald-400">NIYOJAN?</span></h2>
              <p className="text-gray-400 text-lg">
                Built for speed and precision. Our AI engines process your sales data locally to ensure maximum privacy and accuracy.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Feature 1 */}
              <div className="p-8 rounded-2xl bg-[#0F1014] border border-white/5 hover:border-emerald-500/30 hover:-translate-y-1 transition-all duration-300 group shadow-lg">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform text-emerald-400">
                  <TargetIcon className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Accurate Forecasting</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Time-aware demand predictions that account for seasonality, holidays, and local trends.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="p-8 rounded-2xl bg-[#0F1014] border border-white/5 hover:border-amber-500/30 hover:-translate-y-1 transition-all duration-300 group shadow-lg">
                <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform text-amber-400">
                  <ZapIcon className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Smart Alerts</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Proactive detection of stock-outs and overstock risks before they impact your bottom line.
                </p>
              </div>

              {/* Feature 3: AI Human Insights (Replaces Category Intelligence) */}
              <div className="p-8 rounded-2xl bg-[#0F1014] border border-white/5 hover:border-blue-500/30 hover:-translate-y-1 transition-all duration-300 group shadow-lg">
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform text-blue-400">
                  <BotIcon className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">AI Human Insights</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Bilingual, human-readable narratives explaining <i>why</i> demand is changing, powered by Gemini Flash.
                </p>
              </div>

              {/* Feature 4 */}
              <div className="p-8 rounded-2xl bg-[#0F1014] border border-white/5 hover:border-purple-500/30 hover:-translate-y-1 transition-all duration-300 group shadow-lg">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform text-purple-400">
                  <FileTextIcon className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Automated Reports</h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Share-ready PDF summaries and CSV exports generated instantly for your stakeholders.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* --- Footer --- */}
        <footer className="py-12 border-t border-white/5 text-center">
          <div className="mb-4">
            <span className="text-xl font-bold text-white tracking-tight">NIYOJAN</span>
          </div>
          <p className="text-gray-500 text-sm mb-6">
            &copy; 2026 Niyojan. Built with care in India <span className="text-base">🇮🇳</span>
          </p>
          <div className="flex justify-center gap-6 text-sm text-gray-600">
            <a href="#" className="hover:text-emerald-400 transition-colors">Privacy</a>
            <a href="#" className="hover:text-emerald-400 transition-colors">Terms</a>
            <a href="#" className="hover:text-emerald-400 transition-colors">Contact</a>
          </div>
        </footer>

      </div>
    </Layout>
  )
}
