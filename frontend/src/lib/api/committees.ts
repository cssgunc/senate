import { fetchAPI } from "@/lib/api";

export type Member = {
  id: string;
  name: string;
  role: string;
  email: string;
};

export type Committee = {
  id: string;
  name: string;
  isActive: boolean;
  shortDescription: string;
  fullDescription: string;
  chair: {
    name: string;
    email: string;
  };
  members: Member[];
};

type CommitteeApiMember = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  committees?: Array<{
    role?: string;
  }>;
};

type CommitteeApiResponse = {
  id: number;
  name: string;
  description: string;
  chair_name: string;
  chair_email: string;
  is_active: boolean;
  members: CommitteeApiMember[];
};

function mapCommittee(apiCommittee: CommitteeApiResponse): Committee {
  return {
    id: String(apiCommittee.id),
    name: apiCommittee.name,
    isActive: apiCommittee.is_active,
    shortDescription: apiCommittee.description,
    fullDescription: apiCommittee.description,
    chair: {
      name: apiCommittee.chair_name,
      email: apiCommittee.chair_email,
    },
    members: apiCommittee.members.map((member) => ({
      id: String(member.id),
      name: `${member.first_name} ${member.last_name}`,
      role: member.committees?.[0]?.role ?? "Member",
      email: member.email,
    })),
  };
}

export async function getCommittees(): Promise<Committee[]> {
  const committees = await fetchAPI<CommitteeApiResponse[]>("/committees/");
  return committees
    .filter((committee) => committee.is_active)
    .map(mapCommittee);
}

export async function getCommitteeById(id: string): Promise<Committee | null> {
  const numericId = Number.parseInt(id, 10);
  if (!Number.isFinite(numericId)) {
    return null;
  }

  try {
    const committee = await fetchAPI<CommitteeApiResponse>(
      `/committees/${numericId}`,
    );
    return mapCommittee(committee);
  } catch {
    return null;
  }
}
