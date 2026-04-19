"use client";

import { useState, useEffect } from "react";
import { getSenators, submitContactForm, getDistricts, getLeadership } from "@/lib/api";
import { Senator, District, Leadership } from "@/types";

export default function ContactPage() {
  const [senators, setSenators] = useState<Senator[]>([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [senatorId, setSenatorId] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState("");
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
        const [senatorsData, districtsData, leadershipData] = await Promise.all([
          getSenators(),
          getDistricts(),
          getLeadership()
        ]);
        setSenators(senatorsData);
        setDistricts(districtsData);
        
        const currentSpeaker = leadershipData.find((l) => l.is_current && l.title.toLowerCase().includes("speaker"));
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
    return /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(e);
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
        ...(senatorId ? { senator_id: parseInt(senatorId, 10) } : {})
      });
      setSuccess(true);
      setName("");
      setEmail("");
      setMessage("");
      setSenatorId("");
      setSearchTerm("");
    } catch (err) {
      console.error(err);
      setError("Something went wrong. Please email speaker@unc.edu directly.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const getDistrictName = (id: number) => {
    const d = districts.find(d => d.id === id);
    return d ? d.district_name : `District ${id}`;
  };

  const filteredSenators = senators.filter((senator) => {
    const term = searchTerm.toLowerCase();
    const fullName = `${senator.first_name} ${senator.last_name}`.toLowerCase();
    const districtName = getDistrictName(senator.district_id).toLowerCase();
    return fullName.includes(term) || districtName.includes(term);
  });

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
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
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
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
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
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Recipient (Optional)
          </label>
          {isLoadingSenators ? (
            <p className="text-sm text-gray-500">Loading senators...</p>
          ) : (
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Search by name or district..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-400"
              />

              <div
                onClick={() => setSenatorId("")}
                className={`p-4 border rounded-md cursor-pointer transition-colors ${
                  senatorId === ""
                    ? "border-blue-500 bg-blue-50 ring-1 ring-blue-500"
                    : "border-gray-200 hover:border-blue-300 bg-white"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">Speaker of the Senate {speaker && `(${speaker.first_name} ${speaker.last_name})`}</h3>
                    <p className="text-sm text-gray-500 mt-1">Default General Contact</p>
                  </div>
                  {senatorId === "" && (
                    <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-64 overflow-y-auto p-1 -mx-1">
                {filteredSenators.length > 0 ? (
                  filteredSenators.map((senator) => (
                    <div
                      key={senator.id}
                      onClick={() => setSenatorId(senator.id.toString())}
                      className={`relative p-3 border rounded-md cursor-pointer transition-colors group ${
                        senatorId === senator.id.toString()
                          ? "border-blue-500 bg-blue-50 ring-1 ring-blue-500"
                          : "border-gray-200 hover:border-blue-300 bg-white"
                      }`}
                    >
                      <h4 className="font-medium text-sm text-gray-900 pr-6">
                        {senator.first_name} {senator.last_name}
                      </h4>
                      {senator.district_id && (
                        <p className="text-xs text-gray-500 mt-1 font-semibold">
                          {getDistrictName(senator.district_id)}
                        </p>
                      )}
                      
                      {senator.committees && senator.committees.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {senator.committees.map(c => (
                            <span key={c.committee_id} className="inline-block bg-blue-50 text-blue-700 border border-blue-200 text-[10px] px-2 py-0.5 rounded-full whitespace-nowrap">
                              {c.role && c.role !== "Member" ? `${c.role}, ` : ""}{c.committee_name}
                            </span>
                          ))}
                        </div>
                      )}

                      {senatorId === senator.id.toString() && (
                        <div className="absolute top-3 right-3 w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center">
                          <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-gray-500 col-span-full py-4 text-center border border-dashed rounded-md border-gray-300 bg-gray-50">
                    No senators found matching &quot;{searchTerm}&quot;
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

        <div>
          <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
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
        <div className="px-4 text-lg font-bold uppercase tracking-widest text-gray-500">OR</div>
        <div className="flex-1 border-t-2 border-dashed border-gray-300"></div>
      </div>

      <div className="mt-8 text-left bg-gray-50 p-6 rounded-lg border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Message to speaker@unc.edu</h2>

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
            <svg className="mr-2 -ml-1 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Send Email
          </a>
        </div>
      </div>
    </div>
  );
}
