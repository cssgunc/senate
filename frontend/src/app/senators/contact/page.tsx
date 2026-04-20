"use client";

import {
  getDistricts,
  getLeadership,
  getSenators,
  submitContactForm,
} from "@/lib/api";
import { District, Leadership, Senator } from "@/types";
import { useEffect, useState } from "react";

export default function ContactPage() {
  const [senators, setSenators] = useState<Senator[]>([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [senatorId, setSenatorId] = useState<string>("");
  const [speakerMessage, setSpeakerMessage] = useState("");
  const [districts, setDistricts] = useState<District[]>([]);
  const [speaker, setSpeaker] = useState<Leadership | null>(null);

  const [isLoadingSenators, setIsLoadingSenators] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [senatorsData, districtsData, leadershipData] = await Promise.all(
          [getSenators(), getDistricts(), getLeadership()],
        );
        setSenators(senatorsData);
        setDistricts(districtsData);

        const currentSpeaker = leadershipData.find(
          (l) => l.is_current && l.title.toLowerCase().includes("speaker"),
        );
        if (currentSpeaker) {
          setSpeaker(currentSpeaker);
        }
      } catch (err) {
        console.error("Failed to load contact data", err);
      } finally {
        setIsLoadingSenators(false);
      }
    }
    loadData();
  }, []);

  const validateEmail = (e: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!name.trim()) {
      setError("Name is required.");
      return;
    }
    if (!email.trim() || !validateEmail(email)) {
      setError("A valid email address is required.");
      return;
    }
    if (!message.trim()) {
      setError("Message cannot be empty.");
      return;
    }
    if (message.length > 1000) {
      setError("Message cannot exceed 1000 characters.");
      return;
    }

    setIsSubmitting(true);

    try {
      await submitContactForm({
        name: name.trim(),
        email: email.trim(),
        message: message.trim(),
        ...(senatorId ? { senator_id: parseInt(senatorId, 10) } : {}),
      });
      setSuccess(true);
      setName("");
      setEmail("");
      setMessage("");
      setSenatorId("");
    } catch (err) {
      console.error(err);
      setError("Something went wrong. Please email speaker@unc.edu directly.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const getDistrictName = (id: number) => {
    const d = districts.find((d) => d.id === id);
    return d ? d.district_name : `District ${id}`;
  };

  const recipientOptions = senators
    .filter((senator) => senator.is_active)
    .map((senator) => {
      const district = getDistrictName(senator.district_id);
      return {
        id: senator.id,
        label: `${senator.first_name} ${senator.last_name} (${district})`,
      };
    })
    .sort((a, b) => a.label.localeCompare(b.label));

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Contact Your Senator</h1>
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
          Your message has been sent!
        </div>
      )}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label
            htmlFor="name"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Email <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label
            htmlFor="recipient"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Recipient (Optional)
          </label>
          {isLoadingSenators ? (
            <p className="text-sm text-gray-500">Loading senators...</p>
          ) : (
            <select
              id="recipient"
              value={senatorId}
              onChange={(e) => setSenatorId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">
                Speaker of the Senate
                {speaker
                  ? ` (${speaker.first_name} ${speaker.last_name})`
                  : ""}{" "}
                (Default General Contact)
              </option>
              {recipientOptions.map((senator) => (
                <option key={senator.id} value={senator.id.toString()}>
                  {senator.label}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label
            htmlFor="message"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Message <span className="text-red-500">*</span>
          </label>
          <textarea
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            required
            maxLength={1000}
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="text-sm text-gray-500 mt-1 flex justify-between">
            <span>Maximum 1000 characters.</span>
            <span>{message.length}/1000</span>
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed mx-auto block"
        >
          {isSubmitting ? "Sending..." : "Send Message"}
        </button>
      </form>

      <div className="mt-12 flex items-center text-gray-400">
        <div className="flex-1 border-t-2 border-dashed border-gray-300"></div>
        <div className="px-4 text-lg font-bold uppercase tracking-widest text-gray-500">
          OR
        </div>
        <div className="flex-1 border-t-2 border-dashed border-gray-300"></div>
      </div>

      <div className="mt-8 text-left bg-gray-50 p-6 rounded-lg border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Message to speaker@unc.edu
        </h2>

        <div className="space-y-4">
          <textarea
            value={speakerMessage}
            onChange={(e) => setSpeakerMessage(e.target.value)}
            placeholder="Type your message here..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={4}
          />
          <a
            href={`mailto:speaker@unc.edu?body=${encodeURIComponent(speakerMessage)}`}
            className="inline-flex w-full sm:w-auto items-center justify-center px-6 py-2 border border-transparent shadow-sm text-base font-bold rounded-full text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 mx-auto"
          >
            <svg
              className="mr-2 -ml-1 h-5 w-5 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
            Send Email
          </a>
        </div>
      </div>
    </div>
  );
}
