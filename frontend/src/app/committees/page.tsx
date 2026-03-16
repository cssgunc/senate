import Link from "next/link";
import {getCommittees} from "@/lib/api/committees";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter} from "@/components/ui/card";
import {Button} from "@/components/ui/button";

export default async function CommitteesPage() {
    const committees = await getCommittees();
    return (
        <div className="container mx-auto py-8">
            <h1 className="text-4xl font-bold mb-8">Committees</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {committees.map((committee) => (
                    <Card key={committee.id}>
                        <CardHeader>
                            <CardTitle>{committee.name}</CardTitle>
                            <CardDescription className="line-clamp-2">{committee.shortDescription}</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm font-medium text-muted-foreground">Chair: {committee.chair.name}</p>
                        </CardContent>
                        <CardFooter>
                            <Link href={`/committees/${committee.id}`} passHref>
                                <Button>Learn More</Button>
                            </Link>
                        </CardFooter>
                    </Card>
                ))}
            </div>
        </div>
    );
}