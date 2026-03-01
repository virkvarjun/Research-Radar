"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { supabase } from "@/lib/supabase";

/* ─── tiny icon components (no deps needed) ─── */
function IconRadar() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
      <line x1="12" y1="2" x2="12" y2="12" />
    </svg>
  );
}
function IconPapers() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
      <rect x="4" y="3" width="16" height="18" rx="2" />
      <line x1="8" y1="8" x2="16" y2="8" />
      <line x1="8" y1="12" x2="16" y2="12" />
      <line x1="8" y1="16" x2="12" y2="16" />
    </svg>
  );
}
function IconBrain() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
      <path d="M12 2a7 7 0 0 1 7 7c0 2.5-1.3 4.7-3.3 6L14 17h-4l-1.7-2C6.3 13.7 5 11.5 5 9a7 7 0 0 1 7-7z" />
      <line x1="10" y1="20" x2="14" y2="20" />
      <line x1="11" y1="23" x2="13" y2="23" />
    </svg>
  );
}
function IconUniversity() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
      <path d="M2 20h20M4 20V10l8-6 8 6v10" />
      <path d="M9 20v-6h6v6" />
    </svg>
  );
}
function IconChat() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
    </svg>
  );
}
function IconMail() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <polyline points="22,7 12,13 2,7" />
    </svg>
  );
}
function IconShield() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-6 h-6">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <polyline points="9,12 11,14 15,10" />
    </svg>
  );
}
function IconArrowRight() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12,5 19,12 12,19" />
    </svg>
  );
}

/* ─── feature data ─── */
const FEATURES = [
  {
    icon: <IconRadar />,
    title: "Personalized Feed",
    desc: "Papers ranked by your interests, not recency. Every recommendation comes with a transparent explanation of why it matched.",
  },
  {
    icon: <IconUniversity />,
    title: "University Radar",
    desc: "Track your institution's latest output and discover related work from other labs worldwide — powered by OpenAlex.",
  },
  {
    icon: <IconChat />,
    title: "Chat with Papers",
    desc: "Ask questions about any saved paper. Answers are grounded in the actual text with citations — no hallucination.",
  },
  {
    icon: <IconShield />,
    title: "Evidence & Rigour",
    desc: "See datasets, metrics, baselines, code links, and limitations at a glance. Missing evidence is flagged transparently.",
  },
  {
    icon: <IconMail />,
    title: "Daily Digest",
    desc: "Up to 5 top papers delivered to your inbox every morning. One-click Save or Skip — no login required.",
  },
  {
    icon: <IconBrain />,
    title: "Learns from You",
    desc: "Every save, skip, or 'not relevant' updates your interest vector in real time. The more you use it, the better it gets.",
  },
];

const HOW_IT_WORKS = [
  { step: "01", title: "Tell us who you are", desc: "Student, builder, or lab researcher — we tailor paper types to your workflow." },
  { step: "02", title: "Pick your topics", desc: "Select from 12+ research areas or add your own. This seeds your interest graph." },
  { step: "03", title: "Rate some papers", desc: "Interested, neutral, or not interested — 12 anchor papers calibrate your feed instantly." },
  { step: "04", title: "Get your feed", desc: "A personalized stream of papers, ranked by relevance, with transparent scoring." },
];

