"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { submitOnboarding } from "@/lib/api";

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

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [role, setRole] = useState("");
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [customTopic, setCustomTopic] = useState("");
  const [loading, setLoading] = useState(false);

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

  async function handleComplete() {
    setLoading(true);
    try {
      await submitOnboarding({
        role,
        topics: selectedTopics,
        anchor_labels: {},
        pairwise_choices: [],
      });
      router.push("/feed");
    } catch {
      // If API fails (e.g., no backend), still redirect
      router.push("/feed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 w-full max-w-lg">
        <h1 className="text-2xl font-bold text-blue-600 mb-1">Research Radar</h1>
        <p className="text-gray-500 text-sm mb-6">
          Step {step} of 2 — Let&apos;s personalize your feed
        </p>

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
                onClick={handleComplete}
                disabled={selectedTopics.length === 0 || loading}
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
