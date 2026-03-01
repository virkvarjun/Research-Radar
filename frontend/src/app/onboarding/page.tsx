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
  { id: "student", label: "Student", desc: "Surveys, tutorials, foundational papers" },
  { id: "builder", label: "Builder", desc: "Papers with code, practical applications" },
  { id: "lab", label: "Lab Researcher", desc: "Datasets, baselines, cutting-edge methods" },
];

const TOPICS = [
  "Machine Learning", "Natural Language Processing", "Computer Vision",
  "Robotics", "Reinforcement Learning", "Graph Neural Networks",
  "Generative Models", "Optimization", "Bayesian Methods",
  "Speech Recognition", "Multi-Agent Systems", "Bioinformatics",
];

const LABEL_OPTIONS = [
  { value: "interested", label: "Interested", color: "bg-blue-600 text-white" },
  { value: "neutral", label: "Neutral", color: "bg-gray-100 text-gray-700" },
  { value: "not_interested", label: "Not interested", color: "bg-red-50 text-red-600" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [role, setRole] = useState("");
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [customTopic, setCustomTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Step 3: Anchor papers
  const [anchorPapers, setAnchorPapers] = useState<Paper[]>([]);
  const [anchorLabels, setAnchorLabels] = useState<Record<string, string>>({});
  const [anchorLoading, setAnchorLoading] = useState(false);

  // Step 4: Pairwise
  const [pairwisePairs, setPairwisePairs] = useState<{ paper_a: Paper; paper_b: Paper }[]>([]);
  const [pairwiseChoices, setPairwiseChoices] = useState<{ winner_id: string; loser_id: string }[]>([]);
  const [currentPair, setCurrentPair] = useState(0);
  const [pairwiseLoading, setPairwiseLoading] = useState(false);

  const totalSteps = 4;

  function toggleTopic(topic: string) {
    setSelectedTopics((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]
    );
  }

  function addCustomTopic() {
    if (customTopic.trim() && !selectedTopics.includes(customTopic.trim())) {
      setSelectedTopics((prev) => [...prev, customTopic.trim()]);
      setCustomTopic("");
    }
  }

  // Load anchor papers when entering step 3
  useEffect(() => {
    if (step === 3 && anchorPapers.length === 0) {
      setAnchorLoading(true);
      getAnchorPapers()
        .then((papers) => setAnchorPapers(papers))
        .catch(() => setError("Could not load anchor papers. You can skip this step."))
        .finally(() => setAnchorLoading(false));
    }
  }, [step, anchorPapers.length]);

  // Load pairwise papers when entering step 4
  useEffect(() => {
    if (step === 4 && pairwisePairs.length === 0) {
      setPairwiseLoading(true);
      getPairwisePapers()
        .then((pairs) => setPairwisePairs(pairs))
        .catch(() => setError("Could not load comparison papers. You can skip this step."))
        .finally(() => setPairwiseLoading(false));
    }
  }, [step, pairwisePairs.length]);

  function setAnchorLabel(paperId: string, label: string) {
    setAnchorLabels((prev) => ({ ...prev, [paperId]: label }));
  }

  function choosePairwise(winnerId: string, loserId: string) {
    setPairwiseChoices((prev) => [...prev, { winner_id: winnerId, loser_id: loserId }]);
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
      // If backend is down, still let user proceed
      router.push("/feed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 w-full max-w-2xl">
        <h1 className="text-2xl font-bold text-blue-600 mb-1">Research Radar</h1>
        <p className="text-gray-500 text-sm mb-6">
          Step {step} of {totalSteps} — Let&apos;s personalize your feed
        </p>

        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-1.5 mb-6">
          <div
            className="bg-blue-600 h-1.5 rounded-full transition-all"
            style={{ width: `${(step / totalSteps) * 100}%` }}
          />
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">
            {error}
          </div>
        )}

        {/* ============ Step 1: Role Selection ============ */}
        {step === 1 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              What&apos;s your role?
            </h2>
            <div className="space-y-3">
              {ROLES.map((r) => (
                <button
                  key={r.id}
                  onClick={() => setRole(r.id)}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-colors ${
                    role === r.id
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <p className="font-medium text-gray-900">{r.label}</p>
                  <p className="text-sm text-gray-500">{r.desc}</p>
                </button>
              ))}
            </div>
            <button
              onClick={() => setStep(2)}
              disabled={!role}
              className="mt-6 w-full py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              Next
            </button>
          </div>
        )}

        {/* ============ Step 2: Topic Selection ============ */}
        {step === 2 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Select your research interests
            </h2>
            <div className="flex flex-wrap gap-2 mb-4">
              {TOPICS.map((topic) => (
                <button
                  key={topic}
                  onClick={() => toggleTopic(topic)}
                  className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                    selectedTopics.includes(topic)
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {topic}
                </button>
              ))}
            </div>
            <div className="flex gap-2 mb-6">
              <input
                type="text"
                value={customTopic}
                onChange={(e) => setCustomTopic(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addCustomTopic())}
                placeholder="Add custom topic..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={addCustomTopic}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md text-sm hover:bg-gray-200"
              >
                Add
              </button>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="flex-1 py-2 bg-gray-100 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-200"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                disabled={selectedTopics.length === 0}
                className="flex-1 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* ============ Step 3: Anchor Papers ============ */}
        {step === 3 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Rate these papers
            </h2>
            <p className="text-sm text-gray-500 mb-4">
              Tell us how interested you are in each paper. This helps calibrate your feed.
            </p>

            {anchorLoading ? (
              <p className="text-gray-500 text-center py-8">Loading papers...</p>
            ) : anchorPapers.length === 0 ? (
              <p className="text-gray-400 text-center py-8 text-sm">
                No anchor papers available yet. You can skip this step.
              </p>
            ) : (
              <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
                {anchorPapers.map((paper) => (
                  <div
                    key={paper.id}
                    className="border border-gray-200 rounded-lg p-3"
                  >
                    <p className="font-medium text-gray-900 text-sm mb-1">
                      {paper.title}
                    </p>
                    {paper.abstract && (
                      <p className="text-xs text-gray-500 mb-2 line-clamp-2">
                        {paper.abstract}
                      </p>
                    )}
                    <div className="flex gap-2">
                      {LABEL_OPTIONS.map((opt) => (
                        <button
                          key={opt.value}
                          onClick={() => setAnchorLabel(paper.id, opt.value)}
                          className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                            anchorLabels[paper.id] === opt.value
                              ? opt.color
                              : "bg-gray-50 text-gray-500 hover:bg-gray-100"
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

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setStep(2)}
                className="flex-1 py-2 bg-gray-100 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-200"
              >
                Back
              </button>
              <button
                onClick={() => setStep(4)}
                className="flex-1 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                {anchorPapers.length === 0 ? "Skip" : "Next"}
              </button>
            </div>
          </div>
        )}

        {/* ============ Step 4: Pairwise Comparison ============ */}
        {step === 4 && (
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Which paper interests you more?
            </h2>
            <p className="text-sm text-gray-500 mb-4">
              Pick the paper you&apos;d rather read — {currentPair + 1} of{" "}
              {Math.max(pairwisePairs.length, 1)}
            </p>

            {pairwiseLoading ? (
              <p className="text-gray-500 text-center py-8">Loading comparisons...</p>
            ) : currentPair >= pairwisePairs.length ? (
              <div className="text-center py-8">
                <p className="text-green-600 font-medium mb-2">
                  {pairwisePairs.length > 0
                    ? "All comparisons done!"
                    : "No comparison papers available."}
                </p>
                <p className="text-sm text-gray-400">
                  Click &quot;Complete Setup&quot; to finish.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {[pairwisePairs[currentPair].paper_a, pairwisePairs[currentPair].paper_b].map(
                  (paper, idx) => {
                    const other = idx === 0
                      ? pairwisePairs[currentPair].paper_b
                      : pairwisePairs[currentPair].paper_a;
                    return (
                      <button
                        key={paper.id}
                        onClick={() => choosePairwise(paper.id, other.id)}
                        className="text-left p-4 border-2 border-gray-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-colors"
                      >
                        <p className="font-medium text-gray-900 text-sm mb-1">
                          {paper.title}
                        </p>
                        {paper.abstract && (
                          <p className="text-xs text-gray-500 line-clamp-3">
                            {paper.abstract}
                          </p>
                        )}
                      </button>
                    );
                  }
                )}
              </div>
            )}

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setStep(3)}
                className="flex-1 py-2 bg-gray-100 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-200"
              >
                Back
              </button>
              <button
                onClick={handleComplete}
                disabled={loading}
                className="flex-1 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {loading ? "Setting up..." : "Complete Setup"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