export default function LandingPage() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        setIsLoggedIn(true);
      } else {
        setIsLoggedIn(false);
      }
    });
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* ──────── NAV ──────── */}
      <header className="fixed top-0 inset-x-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="max-w-6xl mx-auto flex items-center justify-between px-6 h-16">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white text-sm font-bold">
              R
            </div>
            <span className="text-lg font-semibold text-gray-900">Research Radar</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm text-gray-600">
            <a href="#features" className="hover:text-gray-900 transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-gray-900 transition-colors">How it works</a>
            <a href="#evidence" className="hover:text-gray-900 transition-colors">Evidence</a>
          </nav>
          <div className="flex items-center gap-3">
            {isLoggedIn ? (
              <button
                onClick={() => router.push("/feed")}
                className="px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-full hover:bg-blue-700 transition-colors"
              >
                Go to Feed
              </button>
            ) : (
              <>
                <Link
                  href="/login?mode=signin"
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Sign in
                </Link>
                <Link
                  href="/login?mode=signup"
                  className="px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-full hover:bg-blue-700 transition-colors"
                >
                  Get started
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* ──────── HERO ──────── */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-50 text-blue-700 rounded-full text-sm font-medium mb-8">
            <span className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" />
            Powered by OpenAlex & arXiv
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-gray-900 mb-6 leading-[1.1]">
            Research papers,{" "}
            <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 bg-clip-text text-transparent">
              tuned to you
            </span>
          </h1>

          <p className="text-xl text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
            Stop drowning in arXiv. Research Radar learns your interests and delivers a personalized, 
            explainable feed of papers that actually matter to your work.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            {isLoggedIn ? (
              <button
                onClick={() => router.push("/feed")}
                className="group px-8 py-3.5 bg-blue-600 text-white text-base font-medium rounded-full hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/25 flex items-center gap-2"
              >
                Go to your feed
                <IconArrowRight />
              </button>
            ) : (
              <>
                <Link
                  href="/login?mode=signup"
                  className="group px-8 py-3.5 bg-blue-600 text-white text-base font-medium rounded-full hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/25 flex items-center gap-2"
                >
                  Get started — it&apos;s free
                  <IconArrowRight />
                </Link>
                <Link
                  href="/login?mode=signin"
                  className="px-8 py-3.5 bg-gray-100 text-gray-700 text-base font-medium rounded-full hover:bg-gray-200 transition-all"
                >
                  Sign in
                </Link>
              </>
            )}
          </div>

          {/* ── Mini demo visual ── */}
          <div className="mt-16 relative">
            <div className="bg-gradient-to-b from-gray-50 to-white rounded-2xl border border-gray-200 shadow-2xl shadow-gray-200/50 overflow-hidden">
              <div className="bg-gray-800 px-4 py-2.5 flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400" />
                  <div className="w-3 h-3 rounded-full bg-yellow-400" />
                  <div className="w-3 h-3 rounded-full bg-green-400" />
                </div>
                <div className="flex-1 text-center">
                  <span className="text-xs text-gray-400 font-mono">researchradar.dev/feed</span>
                </div>
              </div>
              <div className="p-6 md:p-8 space-y-4">
                {/* Simulated paper cards */}
                {[
                  {
                    title: "Multi-Agent Reinforcement Learning: A Selective Overview",
                    match: "score 0.847 · interest 72% · novelty 100%",
                    tags: ["Multi-Agent Systems", "RL"],
                    evidence: "✅ Datasets  ✅ Limitations  ❌ Code",
                  },
                  {
                    title: "Scaling Vision Transformers to 22B Parameters",
                    match: "score 0.793 · thread 65% · role boost +0.15",
                    tags: ["Computer Vision", "Transformers"],
                    evidence: "✅ Metrics  ✅ Baselines  ✅ Code",
                  },
                  {
                    title: "Constitutional AI: Harmlessness from AI Feedback",
                    match: "score 0.712 · interest 58% · novelty 85%",
                    tags: ["AI Safety", "RLHF"],
                    evidence: "✅ Datasets  ❌ Baselines  ❌ Code",
                  },
                ].map((p, i) => (
                  <div key={i} className="bg-white rounded-xl border border-gray-100 p-4 text-left hover:shadow-md transition-shadow">
                    <h4 className="font-semibold text-gray-900 text-sm mb-1">{p.title}</h4>
                    <p className="text-xs text-gray-400 mb-2">Why matched: {p.match}</p>
                    <div className="flex items-center gap-2 flex-wrap">
                      {p.tags.map((t) => (
                        <span key={t} className="text-xs px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full">{t}</span>
                      ))}
                      <span className="text-xs text-gray-400 ml-auto">{p.evidence}</span>
                    </div>
                    <div className="flex gap-2 mt-3">
                      <span className="px-3 py-1 bg-blue-600 text-white text-xs rounded-md">Save</span>
                      <span className="px-3 py-1 bg-gray-100 text-gray-600 text-xs rounded-md">Skip</span>
                      <span className="px-3 py-1 bg-red-50 text-red-500 text-xs rounded-md">Not relevant</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            {/* Fade at bottom */}
            <div className="absolute bottom-0 inset-x-0 h-24 bg-gradient-to-t from-white to-transparent" />
          </div>
        </div>
      </section>

      {/* ──────── FEATURES ──────── */}
      <section id="features" className="py-24 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Everything you need to stay ahead
            </h2>
            <p className="text-lg text-gray-500 max-w-2xl mx-auto">
              Built for researchers who want signal, not noise. Every feature is designed to save you time.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f, i) => (
              <div
                key={i}
                className="bg-white rounded-2xl border border-gray-100 p-6 hover:shadow-lg hover:border-gray-200 transition-all group"
              >
                <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                  {f.icon}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ──────── HOW IT WORKS ──────── */}
      <section id="how-it-works" className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              From zero to personalized in 2 minutes
            </h2>
            <p className="text-lg text-gray-500">
              A quick onboarding builds your research profile. Then it just gets better.
            </p>
          </div>

          <div className="space-y-0">
            {HOW_IT_WORKS.map((item, i) => (
              <div key={i} className="flex gap-6 items-start relative">
                {/* Line */}
                {i < HOW_IT_WORKS.length - 1 && (
                  <div className="absolute left-6 top-14 w-px h-full bg-gray-200" />
                )}
                {/* Step number */}
                <div className="w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0 relative z-10">
                  {item.step}
                </div>
                <div className="pb-12">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{item.title}</h3>
                  <p className="text-gray-500">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ──────── EVIDENCE / RIGOUR ──────── */}
      <section id="evidence" className="py-24 px-6 bg-gray-50">
        <div className="max-w-5xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Transparency,{" "}
                <span className="text-blue-600">not black boxes</span>
              </h2>
              <p className="text-gray-500 mb-6 leading-relaxed">
                Every paper comes with an evidence panel showing exactly what we found — and what we didn&apos;t. 
                No hidden scores, no unexplained rankings.
              </p>
              <ul className="space-y-3 text-sm">
                {[
                  "Why matched — see the exact scoring breakdown",
                  "Evidence extracted from paper text, not guessed",
                  "\"Not found\" is stated explicitly, never hidden",
                  "Chat answers grounded in citations, not hallucinated",
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3 text-gray-600">
                    <span className="text-blue-600 mt-0.5 flex-shrink-0">✓</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            {/* Panel mockup */}
            <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-lg">
              <h4 className="text-sm font-semibold text-gray-900 mb-4">Evidence / Rigour Panel</h4>
              {[
                { label: "Datasets", icon: "✅", detail: "ImageNet-1K, COCO", found: true },
                { label: "Metrics", icon: "✅", detail: "Top-1 acc: 88.5%, mAP: 63.2", found: true },
                { label: "Baselines", icon: "✅", detail: "ResNet-152, ViT-L/16", found: true },
                { label: "Code Link", icon: "✅", detail: "github.com/research/vit-22b", found: true },
                { label: "Limitations", icon: "❌", detail: "not found in text", found: false },
              ].map((row, i) => (
                <div key={i} className="flex items-center justify-between py-2.5 border-b border-gray-50 last:border-0">
                  <span className="text-sm text-gray-600">{row.label}</span>
                  <div className="flex items-center gap-2 text-xs">
                    <span>{row.icon}</span>
                    <span className={row.found ? "text-gray-500" : "text-gray-400"}>
                      {row.detail}
                    </span>
                  </div>
                </div>
              ))}
              <p className="text-xs text-gray-400 mt-4 pt-3 border-t border-gray-100">
                Evidence extracted from paper text. &quot;Not found&quot; = insufficient evidence.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ──────── BOTTOM CTA ──────── */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Ready to cut through the noise?
          </h2>
          <p className="text-lg text-gray-500 mb-8">
            Join researchers who read smarter, not harder. Set up takes 2 minutes.
          </p>
          {isLoggedIn ? (
            <button
              onClick={() => router.push("/feed")}
              className="group px-8 py-3.5 bg-blue-600 text-white text-base font-medium rounded-full hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/25 inline-flex items-center gap-2"
            >
              Go to your feed
              <IconArrowRight />
            </button>
          ) : (
            <Link
              href="/login?mode=signup"
              className="group px-8 py-3.5 bg-blue-600 text-white text-base font-medium rounded-full hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/25 inline-flex items-center gap-2"
            >
              Get started — it&apos;s free
              <IconArrowRight />
            </Link>
          )}
        </div>
      </section>

      {/* ──────── FOOTER ──────── */}
      <footer className="border-t border-gray-100 py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xs font-bold">
              R
            </div>
            <span>Research Radar</span>
            <span className="mx-2">·</span>
            <span>Personalized research paper discovery</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-400">
            <span>Powered by OpenAlex & arXiv</span>
            <span>·</span>
            <span>No Google Scholar scraping</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
