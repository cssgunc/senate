export type Member = {
    id: string;
    name: string;
    role: string;
    email: string;
};

export type Committee = {
    id: string;
    name: string;
    shortDescription: string;
    fullDescription: string;
    chair: {
        name: string;
        email: string;
    };
    members: Member[]
};

const MOCK_COMMITTEES: Committee[] = [
    {
    id: "academic-affairs",
    name: "Academic Affairs",
    shortDescription: "Focuses on curriculum, graduation requirements, and academic policies.",
    fullDescription: "The Academic Affairs committee works closely with faculty to ensure that the student body's academic needs are met. This includes policy reviews, course evaluations, and grading systems.",
    chair: { name: "Jane Doe", email: "jane.doe@example.edu" },
    members: [
      { id: "1", name: "John Smith", role: "Vice Chair", email: "john@example.edu" },
      { id: "2", name: "Alice Johnson", role: "Member", email: "alice@example.edu" },
    ],
    },
];

export async function getCommittees(): Promise<Committee[]> {
    return MOCK_COMMITTEES;
}

export async function getCommitteeById(id: string): Promise<Committee | null> {
    const committee = MOCK_COMMITTEES.find(c => c.id === id);
    return committee || null;
}

