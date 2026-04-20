import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getLeadership } from "@/lib/api";
import { loadLeadershipForPage } from "@/lib/leadership";
import Image from "next/image";

export default async function LeadershipPage() {
  const leadership = await loadLeadershipForPage(() => getLeadership());

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Senate Leadership
          </h1>
          <p className="text-lg text-gray-600">
            Meet the current officers of the Undergraduate Senate
          </p>
        </div>

        {leadership.length === 0 ? (
          <div className="mx-auto mt-8 max-w-2xl rounded-lg border border-gray-200 bg-white p-8 text-center shadow-sm">
            <h2 className="text-2xl font-semibold text-gray-900">
              Leadership Information Unavailable
            </h2>
            <p className="mt-2 text-gray-600">
              We are unable to load current leadership data right now. Please
              check back soon.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {leadership.map((leader) => (
              <Card
                key={leader.id}
                className="overflow-hidden hover:shadow-lg transition-shadow"
              >
                <CardHeader className="pb-4">
                  <div className="flex justify-center mb-4">
                    <div className="relative w-32 h-32 rounded-full overflow-hidden bg-gray-200">
                      {leader.photo_url ? (
                        <Image
                          src={leader.photo_url}
                          alt={`${leader.first_name} ${leader.last_name}`}
                          fill
                          className="object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400 text-4xl font-bold">
                          {leader.first_name[0]}
                          {leader.last_name[0]}
                        </div>
                      )}
                    </div>
                  </div>
                  <CardTitle className="text-center text-xl">
                    {leader.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {leader.first_name} {leader.last_name}
                  </h3>
                  <a
                    href={`mailto:${leader.email}`}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    {leader.email}
                  </a>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
