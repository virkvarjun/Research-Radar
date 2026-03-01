"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  submitOnboarding,
  getAnchorPapers,
  getPairwisePapers,
  type Paper,
} from "@/lib/api";

const ROLES = [
  {
    id: "student",
    label: "Student / Early researcher",
    desc: "Surveys, tutorials, and foundational papers to build your knowledge base.",
    emoji: "🎓",
  },
  {
    id: "builder",
    label: "Builder / Engineer",
    desc: "Papers with code, practical applications, and implementation details.",
    emoji: "🛠️",
  },
  {
    id: "lab",
    label: "Lab Researcher",
    desc: "Cutting-edge methods, datasets, baselines, and reproducibility details.",
    emoji: "🔬",
  },
];

const TOPICS = [
  "Machine Learning",
  "Natural Language Processing",
  "Computer Vision",
  "Robotics",
  "Reinforcement Learning",
  "Graph Neural Networks",
  "Generative Models",
  "Optimization",
  "Bayesian Methods",
  "Speech Recognition",
  "Multi-Agent Systems",
  "Bioinformatics",
];

const LABEL_OPTIONS = [
  { value: "interested", label: "Interested", color: "bg-blue-600 text-white border-blue-600" },
  { value: "neutral", label: "Neutral", color: "bg-gray-100 text-gray-700 border-gray-200" },
  {
    value: "not_interested",
    label: "Not for me",
    color: "bg-red-50 text-red-600 border-red-200",
  },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [role, setRole] = useState("");
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [customTopic, setCustomTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Step 3
  const [anchorPapers, setAnchorPapers] = useState<Paper[]>([]);
  const [anchorLabels, setAnchorLabels] = useState<Record<string, string>>({});
  const [anchorLoading, setAnchorLoading] = useState(false);

  // Step 4
  const [pairwisePairs, setPairwisePairs] = useState<
    { paper_a: Paper; paper_b: Paper }[]
  >([]);
  const [pairwiseChoices, setPairwiseChoices] = useState<
    { winner_id: string; loser_id: string }[]
  >([]);
  const [currentPair, setCurrentPair] = useState(0);
  const [pairwiseLoading, setPairwiseLoading] = useState(false);

  const totalSteps = 4;

  function toggleTopic(topic: string) {
    setSelectedTopics((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]
    );
  }

  function addCustomTopic() {
    const t = customTopic.trim();
    if (t && !selectedTopics.includes(t)) {
      setSelectedTopics((prev) => [...prev, t]);
      setCustomTopic("");
    }
  }

  useEffect(() => {
    if (step === 3 && anchorPapers.length === 0) {
      setAnchorLoading(true);
      getAnchorPapers()
        .then((papers) => setAnchorPapers(papers))
        .catch(() =>
          setError("Could not load anchor papers. You can skip this step.")
        )
        .finally(() => setAnchorLoading(false));
    }
  }, [step, anchorPapers.length]);

  useEffect(() => {
    if (step === 4 && pairwisePairs.length === 0) {
      setPairwiseLoading(true);
      getPairwisePapers()
        .then((pairs) => setPairwisePairs(pairs))
        .catch(() =>
          setError("Could not load comparisons. You can skip this step.")
        )
        .finally(() => setPairwiseLoading(false));
    }
  }, [step, pairwisePairs.length]);

  function setAnchorLabel(paperId: string, label: string) {
    setAnchorLabels((prev) => ({ ...prev, [paperId]: label }));
  }

  function choosePairwise(winnerId: string, loserId: string) {
    setPairwiseChoices((prev) => [
      ...prev,
      { winner_id: winnerId, loser_id: loserId },
    ]);
    setCurrentPair((prev) => prev + 1);
  }

  async function handleComplete() {
    setLoading(true);
    setError("");
    try {
      await submitOnboarding({
        role,
        topics: selectedTopics,
        anchor_labels: anchorLabels,
        pairwise_choices: pairwiseChoices,
      });
      router.push("/feed");
    } catch {
      router.push("/feed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white text-sm font-bold mx-auto mb-4">
            R
          </div>
          <h1 className="text-xl font-bold text-gray-900">
            Let&apos;s personalize your feed
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Step {step} of {totalSteps}
          </p>
        </div>

        {/* Progress bar */}
        <div className="w-full max-w-md mx-auto bg-gray-200 rounded-full h-1 mb-8">
          <div
            className="bg-blue-600 h-1 rounded-full transition-all duration-300"
            style={{ width: `${(step / totalSteps) * 100}%` }}
          />
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-xl mb-6 text-sm max-w-md mx-auto text-center">
            {error}
          </div>
        )}

        <div className="bg-white rounded-2xl border border-gray-200 p-6 md:p-8 shadow-sm">
          {/* ── Step 1: Role ── */}
          {step === 1 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-1">
                What best describes you?
              </h2>
              <p className="text-sm text-gray-400 mb-6">
                This helps us prioritize the right types of papers.
              </p>
              <div className="space-y-3">
                {ROLES.map((r) => (
                  <button
                    key={r.id}
                    onClick={() => setRole(r.id)}
                    className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                      role === r.id
                        ? "border-blue-500 bg-blue-50 shadow-sm"
                        : "border-gray-100 hover:border-gray-200 hover:bg-gray-50"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl mt-0.5">{r.emoji}</span>
                      <div>
                        <p className="font-medium text-gray-900">{r.label}</p>
                        <p className="text-sm text-gray-500 mt-0.5">{r.desc}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
              <button
                onClick={() => setStep(2)}
                disabled={!role}
                className="mt-8 w-full py-3 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-40 transition-colors"
              >
                Continue
              </button>
            </div>
          )}

          {/* ── Step 2: Topics ── */}
          {step === 2 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-1">
                What are you researching?
              </h2>
              <p className="text-sm text-gray-400 mb-6">
                Select all that apply, or add your own.
              </p>
              <div className="flex flex-wrap gap-2 mb-6">
                {TOPICS.map((topic) => (
                  <button
                    key={topic}
                    onClick={() => toggleTopic(topic)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      selectedTopics.includes(topic)
                        ? "bg-blue-600 text-white shadow-sm"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                  >
                    {topic}
                  </button>
                ))}
                {/* Show custom topics that were added */}
                {selectedTopics
                  .filter((t) => !TOPICS.includes(t))
                  .map((t) => (
                    <button
                      key={t}
                      onClick={() => toggleTopic(t)}
                      className="px-4 py-2 rounded-full text-sm font-medium bg-blue-600 text-white shadow-sm"
                    >
                      {t} ×
                    </button>
                  ))}
              </div>

              <div className="flex gap-2 mb-8">
                <input
                  type="text"
                  value={customTopic}
                  onChange={(e) => setCustomTopic(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      addCustomTopic();
                    }
                  }}
                  placeholder="Add a custom topic…"
                  className="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50"
                />
                <button
                  onClick={addCustomTopic}
                  className="px-5 py-2.5 bg-gray-100 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors"
                >
                  Add
                </button>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setStep(1)}
                  className="flex-1 py-3 bg-gray-100 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={() => setStep(3)}
                  disabled={selectedTopics.length === 0}
                  className="flex-1 py-3 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-40 transition-colors"
                >
                  Continue
                </button>
              </div>
            </div>
          )}

          {/* ── Step 3: Anchor Papers ── */}
          {step === 3 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-1">
                Rate these papers
              </h2>
              <p className="text-sm text-gray-400 mb-6">
                This calibrates your feed. Quick gut reactions are perfect.
              </p>

              {anchorLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : anchorPapers.length === 0 ? (
                <p className="text-gray-400 text-center py-12 text-sm">
                  No anchor papers available yet. You can skip this step.
                </p>
              ) : (
                <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
                  {anchorPapers.map((paper) => (
                    <div
                      key={paper.id}
                      className={`border rounded-xl p-4 transition-colors ${
                        anchorLabels[paper.id]
                          ? "border-gray-200 bg-gray-50"
                          : "border-gray-100"
                      }`}
                    >
                      <p className="font-medium text-gray-900 text-sm mb-1">
                        {paper.title}
                      </p>
                      {paper.abstract && (
                        <p className="text-xs text-gray-500 mb-3 line-clamp-2">
                          {paper.abstract}
                        </p>
                      )}
                      <div className="flex gap-2">
                        {LABEL_OPTIONS.map((opt) => (
                          <button
                            key={opt.value}
                            onClick={() => setAnchorLabel(paper.id, opt.value)}
                            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                              anchorLabels[paper.id] === opt.value
                                ? opt.color
                                : "bg-white text-gray-500 border-gray-200 hover:bg-gray-50"
                            }`}
                          >
                            {opt.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex gap-3 mt-8">
                <button
                  onClick={() => setStep(2)}
                  className="flex-1 py-3 bg-gray-100 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={() => setStep(4)}
                  className="flex-1 py-3 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors"
                >
                  {anchorPapers.length === 0 ? "Skip" : "Continue"}
                </button>
              </div>
            </div>
          )}

          {/* ── Step 4: Pairwise ── */}
          {step === 4 && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-1">
                Which paper interests you more?
              </h2>
              <p className="text-sm text-gray-400 mb-6">
                Comparison {Math.min(currentPair + 1, pairwisePairs.length)} of{" "}
                {Math.max(pairwisePairs.length, 1)}
              </p>

              {pairwiseLoading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : currentPair >= pairwisePairs.length ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth={2}
                      className="w-8 h-8 text-green-600"
                    >
                      <polyline points="20,6 9,17 4,12" />
                    </svg>
                  </div>
                  <p className="text-lg font-semibold text-gray-900 mb-1">
                    {pairwisePairs.length > 0
                      ? "All done!"
                      : "No comparisons available"}
                  </p>
                  <p className="text-sm text-gray-400">
                    Click &quot;Finish setup&quot; to start using Research Radar.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {[
                    pairwisePairs[currentPair].paper_a,
                    pairwisePairs[currentPair].paper_b,
                  ].map((paper, idx) => {
                    const other =
                      idx === 0
                        ? pairwisePairs[currentPair].paper_b
                        : pairwisePairs[currentPair].paper_a;
                    return (
                      <button
                        key={paper.id}
                        onClick={() => choosePairwise(paper.id, other.id)}
                        className="text-left p-5 border-2 border-gray-100 rounded-2xl hover:border-blue-400 hover:bg-blue-50 transition-all group"
                      >
                        <p className="font-medium text-gray-900 text-sm mb-2 group-hover:text-blue-700 transition-colors">
                          {paper.title}
                        </p>
                        {paper.abstract && (
                          <p className="text-xs text-gray-500 line-clamp-4">
                            {paper.abstract}
                          </p>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}

              <div className="flex gap-3 mt-8">
                <button
                  onClick={() => setStep(3)}
                  className="flex-1 py-3 bg-gray-100 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={handleComplete}
                  disabled={loading}
                  className="flex-1 py-3 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {loading ? "Setting up…" : "Finish setup →"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
