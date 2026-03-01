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
  { id: "student", label: "Student" },
  { id: "builder", label: "Builder" },
  { id: "lab", label: "Lab Researcher" },
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
      // ignore
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
        <main className="max-w-2xl mx-auto px-4 py-6">
          <p className="text-gray-500 text-center py-12">Loading...</p>
        </main>
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-2xl mx-auto px-4 py-6">
          <p className="text-red-500 text-center py-12">
            Failed to load settings. Is the backend running?
          </p>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>

        {/* Role Toggle */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">Role</h2>
          <div className="flex gap-2">
            {ROLES.map((r) => (
              <button
                key={r.id}
                onClick={() => setSettings({ ...settings, role: r.id })}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  settings.role === r.id
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        {/* Digest */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-gray-900">
                Daily Email Digest
              </h2>
              <p className="text-xs text-gray-500">
                Receive up to 5 papers daily
              </p>
            </div>
            <button
              onClick={() =>
                setSettings({
                  ...settings,
                  digest_enabled: !settings.digest_enabled,
                })
              }
              className={`w-12 h-6 rounded-full transition-colors ${
                settings.digest_enabled ? "bg-blue-600" : "bg-gray-300"
              }`}
            >
              <div
                className={`w-5 h-5 bg-white rounded-full shadow transform transition-transform ${
                  settings.digest_enabled ? "translate-x-6" : "translate-x-0.5"
                }`}
              />
            </button>
          </div>
        </div>

        {/* Institutions */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">
            My Institutions
          </h2>
          {settings.institutions.map((inst) => (
            <div
              key={inst.id}
              className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
            >
              <span className="text-sm text-gray-700">{inst.name}</span>
              <button
                onClick={() => removeInstitution(inst.id)}
                className="text-red-500 text-xs hover:underline"
              >
                Remove
              </button>
            </div>
          ))}
          <div className="flex gap-2 mt-3">
            <input
              type="text"
              value={instQuery}
              onChange={(e) => setInstQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleInstSearch())}
              placeholder="Search institution..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleInstSearch}
              className="px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded-md hover:bg-gray-200"
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
                  className="w-full text-left p-2 text-sm hover:bg-gray-50 rounded"
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

        <button
          onClick={handleSave}
          disabled={saving}
          className={`w-full py-2 rounded-md text-sm font-medium transition-colors ${
            saved
              ? "bg-green-100 text-green-700"
              : "bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
          }`}
        >
          {saving ? "Saving..." : saved ? "Saved!" : "Save Settings"}
        </button>
      </main>
    </div>
  );
}
