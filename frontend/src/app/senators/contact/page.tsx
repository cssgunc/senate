"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getDistricts } from "@/lib/api";
import type { District, Senator } from "@/types";
import Image from "next/image";
import { useEffect, useMemo, useState } from "react";

const GENERAL_INQUIRY_EMAIL = "speaker@unc.edu";

function getSenatorFullName(senator: Senator): string {
  return `${senator.first_name} ${senator.last_name}`;
}

function buildMailtoHref(params: {
  name: string;
  email: string;
  message: string;
  selectedSenator: string;
}): string {
  const subject = "Undergraduate Senate General Inquiry";
  const lines = [
    `Name: ${params.name || "N/A"}`,
    `Email: ${params.email || "N/A"}`,
    `Senator: ${params.selectedSenator || "No senator selected"}`,
    "",
    "Message:",
    params.message || "(No message provided)",
  ];

  return `mailto:${GENERAL_INQUIRY_EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(lines.join("\n"))}`;
}

export default function ContactPage() {
  const [districts, setDistricts] = useState<District[]>([]);
  const [districtSearch, setDistrictSearch] = useState("");
  const [selectedDistrictId, setSelectedDistrictId] = useState<string>("");
  const [selectedSenator, setSelectedSenator] = useState<string>("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [isLoadingDistricts, setIsLoadingDistricts] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [showFormNotice, setShowFormNotice] = useState(false);

  useEffect(() => {
    async function loadDistricts() {
      try {
        const districtData = await getDistricts();
        setDistricts(districtData);
      } catch {
        setLoadError(
          "Unable to load district data right now. You can still send a general inquiry.",
        );
      } finally {
        setIsLoadingDistricts(false);
      }
    }

    loadDistricts();
  }, []);

  const filteredDistricts = useMemo(() => {
    const normalizedSearch = districtSearch.trim().toLowerCase();

    if (!normalizedSearch) {
      return districts;
    }

    return districts.filter((district) =>
      district.district_name.toLowerCase().includes(normalizedSearch),
    );
  }, [districtSearch, districts]);

  const selectedDistrict = useMemo(
    () =>
      districts.find(
        (district) => district.id.toString() === selectedDistrictId,
      ) ?? null,
    [districts, selectedDistrictId],
  );

  const matchedSenators = selectedDistrict?.senator ?? [];

  const mailtoHref = buildMailtoHref({
    name,
    email,
    message,
    selectedSenator,
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-12 space-y-8">
        <header className="max-w-3xl">
          <h1 className="text-4xl font-bold text-gray-900">
            Contact Your Senator
          </h1>
          <p className="mt-3 text-lg text-gray-600">
            Search for your district to find your senator and contact details.
            If you are not sure who to contact, send a general inquiry.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Find Your District</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label
                htmlFor="district-search"
                className="mb-2 block text-sm font-medium text-gray-700"
              >
                Search district name
              </label>
              <Input
                id="district-search"
                placeholder="Example: North Campus"
                value={districtSearch}
                onChange={(event) => setDistrictSearch(event.target.value)}
                disabled={isLoadingDistricts}
              />
            </div>

            <div>
              <label
                htmlFor="district-select"
                className="mb-2 block text-sm font-medium text-gray-700"
              >
                Select district
              </label>
              <Select
                value={selectedDistrictId}
                onValueChange={(value) => {
                  setSelectedDistrictId(value);
                  setSelectedSenator("");
                }}
                disabled={isLoadingDistricts || filteredDistricts.length === 0}
              >
                <SelectTrigger id="district-select">
                  <SelectValue
                    placeholder={
                      isLoadingDistricts
                        ? "Loading districts..."
                        : "Choose a district"
                    }
                  />
                </SelectTrigger>
                <SelectContent>
                  {filteredDistricts.map((district) => (
                    <SelectItem
                      key={district.id}
                      value={district.id.toString()}
                    >
                      {district.district_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {loadError ? (
              <p className="text-sm text-red-700">{loadError}</p>
            ) : null}
          </CardContent>
        </Card>

        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-gray-900">
            District Senator{matchedSenators.length === 1 ? "" : "s"}
          </h2>

          {selectedDistrictId === "" ? (
            <p className="text-gray-600">
              Select a district to view senator contact information.
            </p>
          ) : matchedSenators.length === 0 ? (
            <p className="text-gray-600">
              No active senator is currently assigned to this district.
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {matchedSenators.map((senator) => (
                <Card key={senator.id}>
                  <CardContent className="p-6">
                    <div className="flex gap-4">
                      <div className="relative h-20 w-20 overflow-hidden rounded-full bg-gray-100">
                        {senator.headshot_url ? (
                          <Image
                            src={senator.headshot_url}
                            alt={getSenatorFullName(senator)}
                            fill
                            className="object-cover"
                          />
                        ) : (
                          <div className="flex h-full w-full items-center justify-center text-xl font-semibold text-gray-500">
                            {senator.first_name[0]}
                            {senator.last_name[0]}
                          </div>
                        )}
                      </div>

                      <div className="space-y-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {getSenatorFullName(senator)}
                        </h3>
                        <p className="text-sm text-gray-600">
                          District: {selectedDistrict?.district_name}
                        </p>
                        <a
                          href={`mailto:${senator.email}`}
                          className="text-sm text-blue-700 hover:text-blue-900"
                        >
                          {senator.email}
                        </a>
                      </div>
                    </div>

                    <div className="mt-4">
                      <p className="text-sm font-medium text-gray-700">
                        Committees
                      </p>
                      {senator.committees.length === 0 ? (
                        <p className="mt-1 text-sm text-gray-600">
                          No active committee assignments listed.
                        </p>
                      ) : (
                        <div className="mt-2 flex flex-wrap gap-2">
                          {senator.committees.map((committee) => (
                            <span
                              key={committee.committee_id}
                              className="inline-flex items-center rounded-full border border-gray-300 bg-white px-3 py-1 text-xs text-gray-700"
                            >
                              {committee.committee_name}
                              {committee.role ? ` (${committee.role})` : ""}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </section>

        <Card>
          <CardHeader>
            <CardTitle>General Inquiry</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              The direct contact form endpoint is still being finalized. Use the
              fields below and open an email draft to {GENERAL_INQUIRY_EMAIL}.
            </p>

            <form
              className="mt-6 space-y-4"
              onSubmit={(event) => {
                event.preventDefault();
                setShowFormNotice(true);
                window.location.href = mailtoHref;
              }}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label
                    htmlFor="contact-name"
                    className="mb-2 block text-sm font-medium text-gray-700"
                  >
                    Name
                  </label>
                  <Input
                    id="contact-name"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    placeholder="Your full name"
                  />
                </div>

                <div>
                  <label
                    htmlFor="contact-email"
                    className="mb-2 block text-sm font-medium text-gray-700"
                  >
                    Email
                  </label>
                  <Input
                    id="contact-email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="you@unc.edu"
                  />
                </div>
              </div>

              <div>
                <label
                  htmlFor="contact-senator"
                  className="mb-2 block text-sm font-medium text-gray-700"
                >
                  Senator (optional)
                </label>
                <Select
                  value={selectedSenator || "__none"}
                  onValueChange={(value) =>
                    setSelectedSenator(value === "__none" ? "" : value)
                  }
                >
                  <SelectTrigger id="contact-senator">
                    <SelectValue placeholder="No specific senator selected" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__none">
                      No specific senator selected
                    </SelectItem>
                    {matchedSenators.map((senator) => {
                      const fullName = getSenatorFullName(senator);
                      return (
                        <SelectItem key={senator.id} value={fullName}>
                          {fullName}
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label
                  htmlFor="contact-message"
                  className="mb-2 block text-sm font-medium text-gray-700"
                >
                  Message
                </label>
                <textarea
                  id="contact-message"
                  className="min-h-32 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  value={message}
                  onChange={(event) => setMessage(event.target.value)}
                  placeholder="How can the Senate help?"
                />
              </div>

              <div className="flex flex-col gap-3 sm:flex-row">
                <Button type="submit">Open Email Draft</Button>
                <a
                  href={mailtoHref}
                  className="inline-flex h-9 items-center justify-center rounded-md border border-gray-300 px-4 text-sm font-medium text-gray-700 transition hover:bg-gray-100"
                >
                  Use Mailto Fallback
                </a>
              </div>

              {showFormNotice ? (
                <p className="text-sm text-amber-700">
                  Contact form API is coming soon. We opened your email client
                  as a temporary fallback.
                </p>
              ) : null}
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
