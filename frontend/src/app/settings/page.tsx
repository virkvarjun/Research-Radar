"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import {
  getSettings,
  updateSettings,
  searchInstitutions,
  type UserSettings,
  type Institution,
} from "@/lib/api";

const ROLES = [
  { id: "student", label: "Student", emoji: "🎓" },
  { id: "builder", label: "Builder", emoji: "🛠️" },
  { id: "lab", label: "Lab Researcher", emoji: "🔬" },
];

export default function SettingsPage() {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [instQuery, setInstQuery] = useState("");
  const [instResults, setInstResults] = useState<Institution[]>([]);

  useEffect(() => {
    getSettings()
      .then(setSettings)
      .catch(() => setSettings(null))
      .finally(() => setLoading(false));
  }, []);

  async function handleSave() {
    if (!settings) return;
    setSaving(true);
    try {
      await updateSettings({
        role: settings.role,
        topics: settings.topics,
        digest_enabled: settings.digest_enabled,
        institution_ids: settings.institutions.map((i) => i.id),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      /* ignore */
    } finally {
      setSaving(false);
    }
  }

  async function handleInstSearch() {
    if (!instQuery.trim()) return;
    try {
      const data = await searchInstitutions(instQuery);
      setInstResults(data.institutions);
    } catch {
      setInstResults([]);
    }
  }

  function addInstitution(inst: Institution) {
    if (!settings) return;
    if (settings.institutions.some((i) => i.id === inst.id)) return;
    setSettings({
      ...settings,
      institutions: [...settings.institutions, inst],
    });
    setInstResults([]);
    setInstQuery("");
  }

  function removeInstitution(instId: string) {
    if (!settings) return;
    setSettings({
      ...settings,
      institutions: settings.institutions.filter((i) => i.id !== instId),
    });
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-2xl mx-auto px-4 py-8">
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        </main>
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-2xl mx-auto px-4 py-8">
          <div className="text-center py-20">
            <div className="text-5xl mb-4">⚠️</div>
            <p className="text-lg font-medium text-gray-900 mb-2">
              Failed to load settings
            </p>
            <p className="text-sm text-gray-400">Is the backend running?</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-sm text-gray-400 mt-1">
            Manage your preferences and profile
          </p>
        </div>

        {/* Role */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5 mb-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">Role</h2>
          <div className="flex gap-2">
            {ROLES.map((r) => (
              <button
                key={r.id}
                onClick={() => setSettings({ ...settings, role: r.id })}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-1.5 ${
                  settings.role === r.id
                    ? "bg-blue-600 text-white shadow-sm"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                <span>{r.emoji}</span>
                {r.label}
              </button>
            ))}
          </div>
        </div>

        {/* Digest */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-gray-900">
                Daily Email Digest
              </h2>
              <p className="text-xs text-gray-400 mt-0.5">
                Receive up to 5 personalized papers daily
              </p>
            </div>
            <button
              onClick={() =>
                setSettings({
                  ...settings,
                  digest_enabled: !settings.digest_enabled,
                })
              }
              className={`relative w-12 h-6 rounded-full transition-colors ${
                settings.digest_enabled ? "bg-blue-600" : "bg-gray-300"
              }`}
            >
              <div
                className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${
                  settings.digest_enabled
                    ? "translate-x-6"
                    : "translate-x-0.5"
                }`}
              />
            </button>
          </div>
        </div>

        {/* Institutions */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5 mb-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">
            My Institutions
          </h2>
          {settings.institutions.length > 0 ? (
            <div className="space-y-2 mb-4">
              {settings.institutions.map((inst) => (
                <div
                  key={inst.id}
                  className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-xl"
                >
                  <span className="text-sm text-gray-700">{inst.name}</span>
                  <button
                    onClick={() => removeInstitution(inst.id)}
                    className="text-red-400 text-xs hover:text-red-600 transition-colors font-medium"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-400 mb-4">
              No institutions added yet.
            </p>
          )}
          <div className="flex gap-2">
            <input
              type="text"
              value={instQuery}
              onChange={(e) => setInstQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  handleInstSearch();
                }
              }}
              placeholder="Search institution…"
              className="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50"
            />
            <button
              onClick={handleInstSearch}
              className="px-4 py-2.5 bg-gray-100 text-gray-600 text-sm font-medium rounded-xl hover:bg-gray-200 transition-colors"
            >
              Search
            </button>
          </div>
          {instResults.length > 0 && (
            <div className="mt-2 space-y-1">
              {instResults.map((inst) => (
                <button
                  key={inst.id}
                  onClick={() => addInstitution(inst)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-blue-50 rounded-xl transition-colors"
                >
                  {inst.name}
                  {inst.country && (
                    <span className="text-gray-400 ml-1">({inst.country})</span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Save */}
        <button
          onClick={handleSave}
          disabled={saving}
          className={`w-full py-3 rounded-xl text-sm font-medium transition-all ${
            saved
              ? "bg-green-50 text-green-700 border border-green-200"
              : "bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 shadow-sm"
          }`}
        >
          {saving ? "Saving…" : saved ? "✓ Saved!" : "Save Settings"}
        </button>
      </main>
    </div>
  );
}
