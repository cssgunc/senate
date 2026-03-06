export interface NewsArticle {
    id: string;
    title: string;
    description: string;
    content: string;
    image_url: string | null;
    date_published: string;
}

export const mockNews: NewsArticle[] = [
    {
        id: "1",
        title: "Senate Passes New Infrastructure Bill",
        description: "A comprehensive infrastructure bill was passed today with bipartisan support.",
        content: "Full content of the article...",
        image_url: "https://images.unsplash.com/photo-1523995462485-3d171b5c8fa9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=60",
        date_published: "2026-03-01T10:00:00Z"
    },
    {
        id: "2",
        title: "Committee Hearing on Technology Regulation",
        description: "Technology leaders testify before the commerce committee.",
        content: "Full content of the article...",
        image_url: null,
        date_published: "2026-02-28T14:30:00Z"
    },
    {
        id: "3",
        title: "Economic Forum Highlights Job Growth",
        description: "Recent economic data shows stronger than expected job growth in key sectors.",
        content: "Full content of the article...",
        image_url: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=60",
        date_published: "2026-02-27T09:15:00Z"
    },
    {
        id: "4",
        title: "Healthcare Initiative Receives Funding",
        description: "New grants announced for rural healthcare facilities.",
        content: "Full content of the article...",
        image_url: "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=60",
        date_published: "2026-02-26T11:45:00Z"
    },
    {
        id: "5",
        title: "Education Reform Debate Continues",
        description: "Lawmakers debate the merits of proposed changes to standardized testing.",
        content: "Full content of the article...",
        image_url: "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=60",
        date_published: "2026-02-25T16:20:00Z"
    },
    {
        id: "6",
        title: "Environmental Protection Measures Announced",
        description: "New initiatives aimed at reducing carbon emissions were unveiled today.",
        content: "Full content of the article...",
        image_url: null,
        date_published: "2026-02-24T13:00:00Z"
    }
];
