export const dynamic = "force-dynamic";

import { getLeadership } from "@/lib/api"
import { Leadership } from "@/types"

// unused since seems unnecessary with current api setup but was in important notes
// async function fetchAllLeadership(): Promise<Leader[]> {
//   // assumed some mock sessions here, if needed can just use a api call to get available ones
//   const sessions = Array.from({ length: 20 }, (_, i) => 100 + i)

//   const results = await Promise.all(
//     sessions.map(async (session) => await getLeadership(session))
//   )

//   return results.flat()
// }

function groupBySession(leaders: Leadership[]) {
  return leaders.reduce<Record<number, Leadership[]>>((acc, leader) => {
    if (!acc[leader.session_number]) {
      acc[leader.session_number] = []
    }
    acc[leader.session_number].push(leader)
    return acc
  }, {})
}

function formatSession(n: number) {
  const s = ["th", "st", "nd", "rd"]
  const v = n % 100
  return `${n}${s[(v - 20) % 10] || s[v] || s[0]} Session`
}

export default async function PreviousLeadershipPage() {
  // Look above for additional documentation
  // const leaders = await fetchAllLeadership()
  const leaders = await getLeadership()
  const grouped = groupBySession(leaders)

  // Sort sessions descending (most recent first)
  const sortedSessions = Object.keys(grouped)
    .map(Number)
    .sort((a, b) => b - a)

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="text-3xl font-bold mb-8">Previous Senate Leadership</h1>

      <div className="space-y-10">
        {sortedSessions.map((session) => (
          <div key={session}>
            <h2 className="text-xl font-semibold mb-4">
              {formatSession(session)}
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {grouped[session].map((leader) => (
                <div
                  key={leader.id}
                  className="border rounded-xl p-4 shadow-sm hover:shadow-md transition"
                >
                  <div className="text-base font-medium">
                    {leader.first_name} {leader.last_name}
                  </div>
                  <div className="text-sm text-gray-600">
                    {leader.title}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}