export interface NewsArticle {
    id: string;
    title: string;
    description: string;
    body: string;
    author: string | null;
    image_url: string | null;
    date_published: string;
    date_edited: string | null;
}

export const mockNews: NewsArticle[] = [
    {
        id: "1",
        title: "Senate Passes New Infrastructure Bill",
        description: "A comprehensive infrastructure bill was passed today with bipartisan support.",
        body: "A comprehensive infrastructure bill was passed today with bipartisan support. The legislation allocates funds for road repairs, bridge upgrades, and broadband expansion across rural communities. Senators from both parties praised the measure as a long-overdue investment in the nation's foundation.",
        author: "Jane Smith",
        image_url: "https://images.unsplash.com/photo-1523995462485-3d171b5c8fa9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=60",
        date_published: "2026-03-01T10:00:00Z",
        date_edited: null
    },
    {
        id: "2",
        title: "Committee Hearing on Technology Regulation",
        description: "Technology leaders testify before the commerce committee.",
        body: "Technology executives appeared before the Senate Commerce Committee to discuss proposed regulations on data privacy, algorithmic accountability, and content moderation. The hearing drew significant public interest as lawmakers pressed for greater transparency from major platforms.",
        author: "Carlos Rivera",
        image_url: null,
        date_published: "2026-02-28T14:30:00Z",
        date_edited: "2026-03-01T08:00:00Z"
    },
    {
        id: "3",
        title: "Economic Forum Highlights Job Growth",
        description: "Recent economic data shows stronger than expected job growth in key sectors.",
        body: "The annual Economic Forum released a report showing a 3.2% increase in employment across manufacturing, technology, and healthcare sectors. Economists attributed the growth to recent policy incentives and federal investment in workforce training programs.",
        author: "Maria Johnson",
        image_url: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=60",
        date_published: "2026-02-27T09:15:00Z",
        date_edited: null
    },
    {
        id: "4",
        title: "Healthcare Initiative Receives Funding",
        description: "New grants announced for rural healthcare facilities.",
        body: "The Department of Health announced $500 million in grants to expand access to primary care in underserved rural areas. The funding will support the construction of new clinics and the recruitment of medical professionals to regions facing doctor shortages.",
        author: "David Lee",
        image_url: "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=60",
        date_published: "2026-02-26T11:45:00Z",
        date_edited: null
    },
    {
        id: "5",
        title: "Education Reform Debate Continues",
        description: "Lawmakers debate the merits of proposed changes to standardized testing.",
        body: "A heated debate unfolded on the Senate floor over proposed changes to the national standardized testing framework. Proponents argue that current metrics fail to capture student potential, while opponents worry that eliminating benchmarks could reduce accountability in public schools.",
        author: "Sarah Chen",
        image_url: "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=60",
        date_published: "2026-02-25T16:20:00Z",
        date_edited: "2026-02-26T10:00:00Z"
    },
    {
        id: "6",
        title: "Environmental Protection Measures Announced",
        description: "New initiatives aimed at reducing carbon emissions were unveiled today.",
        body: "The Environmental Protection Agency unveiled a sweeping set of new regulations designed to cut carbon emissions from industrial sources by 40% over the next decade. The measures include stricter limits on factory emissions and incentives for companies that transition to clean energy.",
        author: "Tom Williams",
        image_url: null,
        date_published: "2026-02-24T13:00:00Z",
        date_edited: null
    }
];
